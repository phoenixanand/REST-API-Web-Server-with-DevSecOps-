from passlib.context import CryptContext

pwd_contect =  CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str):
    print(password)
    print(type(password))
    print(len(password))
    return pwd_contect.hash(password)

def verify(plain_password, hashed_password):
    return pwd_contect.verify(plain_password, hashed_password)