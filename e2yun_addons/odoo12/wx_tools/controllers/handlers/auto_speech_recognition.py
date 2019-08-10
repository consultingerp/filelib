# encoding = utf-8
from aip import AipSpeech
import os

APP_ID = '16960984'
API_KEY = 'ZVFgFnQ1CxE3UintGnsCcKVI'
SECRET_KEY = 'B9GgHbcqxUsUzRlyxM5Uh9FdG08EKNex'
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)


def voice_conversion(file):

    # 音频文件格式转换
    try:
        mp3_file = file[0:file.rfind('.')] + '.mp3'
        get_mp3 = 'ffmpeg.exe -y -i '+file+' -ac 1 -ar 16.0k '+mp3_file
        os.system(get_mp3)
        pcm_file = file[0:file.rfind('.')] + '.pcm'
        get_pcm = 'ffmpeg.exe -y -i ' + mp3_file + ' -f s16le -acodec pcm_s16le ' + pcm_file
        os.system(get_pcm)
    except Exception as e:
        return e

    # 智能识别转换后的音频文件
    with open(pcm_file, 'rb') as fp:
        re = fp.read()
        res = client.asr(re, 'pcm', 16000, {'dev_pid': 1536})
        # print(res)
        message = ''.join(res['result'])
        # print(message)
        return message