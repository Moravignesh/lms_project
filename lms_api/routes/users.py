from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..schemas import UserCreate, UserOut, LoginRequest, Token
from ..models import UserProfile
from ..auth import hash_password, verify_password, create_access_token
from ..deps import get_db

router = APIRouter()


@router.post("/register/", response_model=UserOut)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(UserProfile).filter(UserProfile.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = UserProfile(
        name=payload.name,
        email=payload.email,
        role=payload.role,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login/", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserProfile).filter(UserProfile.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(subject=user.email)
    return Token(access_token=token)


@router.post("/auth/register/", response_model=UserOut)
def auth_register(payload: UserCreate, db: Session = Depends(get_db)):
    return register_user(payload, db)


@router.post("/auth/login/", response_model=Token)
def auth_login(payload: LoginRequest, db: Session = Depends(get_db)):
    return login(payload, db)


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserProfile).filter(UserProfile.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}
