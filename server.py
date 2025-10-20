from typing import Literal, Optional, TypedDict, cast
from fastapi.responses import FileResponse

from db_stuff import Data, add_user, add_something, change_state, get_things_from_token, get_token_from_credentials, delete_something, kys, is_valid_token 

from fastapi import FastAPI, Response, Cookie, HTTPException, status


class LoginCredentials(TypedDict):
    username: str
    password: str


class StateChange(TypedDict):
    state: Literal['work', 'done']
    id: int

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
def login(login_credentials: LoginCredentials, response: Response) -> dict:
    token: str = get_token_from_credentials(login_credentials["username"], login_credentials['password'])

    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        samesite="lax"
    )
    return {"message": "Token set"}

@app.post('/logout')
def logout(response: Response) -> dict:
    response.set_cookie(
        key='token',
        value='',
        httponly=True,
        samesite='lax',
        expires=1
    )
    return {"message": "Token set"}

@app.get('/valid')
def check_token(token: Optional[str] = Cookie(None)) -> bool:
    return is_valid_token(token)

@app.get('/get_data')
def get_data(token: Optional[str] = Cookie(None)) -> list[Data]:
    if not is_valid_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token"
        )
    
    cast_token: str = cast(str, token)
    return get_things_from_token(cast_token)

@app.post('/add_data')
def add_data(data: Data, token: Optional[str] = Cookie(None)) -> None:
    if not is_valid_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token"
        )
    cast_token: str = cast(str, token)
    add_something(data, cast_token)

@app.post('/change_state')
def change_state_endpoint(data: StateChange, token: Optional[str] = Cookie(None)):
    if not is_valid_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token"
        )
    cast_token: str = cast(str, token)
    
    change_state(data['state'], data['id'], cast_token)

@app.delete('/delete_data')
def delete_data(id: int, token: Optional[str] = Cookie(None)) -> None:
    if not is_valid_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token"
        )
    cast_token: str = cast(str, token)
    delete_something(cast_token, id)

@app.delete('/delete_account')
def delete_account(username: str, password: str, token: Optional[str] = Cookie(None)) -> None:
    if not is_valid_token(token) and get_token_from_credentials(username, password) != token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token or credentials"
        )
    cast_token: str = cast(str, token)
    kys(cast_token)


@app.post('/debug/add_user')
def debug_add_user(username: str, password: str) -> None:
    add_user(username, password)

@app.get('/debug/get_token')
def debug_get_token(token: Optional[str] = Cookie(None)) -> str:
    return str(token)

if __name__ == "__main__":
    import uvicorn

    PORT: int = 3000

    uvicorn.run('server:app', host="0.0.0.0", port=PORT, reload=True)
    
