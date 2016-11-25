# coding: utf-8
import logging
from logging.handlers import TimedRotatingFileHandler
# import time
# import random
# import base64
# from functools import wraps
from hashlib import md5
from subprocess import Popen, PIPE
from tempfile import TemporaryFile
import platform
import pyaudio
import wave
# import Queue

from settings import (
    LogConfig as LC, BasicConfig as BC)

# def convert_to_wav(file_):
#     """convert mp3 to wav"""
#     p = Popen(['ffmpeg', '-y', '-i', '-', '-f', 'wav', BC.OUTPUT_NAME], stdin=file_ , stdout=None, stderr=None)
#     p.wait()


def init_logging_handler():
    handler = TimedRotatingFileHandler(LC.LOGGING_LOCATION, when='MIDNIGHT')
    formatter = logging.Formatter(LC.LOGGING_FORMAT)
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.setLevel(LC.LOGGING_LEVEL)
    logger.addHandler(handler)
    return logger


def unique_id(func, args, kwargs):
    return md5(func.__name__ + repr(args) + repr(kwargs)).hexdigest()


class AudioHandler(object):
    """AudioHandler for processing audio, including recording and playing."""
    def __init__(self, chunk=1024, format_=pyaudio.paInt16, channels=1, rate=16000):
        self.CHUNK = chunk
        self.FORMAT = format_
        self.CHANNELS = channels
        self.RATE = rate
 #       self.active_process = Queue.Queue(maxsize=1)
 #       self.active_process.put({'empty': 0})

    def record(self, record_seconds, file_):
        p = pyaudio.PyAudio()

        stream = p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        input_device_index=0,
                        frames_per_buffer=self.CHUNK)

        frames = []

        for i in range(0, int(self.RATE / self.CHUNK * record_seconds)):
            data = stream.read(self.CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(file_, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(''.join(frames))
        wf.close()

    def arecord(self, record_seconds, is_buffer=False, file_=BC.INPUT_NAME):
        if is_buffer:
            p = Popen(
                ['arecord', '-r', '16000', '-D', 'plughw:1,0', '-f', 'S16_LE', '-d', str(record_seconds), '-'],
                stdout=PIPE,
                stderr=PIPE)
            stdout, _ = p.communicate()
            return stdout
        else:
            p = Popen(
                ['arecord', '-r', '16000', '-D', 'plughw:1,0', '-f', 'S16_LE', '-d', str(record_seconds), file_])
            p.wait()

    def aplay(self, file_=BC.OUTPUT_MP3_NAME, is_buffer=False):
        if is_buffer:
            temp = TemporaryFile()
            temp.write(file_)
            temp.seek(0)
            p = Popen(['play', '-'], stdin=temp)
            temp.close()
        else:
            if platform.system() == 'Darwin':
                player = 'play'
            elif platform.system() == 'Linux':
                player = 'mpg321'
            cmd = '%s %s 1>/dev/null 2>/dev/null &' % (player, file_)
            p = Popen(cmd, shell=True, stdout=PIPE)
            # self.active_process.put({'play': p})
        p.wait()

    def play(self, file_):
        wf = wave.open(file_, 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        data = wf.readframes(self.CHUNK)

        while data != '':
            stream.write(data)
            data = wf.readframes(self.CHUNK)

        stream.stop_stream()
        stream.close()

        p.terminate()


class Keyword(object):
    """Object for """
    def __init__(self, list_):
        list_.sort()
        self.keywords = list_
        self.value = '/'.join(list_)

    def __repr__(self):
        return self.value
