import os
import shlex
import subprocess

from flask import Flask, request
from flask_restful import Api, Resource, reqparse

from lock_screen import Display
from pesh_service import Discovery

app = Flask(__name__)
api = Api(app)
port = 5009
display = Display()
discovery = Discovery(port)


def run(command):
    subprocess.check_call(shlex.split(command))


class GetSetVolume(Resource):
    def get(self):
        raw = subprocess.check_output(shlex.split("pacmd list-sinks"))
        is_muted = raw.find(b"muted: yes") != -1
        data = {"is_muted": is_muted}

        return data, 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('set_mute', type=int, help='Toggle mute/unmute states', choices=(1, 0))
        args = parser.parse_args(strict=True)

        if args.get("set_mute") == 1:
            try:
                run("amixer -D pulse sset Master mute")
                is_muted = True
            except ChildProcessError:
                is_muted = False
        else:
            try:
                run("amixer -D pulse sset Master unmute")
                is_muted = False
            except ChildProcessError:
                is_muted = True

        return {"is_muted": is_muted}, 200


class GetSetLock(Resource):
    def get(self):
        data = {"is_locked": True if display.is_locked() else False}
        return data, 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('set_lock', type=int, help='Toggle lock/unlock states', choices=(1, 0))
        args = parser.parse_args(strict=True)

        if args.get("set_lock") == 1:
            try:
                display.lock()
                is_locked = True
            except ChildProcessError:
                is_locked = False
        else:
            try:
                run("loginctl unlock-session")
                is_locked = False
            except ChildProcessError:
                is_locked = True

        return {"is_locked": is_locked}, 200


class OpenLink(Resource):
    def post(self):
        print("I am here")
        parser = reqparse.RequestParser()
        parser.add_argument('link', type=str, help='Toggle lock/unlock states')
        args = parser.parse_args(strict=True)
        link = args.get("link")
        print(link)

        run(f'xdg-open {link}')
        return {"open": link}, 200


api.add_resource(GetSetVolume, '/api/volume')
api.add_resource(GetSetLock, '/api/lock')
api.add_resource(OpenLink, '/api/open')


if __name__ == '__main__':
    discovery.publish()
    app.run(host='0.0.0.0', port=port, debug=True)
