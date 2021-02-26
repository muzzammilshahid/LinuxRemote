import shlex
import subprocess
import pickledb
import random

from flask import Flask
from flask import send_from_directory
from flask_restful import Api, Resource, reqparse

from lock_screen import Display
from pesh_service import Discovery

import numpy as np
import cv2
import pyautogui

import alsaaudio
import psutil

app = Flask(__name__)
api = Api(app)
port = 5009
display = Display()
discovery = Discovery(port)

db = pickledb.load('test.db', True)
if not db.exists('database'):
    dict_ = db.dcreate('database')


def run(command):
    subprocess.check_call(shlex.split(command))


def screenshot():
    image = pyautogui.screenshot()
    image = cv2.cvtColor(np.array(image),
                         cv2.COLOR_RGB2BGR)
    print("Screenshot     ")
    cv2.imwrite("image.png", image)


# function returning time in hh:mm:ss
def convertTime(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return "%d:%02d:%02d" % (hours, minutes, seconds)


# returns a tuple
battery = psutil.sensors_battery()


class GetSetMute(Resource):
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


class GetSetVolume(Resource):

    def get(self):
        m = alsaaudio.Mixer()
        vol = m.getvolume()
        vol = int(vol[0])
        return vol

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('volume', type=int, help='volume of the speakers')
        args = parser.parse_args(strict=True)
        vol = args.get("volume")
        m = alsaaudio.Mixer()
        m.setvolume(vol)
        return {"volume": args.get("volume")}, 200


class GetSetMuteMic(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('set_mute', type=int, help='Toggle mute/unmute states', choices=(1, 0))
        args = parser.parse_args(strict=True)

        if args.get("set_mute") == 1:
            try:
                run("amixer -D pulse sset Capture nocap")
                is_muted = True
            except ChildProcessError:
                is_muted = False
        else:
            try:
                run("amixer -D pulse sset Capture cap")
                is_muted = False
            except ChildProcessError:
                is_muted = True

        return {"is_muted": is_muted}, 200


class GetSetMicVolume(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('volume', type=int, help='volume of the speakers')
        args = parser.parse_args(strict=True)
        vol = args.get("volume")
        run(f"amixer -D pulse set Capture {vol}%")
        return {"volume": args.get("volume")}, 200


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
        parser = reqparse.RequestParser()
        parser.add_argument('link', type=str, help='Toggle lock/unlock states')
        args = parser.parse_args(strict=True)
        link = args.get("link")
        print(link)

        run(f'xdg-open {link}')
        return {"open": link}, 200


class Verify(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('device_id', type=str, help='Device Id')
        args = parser.parse_args()
        device_id = args['device_id']
        if db.dexists('database', device_id):
            return True
        return False


class Pair(Resource):
    dict = {"otp": 123}

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('device_id', type=str, help='Device ID')
        parser.add_argument('otp', type=str, help='OTP')
        args = parser.parse_args()
        if str(self.dict.get("otp")) == args['otp']:
            db.dadd('database', (args['device_id'], self.dict.get("otp")))
            db.dump()
            return True
        return False

    def get(self):
        otp = random.randint(10000, 99999)
        self.dict["otp"] = otp
        print(self.dict.get("otp"))
        return self.dict.get("otp"), 200


@app.route('/api/screenshot')
def download_file():
    screenshot()
    image = send_from_directory('.', "image.png", as_attachment=False)
    return image, 200


class BatteryInfo(Resource):
    def get(self):
        percentage = battery.percent
        plugin_info = battery.power_plugged
        battery_left = convertTime(battery.secsleft)
        return 200, {"percentage": percentage, "plugin_info": plugin_info, "battery_time_left": battery_left}


api.add_resource(GetSetMute, '/api/volume')
api.add_resource(GetSetVolume, '/api/vol')
api.add_resource(GetSetMuteMic, '/api/mic/mute')
api.add_resource(GetSetMicVolume, '/api/mic/vol')
api.add_resource(GetSetLock, '/api/lock')
api.add_resource(OpenLink, '/api/open')
api.add_resource(Pair, '/api/pair/')
api.add_resource(Verify, '/api/verify/')
api.add_resource(BatteryInfo, '/api/battery/')

if __name__ == '__main__':
    discovery.publish()
    app.run(host='0.0.0.0', port=port, debug=True)
    discovery.unpublish()
