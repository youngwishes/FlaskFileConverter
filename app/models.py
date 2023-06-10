from config import db
from sqlalchemy.dialects.postgresql import UUID
import uuid


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(UUID(as_uuid=True), default=uuid.uuid4)
    username = db.Column(db.Str, nullable=False, unique=True)

    def __init__(self, username: str) -> None:
        self.username = username

    @classmethod
    def create_new_user(cls, username: str):
        user = User(username=username)
        new_user = db.session.add(user)
        db.session.commit()
        print(new_user)

    def __repr__(self) -> str:
        pass

    def to_json(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
