from fastapi import APIRouter, status,HTTPException,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ... import database,models,oauth2
from . import schemas


router=APIRouter(prefix="/menu",tags=["Menu"])

@router.get("/{resid}",response_model=list[schemas.menuOut])
async def get_restaurant_menu(resid:str,user:models.Users=Depends(oauth2.get_current_user),db:AsyncSession=Depends(database.get_db)):
    res=await db.execute(select(models.Menu).where(models.Menu.res_id==resid))
    res=res.scalars().all()
    if(not res):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No Menu Found!")
    return res

@router.post("/add",status_code=status.HTTP_201_CREATED,response_model=schemas.menuOut)
async def add_to_menu(menu:schemas.menuCreate,user:models.Users=Depends(oauth2.get_current_user),db:AsyncSession=Depends(database.get_db)):
    res=await db.execute(select(models.Restaurants).where(models.Restaurants.res_id==menu.res_id))
    res=res.scalar_one()
    if(not res):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No Restaurants Found!")
    new_menu=models.Menu(**menu.model_dump(),restaurant=res.restaurant_name)
    db.add(new_menu)
    await db.commit()
    await db.refresh(new_menu)
    return new_menu