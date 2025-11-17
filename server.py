from typing import Literal, Optional, TypedDict, cast
from fastapi.responses import FileResponse

from db_stuff import (
    Data,
    add_user,
    add_something,
    change_state,
    get_things_from_token,
    get_token_from_credentials,
    delete_something,
    kys,
    is_valid_token,
)

from fastapi import FastAPI, Request, Response, Cookie, HTTPException, status


class LoginCredentials(TypedDict):
    username: str
    password: str


class StateChange(TypedDict):
    state: Literal["work", "done"]
    id: int


def sort_by_date(data: list[Data]) -> list[Data]:
    return sorted(data, key=lambda x: x["date"])


def sort_by_state(data: list[Data]) -> list[Data]:
    done_data: list[Data] = []
    work_data: list[Data] = []
    for element in data:
        if element["state"] == "done":
            done_data.append(element)
        else:
            work_data.append(element)
    return work_data + done_data


def sort_kart_or_sprawdz(data: list[Data]) -> list[Data]:
    sorted_data: list[Data] = []
    same_day: dict[str, list[Data]] = {}
    for element in data:
        if element["date"] in same_day:
            same_day[element["date"]].append(element)
        else:
            same_day[element["date"]] = [element]

    for key in same_day.keys():
        if len(same_day[key]) < 2:
            sorted_data.append(same_day[key][0])
            continue

        sprawdz: list[Data] = []
        rest: list[Data] = []
        for element in same_day[key]:
            if element["type"] == "homework":
                sprawdz.append(element)
            else:
                rest.append(element)

        sorted_data.extend(rest + sprawdz)

    return sorted_data


def get_sorted_data(token: str) -> list[Data]:
    sorting: list[Data] = get_things_from_token(token)
    sorting = sort_by_date(sorting)
    sorting = sort_kart_or_sprawdz(sorting)
    sorting = sort_by_state(sorting)

    return sorting


app: FastAPI = FastAPI()


@app.middleware("http")
async def no_cache_middleware(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


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
    token: str = get_token_from_credentials(
        login_credentials["username"], login_credentials["password"]
    )

    response.set_cookie(key="token", value=token, httponly=True, samesite="lax")
    return {"message": "Token set"}


@app.post("/logout")
def logout(response: Response) -> dict:
    response.set_cookie(key="token", value="", httponly=True, samesite="lax", expires=1)
    return {"message": "Token set"}


@app.get("/valid")
def check_token(token: Optional[str] = Cookie(None)) -> bool:
    return is_valid_token(token)


@app.get("/get_data")
def get_data(token: Optional[str] = Cookie(None)) -> list[Data]:
    if not is_valid_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        )

    cast_token: str = cast(str, token)
    return get_sorted_data(cast_token)


@app.post("/add_data")
def add_data(data: Data, token: Optional[str] = Cookie(None)) -> None:
    if not is_valid_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        )
    cast_token: str = cast(str, token)
    add_something(data, cast_token)


@app.post("/change_state")
def change_state_endpoint(data: StateChange, token: Optional[str] = Cookie(None)):
    if not is_valid_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        )
    cast_token: str = cast(str, token)

    change_state(data["state"], data["id"], cast_token)


@app.delete("/delete_data")
def delete_data(id: int, token: Optional[str] = Cookie(None)) -> None:
    if not is_valid_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        )
    cast_token: str = cast(str, token)
    delete_something(cast_token, id)


@app.delete("/delete_account")
def delete_account(
    username: str, password: str, token: Optional[str] = Cookie(None)
) -> None:
    if (
        not is_valid_token(token)
        and get_token_from_credentials(username, password) != token
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token or credentials",
        )
    cast_token: str = cast(str, token)
    kys(cast_token)


@app.post("/debug/add_user")
def debug_add_user(username: str, password: str) -> None:
    add_user(username, password)


@app.get("/debug/get_token")
def debug_get_token(token: Optional[str] = Cookie(None)) -> str:
    return str(token)


def start():
    import uvicorn

    PORT: int = 3000

    uvicorn.run("server:app", host="0.0.0.0", port=PORT, reload=True)


def test():
    token = get_token_from_credentials("rys", "kowalski")
    data = get_things_from_token(token)

    for i in data:
        print(i)
    print("\n\n\n\n")
    for i in sort_kart_or_sprawdz(data):
        print(i)


if __name__ == "__main__":
    start()
