from config import app, api
from flask_restful import Resource, reqparse
from models import User, Record
from flask import request, jsonify, send_file
from services.records import RecordService

user_parser = reqparse.RequestParser()
user_parser.add_argument('username', help='This field cannot be blank', required=True)


class UserRes(Resource):
    def post(self):
        username = user_parser.parse_args()['username']
        if not username:
            return "Username can't be blank", 400
        if User.get_by_username(username=username):
            return "User already exists", 400
        user = User(username=username)
        user.save_obj()
        return {"id": user.id, "token": user.access_token}, 201

    def get(self):
        return jsonify(
            [user.to_json() for user in User.get_all_users()]
        )


class RecordRes(Resource):
    def post(self):
        user_id, token = request.args.get('id', type=int), request.args.get('token', type=str)
        user = User.check_permission(id=user_id, token=token)
        if not user:
            return "Invalid token or user id", 403
        record = request.get_data()
        if not record:
            return "Not data in request", 400
        service = RecordService(binary_data=record, filepath=app.config['UPLOAD_FOLDER'])
        mp3 = service.convert()
        if not mp3:
            return "Load file with .wav extension", 400
        record = Record(uuid=mp3.uuid, user_id=user_id)
        record.save_obj()
        return request.host_url + api.url_for(RecordRes, id=record.id, user=user_id)

    def get(self):
        record_id, user_id = request.args.get('id', type=int), request.args.get('user', type=int)
        if record_id and user_id:
            mp3 = Record.get_user_record(record_id=record_id, user_id=user_id)
            if mp3:
                return send_file(mp3.fullpath, as_attachment=True)
            return "Record does not exists", 400
        return "Check parameters: id=?&user=?", 400


api.add_resource(UserRes, '/api/users')
api.add_resource(RecordRes, '/api/records')

if __name__ == '__main__':
    app.run()
