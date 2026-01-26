import os
import sqlite3
from sqlite3 import Connection, Cursor
from typing import Any, Literal

from db_stuff import Database, ElementData, LessonTypes, InvalidCredentialsError


class Utils:
    testDBPath: str = "test_db.sqlite"

    def delete_db(self) -> None:
        if self.check_file_exists(self.testDBPath):
            os.remove(self.testDBPath)

    def check_file_exists(self, path: str) -> bool:
        exists: bool = os.path.exists(path)
        return exists


TableStructure = list[tuple[int, str, str, int, Any, int]]

utils: Utils = Utils()


def test_database_create_file() -> None:
    utils.delete_db()
    db: Database = Database(utils.testDBPath)

    db.init_database()

    assert utils.check_file_exists(utils.testDBPath)

    utils.delete_db()


def test_database_initial_table_users_exists() -> None:
    utils.delete_db()
    db: Database = Database(utils.testDBPath)
    conn: Connection = sqlite3.connect(utils.testDBPath)
    cursor: Cursor = conn.cursor()

    db.init_database()
    cursor.execute(
        """
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='users';
        """
    )

    assert cursor.fetchone() is not None
    utils.delete_db()


def test_database_initial_table_data_exists() -> None:
    utils.delete_db()
    db: Database = Database(utils.testDBPath)
    conn: Connection = sqlite3.connect(utils.testDBPath)
    cursor: Cursor = conn.cursor()

    db.init_database()
    cursor.execute(
        """
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='data';
        """
    )

    assert cursor.fetchone() is not None
    utils.delete_db()


def test_database_initial_table_users_structure() -> None:
    utils.delete_db()
    db: Database = Database(utils.testDBPath)
    conn: Connection = sqlite3.connect(utils.testDBPath)
    cursor: Cursor = conn.cursor()
    correct_structure: TableStructure = [
        (0, "id", "INTEGER", 0, None, 1),
        (1, "username", "TEXT", 1, None, 0),
        (2, "password", "TEXT", 1, None, 0),
        (3, "token", "TEXT", 1, None, 0),
    ]

    db.init_database()
    cursor.execute(
        """
        PRAGMA table_info(users);
        """
    )
    table_structure: list = cursor.fetchall()

    assert table_structure == correct_structure
    utils.delete_db()


def test_database_initial_table_data_structure() -> None:
    utils.delete_db()
    db: Database = Database(utils.testDBPath)
    conn: Connection = sqlite3.connect(utils.testDBPath)
    cursor: Cursor = conn.cursor()
    correct_structure: TableStructure = [
        (0, "id", "INTEGER", 0, None, 1),
        (1, "type", "TEXT", 1, None, 0),
        (2, "lesson", "TEXT", 1, None, 0),
        (3, "date", "TEXT", 1, None, 0),
        (4, "comment", "TEXT", 0, None, 0),
        (5, "state", "BOOLEAN", 1, None, 0),
        (6, "user_id", "INTEGER", 1, None, 0),
    ]

    db.init_database()
    cursor.execute(
        """
        PRAGMA table_info(data);
        """
    )
    table_structure: list = cursor.fetchall()

    assert table_structure == correct_structure
    utils.delete_db()


def test_database_add_user_creates_user() -> None:
    utils.delete_db()
    db: Database = Database(utils.testDBPath)
    db.init_database()
    conn: Connection = sqlite3.connect(utils.testDBPath)
    cursor: Cursor = conn.cursor()

    db.add_user("rys", "kowalski")
    cursor.execute("SELECT * FROM users")
    row = cursor.fetchone()

    assert row is not None
    utils.delete_db()


def test_database_add_user_correct_data() -> None:
    utils.delete_db()
    db: Database = Database(utils.testDBPath)
    db.init_database()
    conn: Connection = sqlite3.connect(utils.testDBPath)
    cursor: Cursor = conn.cursor()

    correct_id: int = 1
    correct_username: str = "rys"
    correct_password: str = "kowalski"
    correct_data_witchout_token: list[tuple[int, str, str]] = [
        (correct_id, correct_username, correct_password)
    ]

    db.add_user(correct_username, correct_password)
    cursor.execute("SELECT id, username, password FROM users")
    row = cursor.fetchall()
    cursor.execute("SELECT token FROM users WHERE username=?", (correct_username,))
    token = cursor.fetchone()[0]

    assert row == correct_data_witchout_token
    assert type(token) is str
    utils.delete_db()


def test_database_add_element() -> None:
    # prep
    utils.delete_db()
    db: Database = Database(utils.testDBPath)
    db.init_database()
    conn: Connection = sqlite3.connect(utils.testDBPath)
    cursor: Cursor = conn.cursor()

    correctID: int = 1
    correctType: Literal["homework", "kartk", "sprawdz"] = "homework"
    correctLesson: LessonTypes = "biznes i zarządzanie"
    correctDate: str = "1232-12-31"
    correctComment: str = "komentarz wspierający dużo znaków \n🙂😷🤖🩰🛀🏿👨🏻‍🦼‍➡️🩻♚"
    correctState: Literal["work", "done"] = "work"
    correctData: ElementData = {
        "id": correctID,
        "type": correctType,
        "lesson": correctLesson,
        "date": correctDate,
        "comment": correctComment,
        "state": correctState,
    }

    db.add_user("username", "password")
    token: str = db.get_token_from_credentials("username", "password")
    correctUserID: int = db.get_user_id(token)

    # test
    db.add_element(correctData, token)
    cursor.execute("SELECT * FROM data")
    rows: list = cursor.fetchall()

    # assertions
    assert rows == [
        (
            correctID,
            correctType,
            correctLesson,
            correctDate,
            correctComment,
            correctState,
            correctUserID,
        )
    ]
    utils.delete_db()


