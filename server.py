from typing import Literal, Optional, TypedDict, cast
from fastapi.responses import FileResponse
from datetime import datetime, timedelta

from db_stuff import ElementData, Database, InvalidCredentialsError

from fastapi import FastAPI, Request, Response, Cookie, HTTPException, status


class LoginCredentials(TypedDict):
    username: str
    password: str


class StateChange(TypedDict):
    state: Literal["work", "done"]
    id: int


db: Database = Database("database.sqlite")


def sort_by_date(data: list[ElementData]) -> list[ElementData]:
    return sorted(data, key=lambda x: x["date"])


def sort_by_state(
    data: list[ElementData],
) -> tuple[list[ElementData], list[ElementData]]:
    """
    returns (done_data, work_data)
    """
    done_data: list[ElementData] = []
    work_data: list[ElementData] = []
    for element in data:
        if element["state"] == "done":
            work_data.append(element)
        else:
            done_data.append(element)
    return work_data, done_data


def sort_by_type(data: list[ElementData]) -> list[ElementData]:
    sorted_data: list[ElementData] = []
    same_day: dict[str, list[ElementData]] = {}
    for element in data:
        if element["date"] in same_day:
            same_day[element["date"]].append(element)
        else:
            same_day[element["date"]] = [element]

    for key in same_day.keys():
        if len(same_day[key]) < 2:
            sorted_data.append(same_day[key][0])
            continue

        sprawdz: list[ElementData] = []
        kartk: list[ElementData] = []
        homework: list[ElementData] = []
        for element in same_day[key]:
            if element["type"] == "sprawdz":
                sprawdz.append(element)
            elif element["type"] == "kartk":
                kartk.append(element)
            else:
                homework.append(element)

        sorted_data.extend(sprawdz)
        sorted_data.extend(kartk)
        sorted_data.extend(homework)

    return sorted_data


def check_three_days(data: list[ElementData]) -> bool:
    """returns true if there is any element in next three days, else returns False"""
    now: datetime = datetime.now()
    limit: datetime = now + timedelta(days=3)

    for element in data:
        dt: datetime = datetime.strptime(element["date"], "%Y-%m-%d")
        if now <= dt <= limit:
            return True
    return False


def if_thre_days_sort_diffrent(data: list[ElementData]):
    if check_three_days(data):
        return data

    homeworks: list[ElementData] = []
    others: list[ElementData] = []
    for element in data:
        if element["type"] == "homework":
            homeworks.append(element)
        else:
            others.append(element)

    return homeworks + others


def get_sorted_data(token: str) -> list[ElementData]:
    sorting: list[ElementData] = db.get_elements_from_token(token)
    sorting = sort_by_date(sorting)
    sorting = sort_by_type(sorting)
    done_data, work_data = sort_by_state(sorting)
    work_data = if_thre_days_sort_diffrent(work_data)
    sorted: list[ElementData] = work_data + done_data
    return sorted


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
def login(login_credentials: LoginCredentials, response: Response) -> dict[str, str]:
    """{"message": "Token set"}"""
    try:
        token: str = db.get_token_from_credentials(
            login_credentials["username"], login_credentials["password"]
        )
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials"
        )

    response.set_cookie(key="token", value=token, httponly=True, samesite="lax")
    return {"message": "Token set"}


@app.post("/logout")
def logout(response: Response) -> dict:
    response.set_cookie(key="token", value="", httponly=True, samesite="lax", expires=1)
    return {"message": "Token set"}


@app.get("/valid")
def check_token(token: Optional[str] = Cookie(None)) -> bool:
    return db.is_token_valid(token)


@app.get("/get_data")
def get_data(token: Optional[str] = Cookie(None)) -> list[ElementData]:
    if not db.is_token_valid(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        )

    cast_token: str = cast(str, token)
    return get_sorted_data(cast_token)


@app.post("/add_data")
def add_data(data: ElementData, token: Optional[str] = Cookie(None)) -> None:
    if not db.is_token_valid(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        )
    cast_token: str = cast(str, token)
    db.add_element(data, cast_token)


@app.post("/change_state")
def change_state_endpoint(data: StateChange, token: Optional[str] = Cookie(None)):
    if not db.is_token_valid(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        )
    cast_token: str = cast(str, token)

    db.change_state_of_element(data["state"], data["id"], cast_token)


@app.delete("/delete_data")
def delete_data(id: int, token: Optional[str] = Cookie(None)) -> None:
    if not db.is_token_valid(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        )
    cast_token: str = cast(str, token)
    db.delete_element(cast_token, id)


@app.delete("/delete_account")
def delete_account(
    username: str, password: str, token: Optional[str] = Cookie(None)
) -> None:
    if (
        not db.is_token_valid(token)
        and db.get_token_from_credentials(username, password) != token
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token or credentials",
        )
    cast_token: str = cast(str, token)
    db.delete_user(cast_token)


# @app.post("/debug/add_user")
# def debug_add_user(username: str, password: str) -> None:
#     db.add_user(username, password)
#
#
# @app.get("/debug/get_token")
# def debug_get_token(token: Optional[str] = Cookie(None)) -> str:
#     return str(token)


def start():
    import uvicorn

    PORT: int = 3000

    uvicorn.run("server:app", host="0.0.0.0", port=PORT, reload=True)


def test():
    token = db.get_token_from_credentials("rys", "kowalski")
    data = get_sorted_data(token)
    for i in if_thre_days_sort_diffrent(data):
        print(i)


if __name__ == "__main__":
    start()
