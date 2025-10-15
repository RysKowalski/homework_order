from typing import Optional
from fastapi.responses import FileResponse

from db_stuff import Data, add_user, add_something, get_things_from_token, get_token_from_credentials, delete_something, kys, is_valid_token 

from fastapi import FastAPI, Response, Cookie, HTTPException, status


app: FastAPI = FastAPI()


@app.get("/")
def index() -> FileResponse:
    return FileResponse("./frontend/index.html")


@app.get("/script.js")
def js() -> FileResponse:
    return FileResponse("./frontend/script.js")


@app.get("/style.css")
def style() -> FileResponse:
    return FileResponse("./frontend/style.css")

@app.post("/login")
def login(username, password, response: Response) -> dict:
    token: str = get_token_from_credentials(username, password)

    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        samesite="lax"
    )
    return {"message": "Token set"}

@app.get('/valid')
def check_token(token: Optional[str] = Cookie(None)) -> bool:
    return is_valid_token(token)

@app.post('/debug/add_user')
def debug_add_user(username: str, password: str) -> None:
    add_user(username, password)

@app.get('/debug/get_token')
def debug_get_token(token: Optional[str] = Cookie(None)) -> str:
    return str(token)

if __name__ == "__main__":
    import uvicorn

    PORT: int = 3000

    uvicorn.run('server:app', host="127.0.0.1", port=PORT, reload=True)
    
