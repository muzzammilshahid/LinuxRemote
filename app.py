from flask import Flask, request
from flask import send_from_directory
from flask_restful import Api, Resource, reqparse

from brightness import BrightnessControl

brigtness_ctrl = BrightnessControl()


app = Flask(__name__)
api = Api(app)


class SetBrightness(Resource):
    def get(self, percent):
        brigtness_ctrl._set(int(percent))
        return "brightness changed"


api.add_resource(SetBrightness, '/api/brightnes/<percent>')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8520, debug=True)
