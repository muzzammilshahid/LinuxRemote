#!/usr/bin/bash
sudo apt update
sudo apt upgrade
sudo apt install python3-pip
sudo apt install libasound2-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg

sudo apt-get install -y python-dbus-dev
sudo apt-get install libglib2.0-*

sudo pip3 install -r requirements.txt
