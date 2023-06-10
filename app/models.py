from typing import Any

from config import db
import uuid
from sqlalchemy.orm import relationship


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column('access_token', db.String, default=lambda: str(uuid.uuid4()), unique=True)
    username = db.Column(db.String, nullable=False, unique=True)
    music = relationship('Audio', backref="user", lazy="joined", cascade="all, delete-orphan")

    def __init__(self, username: str) -> None:
        self.username = username

    @classmethod
    def check_permission(self, id: int, token: str) -> Any:
        return db.session.query(User.access_token).filter(User.id == id, User.access_token == token).one_or_none()

    @classmethod
    def get_all_users(cls) -> list:
        return db.session.query(User).all()

    @classmethod
    def get_by_username(cls, username: str) -> bool:
        if db.session.query(User.id).filter_by(username=username).one_or_none():
            return True

    def save_obj(self) -> None:
        db.session.add(self)
        db.session.commit()

    def __repr__(self) -> str:
        pass

    def to_json(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Audio(db.Model):
    __tablename__ = "audio"

    id = db.Column(db.String, default=lambda: str(uuid.uuid4()), unique=True, primary_key=True)
    url = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, url: str, user_id: int) -> None:
        self.url = url
        self.user_id = user_id

    def save_obj(self):
        db.session.add(self)
        db.session.commit()
