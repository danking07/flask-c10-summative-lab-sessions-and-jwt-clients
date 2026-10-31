from flask import request, session
from config import app, db
from models import User, Note


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


if __name__ == "__main__":
    app.run(port=5555, debug=True)