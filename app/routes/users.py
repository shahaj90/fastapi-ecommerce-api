from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .. import models, database, auth

router = APIRouter()

# Pydantic model for a User


class UserCreate(BaseModel):
    username: str
    password: str

# Dependency to get a database session


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint to create a new user (UNPROTECTED)


@router.post("/users/", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.DBUser).filter(
        models.DBUser.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=400, detail="Username already registered")

    hashed_password = auth.get_password_hash(user.password)

    db_user = models.DBUser(username=user.username,
                            hashed_password=hashed_password)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": "User created successfully", "user_id": db_user.id}

# Endpoint to authenticate and return a JWT token (UNPROTECTED)


@router.post("/users/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. Retrieve the user from the database
    db_user = db.query(models.DBUser).filter(
        models.DBUser.username == form_data.username).first()

    # 2. Check if user exists and password is correct
    if not db_user or not auth.verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Create the JWT token
    access_token = auth.create_access_token(
        data={"sub": db_user.username}
    )

    # 4. Return the token
    return {"access_token": access_token, "token_type": "bearer"}
