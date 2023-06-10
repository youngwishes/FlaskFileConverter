from config import app, api
from flask_restful import Resource, reqparse

parser = reqparse.RequestParser()
parser.add_argument('username', help='This field cannot be blank', required=True)


class User(Resource):
    def post(self):
        data = parser.parse_args()
        return data


api.add_resource(User, '/api/users')

if __name__ == '__main__':
    app.run()
