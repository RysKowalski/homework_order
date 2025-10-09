from typing import Literal
import json
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI




DATA_FILE = Path("data.json")

app: FastAPI = FastAPI()


def write_data(data_list: list[Data]) -> None:
    """Write a list of Data objects to data.json, converting datetime to ISO strings."""
    serializable = [item.model_dump(mode="json") for item in data_list]
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)


def read_data() -> list[Data]:
    """Read data.json and convert ISO date strings back into Data objects."""
    if not DATA_FILE.exists():
        return []
    with DATA_FILE.open("r", encoding="utf-8") as f:
        raw_data = json.load(f)
    return [Data(**item) for item in raw_data]


data: list[Data] = read_data()


@app.get("/")
def index() -> FileResponse:
    return FileResponse("./frontend/index.html")


@app.get("/script.js")
def js() -> FileResponse:
    return FileResponse("./frontend/script.js")


@app.get("/style.css")
def style() -> FileResponse:
    return FileResponse("./frontend/style.css")


@app.get("/get_data")
def get_data() -> list[Data]:
    print(data)
    return data


@app.post("/add")
def add(new_thing: Data) -> None:
    data.append(new_thing)
    write_data(data)

@app.delete("/delete")
def delete(id: int) -> None:



if __name__ == "__main__":
    import uvicorn

    PORT: int = 3000

    uvicorn.run(app, host="127.0.0.1", port=PORT)
    # with open("./test.json", "r") as file:
#    print(json.load(file))
