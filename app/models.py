from config import db


class User(db.Model):
    __tablename__ = 'user'

    def __repr__(self) -> str:
        pass

    def to_json(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
