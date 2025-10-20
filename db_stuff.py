from os import curdir
import uuid
import sqlite3
from sqlite3 import Connection, Cursor, connect
from typing import Any, Literal, Optional, TypedDict
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


class Data(TypedDict):
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
            password TEXT NOT NULL,
            token TEXT NOT NULL
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
        """INSERT INTO users (username, password, token) VALUES (?, ?, ?)""",
        (username, password, str(uuid.uuid4())),
    )

    conn.commit()
    conn.close()


def get_user_id(token: str) -> int:
    conn: Connection = sqlite3.connect(DB_PATH)
    cursor: Cursor = conn.cursor()

    cursor.execute('SELECT id FROM users WHERE token = ?', (token,))

    user_id: int = cursor.fetchone()[0]
    conn.close()
    return user_id


def add_something(data: Data, token: str) -> None:
    conn: Connection = sqlite3.connect(DB_PATH)
    cursor: Cursor = conn.cursor()

    user_id: int = get_user_id(token)
    cursor.execute(
        """INSERT INTO data (type, lesson, date, comment, state, user_id) VALUES (?, ?, ?, ?, ?, ?)""",
        (
            data["type"],
            data["lesson"],
            data["date"],
            data["comment"],
            data["state"],
            user_id,
        ),
    )

    conn.commit()
    conn.close()

def change_state(state: Literal['work', 'done'], element_id: int, token: str) -> None:
    conn: Connection = sqlite3.connect(DB_PATH)
    cursor: Cursor = conn.cursor()

    cursor.execute("""
        UPDATE data 
        SET state = ?
        WHERE (id, user_id) = (?, ?)
        """, (state, element_id, get_user_id(token)))

    conn.commit()
    conn.close()

def get_things_from_token(token: str) -> list[Data]:
    conn: Connection = sqlite3.connect(DB_PATH)
    cursor: Cursor = conn.cursor()

    user_id: int = get_user_id(token)

    cursor.execute(
        """SELECT id, type, lesson, date, comment, state FROM data WHERE user_id = ?""",
        (user_id,),
    )

    rows: list[Any] = cursor.fetchall()

    conn.close()

    return_data: list[Data] = []

    for row in rows:
        return_data.append(
            {
                "id": row[0],
                "type": row[1],
                "lesson": row[2],
                "date": row[3],
                "comment": row[4],
                "state": row[5],
            }
        )
    return return_data


def get_token_from_credentials(username: str, password: str) -> str:
    conn: Connection = sqlite3.connect(DB_PATH)
    cursor: Cursor = conn.cursor()

    cursor.execute("SELECT token FROM users WHERE (username, password) = (?, ?)", (username, password))
    token: str = cursor.fetchone()[0]

    conn.close()
    return token

def delete_something(token: str, id: int) -> None:
    user_id: int = get_user_id(token)

    conn: Connection = sqlite3.connect(DB_PATH)
    cursor: Cursor = conn.cursor()

    cursor.execute('DELETE FROM data WHERE (id, user_id) = (?, ?)', (id, user_id))
    
    conn.commit()
    conn.close()

def kys(token: str) -> None: # !untested
    """delete_user untested"""
    conn: Connection = sqlite3.connect(DB_PATH)
    cursor: Cursor = conn.cursor()

    cursor.execute('DELETE FROM users WHERE token = ?', (token,))

    conn.commit()
    conn.close()

def is_valid_token(token: Optional[str]) -> bool:
    conn: Connection = sqlite3.connect(DB_PATH)
    cursor: Cursor = conn.cursor()

    cursor.execute('SELECT EXISTS(SELECT 1 FROM users WHERE token = ?)', (token,))
    exists: bool = cursor.fetchone()[0] == 1

    conn.close()
    return exists

if __name__ == "__main__":
    init_db()
