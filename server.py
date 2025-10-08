from typing import TypedDict, Literal
import json

from fastapi import FastAPI

t = [
    {
        "type": "homework",
        "lesson": "niemiecki",
        "date": "2025-10-09",
        "comment": "ish shaise skibidi toilet",
    },
    {
        "type": "kartk",
        "lesson": "angielski",
        "date": "2025-10-10",
        "comment": "Ja ish not spek po english",
    },
    {
        "type": "sprawdz",
        "lesson": "polski",
        "date": "2025-10-18",
        "comment": "Uważam, iż skibidi toilet jest najwybitniejszą animacją wirtualną w wielkich dziejach wielkiego królestwa Polskiego",
    },
]


class Data(TypedDict):
    type: Literal["homework", "kartk", "sprawdz"]
    lesson: Literal[
        "niemiecki",
        "angielski",
        "polski",
        "strony internetowe",
        "angielski zawodowy",
        "informatyka",
        "bhp",
        "biologia",
        "edb",
        "religia",
        "fizyka",
    ]
    date: int
    comment: str


app: FastAPI = FastAPI()


if __name__ == "__main__":
    #  import uvicorn

    #   PORT: int = 3000

    #    uvicorn.run(app, host="127.0.0.1", port=PORT)
    with open("./test.json", "r") as file:
        print(json.load(file))
