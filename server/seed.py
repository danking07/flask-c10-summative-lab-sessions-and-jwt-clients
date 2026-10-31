from faker import Faker
from config import app, db
from models import User, Note

fake = Faker()

with app.app_context():
    Note.query.delete()
    User.query.delete()

    for name in ("alice", "bob"):
        user = User(username=name)
        user.password_hash = "password123"
        db.session.add(user)
        db.session.flush()

        for _ in range(12):
            db.session.add(Note(
                title=fake.sentence(nb_words=4),
                content=fake.paragraph(),
                category=fake.random_element(["work", "personal", "ideas"]),
                user_id=user.id,
            ))

    db.session.commit()
    print("Seeded 2 users and 24 notes.")