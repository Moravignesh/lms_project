from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import requests
from datetime import datetime
from ..deps import get_db
from ..models import UserProfile, SocialAccount
from ..auth import create_access_token, hash_password

router = APIRouter()


@router.post("/auth/github/callback")
def github_callback(access_token: str, db: Session = Depends(get_db)):
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/vnd.github+json"}
    r = requests.get("https://api.github.com/user", headers=headers, timeout=10)
    if r.status_code != 200:
        raise HTTPException(status_code=400, detail="Invalid access_token")
    data = r.json()
    gid = str(data.get("id"))
    name = data.get("name") or data.get("login") or "github_user"
    email = data.get("email")
    if not email:
        r2 = requests.get("https://api.github.com/user/emails", headers=headers, timeout=10)
        if r2.status_code == 200:
            emails = r2.json()
            primary = next((e["email"] for e in emails if e.get("primary")), None)
            email = primary or next((e["email"] for e in emails if e.get("verified")), None)
    if not gid:
        raise HTTPException(status_code=400, detail="Missing user info")
    if not email:
        email = f"{name}@github.local"
    user = db.query(UserProfile).filter(UserProfile.email == email).first()
    if not user:
        user = UserProfile(name=name, email=email, role="student", password_hash=hash_password("oauth-login"))
        db.add(user)
        db.commit()
        db.refresh(user)
    sa = db.query(SocialAccount).filter(SocialAccount.provider == "github", SocialAccount.provider_user_id == gid, SocialAccount.user_id == user.id).first()
    if not sa:
        sa = SocialAccount(user_id=user.id, provider="github", provider_user_id=gid, created_at=datetime.utcnow())
        db.add(sa)
        db.commit()
    token = create_access_token(subject=user.email)
    return {"access_token": token, "token_type": "bearer"}
