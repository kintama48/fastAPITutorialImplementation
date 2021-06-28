from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import requests
from pydantic import BaseModel
from typing import Optional


app = FastAPI()
db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

oauthScheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

async def getCurrentUser(token:str = Depends(oauthScheme)):
    userInfo = None
    if token in db:
        userInfo = db[token]
    if userInfo:
        return userInfo
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials", headers={"WWW-Authenticate":"Bearer"})

async def getCurrentActiveUser(currentUser: User = Depends(getCurrentUser)):
    if currentUser.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return currentUser

@app.post("/token")
async def login(formData: OAuth2PasswordRequestForm=Depends()):
    userInfo = db.get(formData.username)
    if not userInfo:
        raise HTTPException(status_code=400, detail="Incorrect username")
    if not formData.password == db[formData.username]["hashed_password"]:
        raise HTTPException(status_code=400, detail="Incorrect password")
    return {"access-token": userInfo["username"], "tokenType": "Bearer"}

@app.post("/")
def getWeatherByCityName(cityName: str):
    if login:
        response = (requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={cityName}&appid=407b094ecd5af022cd41fc7077c7ca53").json())
        return {"current weather": response['weather']}
    else:
        return {"error": "Please log in to access the weather API!"}
