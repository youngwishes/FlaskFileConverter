import pathlib
from typing import Any
from config import db
import uuid
from sqlalchemy.orm import relationship
from services.records import MP3
from config import UPLOAD_FOLDER


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column('access_token', db.String, default=lambda: str(uuid.uuid4()), unique=True)
    username = db.Column(db.String, nullable=False, unique=True)
    records = relationship('Record', backref="user", lazy="joined", cascade="all, delete-orphan")

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


class Record(db.Model):
    __tablename__ = "record"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, uuid: str, user_id: int) -> None:
        self.uuid = uuid
        self.user_id = user_id

    @classmethod
    def get_user_record(cls, user_id: int, record_id: int) -> Any:
        uuid = db.session.query(Record.uuid).filter(Record.id == record_id, Record.user_id == user_id).scalar()
        if uuid:
            return MP3(mp3_fullpath=pathlib.Path(UPLOAD_FOLDER).joinpath(uuid))

    def save_obj(self):
        db.session.add(self)
        db.session.commit()
