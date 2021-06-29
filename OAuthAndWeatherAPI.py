from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import requests

# from pydantic import BaseModel
# from typing import Optional

db = {"johndoe": {
    "username": "johndoe",
    "fullName": "John Doe",
    "email": "johndoe@example.com",
    "hashed_password": "fakehashedsecret",
    "disabled": False,
}, "alice": {
    "username": "alice",
    "fullName": "Alice Wonderson",
    "email": "alice@example.com",
    "hashed_password": "fakehashedsecret2",
    "disabled": True,
},
}

oauthScheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()


class User:
    def __init__(self, userInfo):
        self.username = userInfo["username"]
        self.email = userInfo["email"]
        self.fullName = userInfo["fullName"]
        self.disabled = userInfo["disabled"]


@app.post("/checkUserInDatabase")
async def checkUserInDatabase(username: str):
    if username in db:
        return {"user": True}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials",
                        headers={"WWW-Authenticate": "Bearer"})


@app.get("/getCurrentActiveUsers")
async def getCurrentActiveUsers():
    for key in db:
        if not db[key]["disabled"]:
            return db[key]


@app.get("/getCurrentInActiveUsers")
async def getCurrentInActiveUsers():
    for key in db:
        if db[key]["disabled"]:
            return db[key]


@app.post("/authorizeUser")
async def login(formData: OAuth2PasswordRequestForm = Depends()):
    userInfo = db.get(formData.username)
    if not userInfo:
        raise HTTPException(status_code=400, detail="Incorrect username")
    if not formData.password == db[formData.username]["hashed_password"]:
        raise HTTPException(status_code=400, detail="Incorrect password")
    return {"access-token": userInfo["username"], "tokenType": "Bearer"}


@app.post("/weatherAPI")
def getWeatherByCityName(cityName: str):
    response = (requests.get(
        f"http://api.openweathermap.org/data/2.5/weather?q={cityName}&appid=407b094ecd5af022cd41fc7077c7ca53").json())
    return {"current weather": response['weather']}
