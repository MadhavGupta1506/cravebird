from passlib.context import CryptContext
pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

async def hash_password(password):
    return pwd_context.hash(password)

async def check_password(password,hash_password):
    return pwd_context.verify(password, hash_password)