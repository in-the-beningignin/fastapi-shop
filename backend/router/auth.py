from router import *
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from utils import verify, hash

router = APIRouter(tags=['Authentication'])

BASE_PATH = Path(__file__).resolve().parent.parent
print(BASE_PATH)
router = APIRouter(tags=['Authentication'])

path = f"{BASE_PATH}/templates"

path_static = f"{BASE_PATH}/static/"

templates = Jinja2Templates(directory=path)

@router.get("/login/")
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post('/auth/login/')
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
    print(user_credentials.username, user_credentials.password)
    user = db.query(User).filter(User.email==user_credentials.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Credentials"
        )
    if not verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Credentials"
        )
    access_tocken = oauth2.create_access_tocken(data={"user_id": user.id})

    return {"access_token":access_tocken, "token_type": "bearer"}


@router.get("/auth/me")
def get_login_user(
    request: Request,
    current_user = Depends(oauth2.get_current_user)):
    return {'message':'hello user'}

@router.post("/auth/register")
def register(
        *,
        db: Session = Depends(get_db),
        username: str,
        email: str,
        password: str,
        phone: str = None,
        image: str = None):
    
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken"
        )
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    
    hashed_password = hash(password)
    new_user = User(
        username=username,
        email=email,
        phone=phone,
        image=image,
        password=hashed_password
    )

    
    db.add(new_user)
    db.commit()

    
    access_token = oauth2.create_access_tocken(data={"user_id": new_user.id})
    return {"access_token": access_token, "token_type": "bearer"}