import sqlite3
from sqlite3 import Connection, Cursor
from typing import Literal
from pydantic import BaseModel
from datetime import datetime

LessonTypes = Literal[
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
    "geografia",
    "biznes i zarządzanie",
    "historia",
    "chemia",
    "podstawy informatyki",
    "inne",
]


class Data(BaseModel):
    id: int
    type: Literal["homework", "kartk", "sprawdz"]
    lesson: LessonTypes
    date: datetime
    comment: str
    state: Literal["work", "done"]


DB_PATH: str = "database.sqlite"


def init_db() -> None:
    """Initialize the database by creating 'users' and 'data' tables if they do not exist."""
    conn: Connection = sqlite3.connect(DB_PATH)
    cursor: Cursor = conn.cursor()

    # Create tables separately to avoid syntax issues
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            lesson TEXT NOT NULL,
            date TEXT NOT NULL,
            comment TEXT,
            state BOOLEAN NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """
    )

    conn.commit()
    conn.close()


def add_user(username: str, password: str) -> None:
    conn: Connection = sqlite3.connect(DB_PATH)
    cursor: Cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO users (username, password) VALUES (?, ?)""", (username, password)
    )

    conn.commit()
    conn.close()


def add_something(data: Data, user_id: int) -> None:
    conn: Connection = sqlite3.connect(DB_PATH)
    cursor: Cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO data (type, lesson, date, comment, state, user_id) VALUES (?, ?, ?, ?, ?, ?)""",
        (data.type, data.lesson, data.date, data.comment, data.state, user_id),
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    add_user("skibidi", "toilet")
    add_something({"type": "homework", "lesson": "niemiecki", "date": datetime.date()})
