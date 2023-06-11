import pathlib
from config import app, api, ALLOWED_FORMATS, UPLOAD_FOLDER
from flask_restful import Resource, reqparse
from models import User, Record
from flask import request, jsonify, send_file
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
        user_id, token = request.args.get('id', type=int), request.args.get('token')
        user = User.check_permission(id=user_id, token=token)
        if not user:
            return "Invalid token or user id", 403
        record = request.get_data()
        if not record:
            return "Not data in request", 400
        service = RecordService(binary_data=record, filepath=app.config['UPLOAD_FOLDER'])
        uuid = service.convert()
        if not uuid:
            return "Load file with .wav extension"
        record = Record(uuid=uuid, user_id=user_id)
        record.save_obj()
        return request.host_url + api.url_for(RecordRes, id=record.id, user=user_id)

    def get(self):
        record_id, user_id = request.args.get('id', type=int), request.args.get('user', type=int)
        if record_id and user_id:
            mp3uuid = Record.get_user_record(record_id=record_id, user_id=user_id)
            filepath = pathlib.Path.joinpath(app.config['UPLOAD_FOLDER'], mp3uuid)
            if mp3uuid:
                return send_file(filepath, as_attachment=True)
            return "Record does not exists", 400
        return "Check parameters: id=?&user=?", 400


api.add_resource(UserRes, '/api/users')
api.add_resource(RecordRes, '/api/records')

if __name__ == '__main__':
    app.run()
