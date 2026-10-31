from functools import wraps
from flask import request, session
from config import app, db
from models import User, Note

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return {"error": "Unauthorized"}, 401
        return func(*args, **kwargs)
    return wrapper

@app.post("/signup")
def signup():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"error": "Username and password are required."}, 422
    if User.query.filter_by(username=username).first():
        return {"error": "Username already taken."}, 422

    user = User(username=username)
    user.password_hash = password
    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id
    return user.to_dict(), 201


@app.post("/login")
def login():
    data = request.get_json() or {}
    user = User.query.filter_by(username=data.get("username")).first()

    if user and user.authenticate(data.get("password", "")):
        session["user_id"] = user.id
        return user.to_dict(), 200
    return {"error": "Invalid username or password."}, 401


@app.delete("/logout")
def logout():
    session.pop("user_id", None)
    return {}, 204


@app.get("/check_session")
def check_session():
    user_id = session.get("user_id")
    user = db.session.get(User, user_id) if user_id else None
    if user:
        return user.to_dict(), 200
    return {"error": "Unauthorized"}, 401


@app.get("/notes")
@login_required
def get_notes():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    pagination = (
        Note.query.filter_by(user_id=session["user_id"])
        .order_by(Note.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    return {
        "notes": [n.to_dict() for n in pagination.items],
        "page": pagination.page,
        "per_page": per_page,
        "total": pagination.total,
        "pages": pagination.pages,
    }, 200


@app.post("/notes")
@login_required
def create_note():
    data = request.get_json() or {}
    try:
        note = Note(
            title=data.get("title"),
            content=data.get("content"),
            category=data.get("category", "general"),
            user_id=session["user_id"],
        )
    except ValueError as e:
        return {"error": str(e)}, 422

    db.session.add(note)
    db.session.commit()
    return note.to_dict(), 201


def find_my_note(note_id):
    return Note.query.filter_by(id=note_id, user_id=session["user_id"]).first()


@app.patch("/notes/<int:note_id>")
@login_required
def update_note(note_id):
    note = find_my_note(note_id)
    if not note:
        return {"error": "Note not found."}, 404

    data = request.get_json() or {}
    try:
        for field in ("title", "content", "category"):
            if field in data:
                setattr(note, field, data[field])
    except ValueError as e:
        return {"error": str(e)}, 422

    db.session.commit()
    return note.to_dict(), 200


@app.delete("/notes/<int:note_id>")
@login_required
def delete_note(note_id):
    note = find_my_note(note_id)
    if not note:
        return {"error": "Note not found."}, 404

    db.session.delete(note)
    db.session.commit()
    return {}, 204

if __name__ == "__main__":
    app.run(port=5555, debug=True)