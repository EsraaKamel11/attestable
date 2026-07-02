import sqlite3
from fastapi import FastAPI, HTTPException


def build_sor(users: list[dict]) -> FastAPI:
    """A synthetic system-of-record: in-memory SQLite behind a read-only JSON API.
    Not a real IAM/GRC system, it demonstrates the integration shape only."""
    db = sqlite3.connect(":memory:", check_same_thread=False)
    db.execute("CREATE TABLE access (user_id TEXT PRIMARY KEY, name TEXT, entitlements TEXT, approved TEXT)")
    db.executemany(
        "INSERT INTO access VALUES (:user_id, :name, :entitlements, :approved)",
        [{"user_id": u["user_id"], "name": u["name"], "entitlements": u["entitlements"], "approved": u["approved"]} for u in users],
    )
    db.commit()

    app = FastAPI()

    @app.get("/users/{uid}/access")
    def get_access(uid: str) -> dict:
        row = db.execute(
            "SELECT user_id, name, entitlements, approved FROM access WHERE user_id = ?", (uid,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail=f"no such user: {uid}")
        return {"user_id": row[0], "name": row[1], "entitlements": row[2], "approved": row[3]}

    return app
