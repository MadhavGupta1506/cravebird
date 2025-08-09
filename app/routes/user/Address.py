from fastapi import HTTPException, APIRouter, Depends,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ... import database, models, oauth2
from . import schemas

router = APIRouter(prefix="/address", tags=["Address"])

@router.post("/add", status_code=201, response_model=schemas.AddressOut)
async def add_address(address: schemas.AddressCreate,user:models.Users=Depends(oauth2.get_current_user), db: AsyncSession = Depends(database.get_db)):
    res=await db.execute(select(models.Users).where(models.Users.user_id==user.user_id))
    res=res.scalar_one()
    if not res:
        raise HTTPException(status_code=404, detail="No User Found!")
    new_address = models.Address(**address.model_dump(), user_id=user.user_id)
    db.add(new_address)
    await db.commit()
    await db.refresh(new_address)
    return new_address

@router.get("/all", response_model=list[schemas.AddressOut])
async def get_all_addresses(user:models.Users=Depends(oauth2.get_current_user), db: AsyncSession = Depends(database.get_db)):
    res=await db.execute(select(models.Address).where(models.Address.user_id==user.user_id))
    res=res.scalars().all()
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Addresses Found!")
    return res

@router.put("/update/{id}", response_model=schemas.AddressOut, status_code=status.HTTP_202_ACCEPTED)
async def update_address(id: int, address: schemas.AddressCreate,user:models.Users=Depends(oauth2.get_current_user), db: AsyncSession = Depends(database.get_db)):
    res= await db.execute(select(models.Address).where(models.Address.id==id))
    res=res.scalar_one()
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    
    user_res=await db.execute(select(models.Users).where(models.Address.user_id==user.user_id and models.Address.id==id))
    user_res=user_res.scalar_one()
    if not user_res:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this address")

    res.address_line1 = address.address_line1
    res.address_line2 = address.address_line2
    res.city = address.city
    res.state = address.state
    res.zip_code = address.zip_code
    res.country = address.country
    await db.commit()
    await db.refresh(res)
    return res

@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(id: int,user:models.Users=Depends(oauth2.get_current_user), db: AsyncSession = Depends(database.get_db)):
    res= await db.execute(select(models.Address).where(models.Address.id==id))
    res=res.scalar_one()
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    
    user_res=await db.execute(select(models.Users).where(models.Address.user_id==user.user_id and models.Address.id==id))
    user_res=user_res.scalar_one()
    if not user_res:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this address")

    await db.delete(synchronize_session=False)
    await db.commit()
    return