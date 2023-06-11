import pathlib
import uuid
import pydub
from config import app, api, ALLOWED_FORMATS, UPLOAD_FOLDER
from flask_restful import Resource, reqparse
from models import User, Audio
from flask import request, send_from_directory, jsonify
import tempfile

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


@app.route('/api/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


class RecordRes(Resource):
    def post(self):
        user_id, token = request.args.get('id'), request.args.get('token')
        user = User.check_permission(id=user_id, token=token)
        if not user:
            return "Invalid token", 403
        record = request.get_data()
        if not record:
            return "Not data in request", 400
        filename = uuid.uuid4().hex  # TODO Сделать уникальное название файла
        filepath = pathlib.Path.joinpath(app.config['UPLOAD_FOLDER'], filename).with_suffix('.wav')
        with open(filepath.with_suffix('.wav'), 'wb') as f:
            f.write(record)
        print(filepath)
        sound = pydub.AudioSegment.from_wav(filepath)
        sound.export(filepath.with_suffix('.mp3'), format='wav')
        record = Audio(url=str(filepath.with_suffix('.mp3')), user_id=user_id)
        record.save_obj()

        return request.url  # TODO Сделать ссылку на скачивание


api.add_resource(UserRes, '/api/users')
api.add_resource(RecordRes, '/api/records')

if __name__ == '__main__':
    app.run()
