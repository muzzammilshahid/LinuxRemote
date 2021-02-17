from flask import Flask, request
from flask import send_from_directory
from flask_restful import Api, Resource, reqparse

from brightness import BrightnessControl

brightness_ctrl = BrightnessControl()


app = Flask(__name__)
api = Api(app)


class SetBrightness(Resource):
    def get(self):
        brightness_percent = int((brightness_ctrl.brightness_current / brightness_ctrl.max_brightness) * 100)
        return brightness_percent

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('brightness', type=int, help='set brightness')
        args = parser.parse_args(strict=True)

        brightness_ctrl._set(int(args.get('brightness')))
        return "brightness changed"


api.add_resource(SetBrightness, '/api/brightness')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8520, debug=True)