def test_database_get_user_id_correct_type() -> None:
    utils.delete_db()
    db: Database = Database(utils.testDBPath)
    db.init_database()
    db.add_user("username", "password")
    token: str = db.get_token_from_credentials("username", "password")

    userID = db.get_user_id(token)

    assert type(userID) is int
    utils.delete_db()


def test_database_get_token_from_credentials_correct_type() -> None:
    utils.delete_db()
    db: Database = Database(utils.testDBPath)
    db.init_database()
    username: str = "username"
    password: str = "password"
    db.add_user(username, password)

    token = db.get_token_from_credentials(username, password)

    assert type(token) is str
    utils.delete_db()


def test_database_get_token_from_credentials_throws_error() -> None:
    utils.delete_db()
    db: Database = Database(utils.testDBPath)
    db.init_database()

    gotError: bool = False
    try:
        db.get_token_from_credentials("non-existent username", "password")
    except InvalidCredentialsError:
        gotError = True

    assert gotError
    utils.delete_db()


def test_database_get_elements_from_token() -> None:
    utils.delete_db()
    db: Database = Database(utils.testDBPath)
    db.init_database()
    username: str = "username"
    password: str = "password"
    db.add_user(username, password)
    token: str = db.get_token_from_credentials(username, password)
    firstElement: ElementData = {
        "id": 1,
        "lesson": "biznes i zarządzanie",
        "state": "done",
        "date": "1232-12-31",
        "type": "homework",
        "comment": "epic comment",
    }
    secoundElement: ElementData = {
        "id": 2,
        "lesson": "angielski",
        "state": "work",
        "date": "2026-15-16",
        "type": "kartk",
        "comment": "epickier comment",
    }
    db.add_element(firstElement, token)
    db.add_element(secoundElement, token)
    correctData: list[ElementData] = [
        {
            "id": 1,
            "lesson": "biznes i zarządzanie",
            "state": "done",
            "date": "1232-12-31",
            "type": "homework",
            "comment": "epic comment",
        },
        {
            "id": 2,
            "lesson": "angielski",
            "state": "work",
            "date": "2026-15-16",
            "type": "kartk",
            "comment": "epickier comment",
        },
    ]

    data: list[ElementData] = db.get_elements_from_token(token)

    assert data == correctData
    utils.delete_db()


def test_database_change_state_of_element() -> None:
    utils.delete_db()
    db: Database = Database(utils.testDBPath)
    db.init_database()
    db.add_user("username", "password")
    token: str = db.get_token_from_credentials("username", "password")
    startState: Literal["work", "done"] = "work"
    db.add_element(
        {
            "id": 1,
            "lesson": "biznes i zarządzanie",
            "state": startState,
            "date": "1232-12-31",
            "type": "homework",
            "comment": "epic comment",
        },
        token,
    )
    elementID: int = db.get_elements_from_token(token)[0]["id"]
    correctState: Literal["work", "done"] = "done"

    db.change_state_of_element(correctState, elementID, token)
    state: Literal["work", "done"] = db.get_elements_from_token(token)[0]["state"]

    assert state == correctState
    utils.delete_db()


def test_database_delete_element() -> None:
    utils.delete_db()
    db: Database = Database(utils.testDBPath)
    db.init_database()
    db.add_user("username", "password")
    token: str = db.get_token_from_credentials("username", "password")
    element: ElementData = {
        "id": 1,
        "lesson": "biznes i zarządzanie",
        "state": "done",
        "date": "1232-12-31",
        "type": "homework",
        "comment": "epic comment",
    }
    db.add_element(element, token)
    elementID: int = db.get_elements_from_token(token)[0]["id"]

    db.delete_element(token, elementID)

    elements: list[ElementData] = db.get_elements_from_token(token)
    assert len(elements) == 0
    utils.delete_db()


def test_database_delete_user() -> None:
    utils.delete_db()
    db: Database = Database(utils.testDBPath)
    db.init_database()
    db.add_user("username", "password")
    token: str = db.get_token_from_credentials("username", "password")

    db.delete_user(token)

    userDeleted: bool = False
    try:
        db.get_token_from_credentials("username", "password")
    except InvalidCredentialsError:
        userDeleted = True
    assert userDeleted
    utils.delete_db()


def test_database_is_token_valid() -> None:
    utils.delete_db()
    db: Database = Database(utils.testDBPath)
    db.init_database()
    db.add_user("username", "password")
    validToken: str = db.get_token_from_credentials("username", "password")
    invalidToken: str = "invalid token"

    assert db.is_token_valid(validToken)
    assert not db.is_token_valid(invalidToken)
    utils.delete_db()
