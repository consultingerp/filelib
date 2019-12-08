# -*-coding:utf-8-*-
import os


def armtomp3(name):
    mp3_file_name = name[0:name.rfind('.')] + '.mp3'
    mp3_name = 'ffmpeg  -y -i ' + name + ' ' + mp3_file_name
    os.system(mp3_name)
