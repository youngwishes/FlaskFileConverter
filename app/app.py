from config import app, api, ALLOWED_FORMATS, UPLOAD_FOLDER
from flask_restful import Resource, reqparse
from models import User, Record
from flask import request, send_from_directory, jsonify, url_for
from services.records import RecordService

user_parser = reqparse.RequestParser()
user_parser.add_argument('username', help='This field cannot be blank', required=True)


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.split('.')[-1].lower() in ALLOWED_FORMATS


class UserRes(Resource):
    def post(self):
        username = user_parser.parse_args()['username']
        if User.get_by_username(username=username):
            return "Пользователь с таким никнеймом уже существует", 400

        user = User(username=username)
        user.save_obj()
        user_data = user.to_json()
        user_data.pop('username')
        return user_data, 201

    def get(self):
        return jsonify(
            [user.to_json() for user in User.get_all_users()]
        )


class RecordRes(Resource):
    def post(self):
        user_id, token = request.args.get('id'), request.args.get('token')
        user = User.check_permission(id=user_id, token=token)
        if not user:
            return "Invalid token or user id", 403
        record = request.get_data()
        if not record:
            return "Not data in request", 400
        service = RecordService(binary_data=record, filepath=app.config['UPLOAD_FOLDER'])
        uuid = service.convert()
        record = Record(uuid=uuid, user_id=user_id)
        record.save_obj()

        return request.url

    def get(self):
        record_id, user_id = request.args.get('id'), request.args.get('user')
        if record_id and user_id:
            mp3uuid = Record.get_user_record(record_id=record_id, user_id=user_id)
            if mp3uuid:
                return send_from_directory(directory=app.config['UPLOAD_FOLDER'], path=mp3uuid)
            return "Такой аудиозаписи не существует", 400
        return "Не указаны параметры id и user", 400


api.add_resource(UserRes, '/api/users')
api.add_resource(RecordRes, '/api/records')

if __name__ == '__main__':
    app.run()
