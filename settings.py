# coding: utf-8
import logging
import os
import platform
from voicetools import (
    APIError, RespError, RecognitionError, VerifyError, QuotaError)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


class BasicConfig(object):
    """Basic config for the raspi_assistant."""

    VOICE_API_KEY = 'dAkc6QvjXOR7eGeD9GcRRS9a'
    VOICE_SECRET = 'KfaFUjPjBchCKcuLU6yw1YdnbwrL1Cl9'
    APP_ID = '9d152115e232a48c2edea2d44825232b'
    USER_ID = '06C6D39DA8A3C205EDEE821C1202BFC97'
    INPUT_NAME = 'record.wav'
    OUTPUT_NAME = 'output.wav'
    OUTPUT_MP3_NAME = os.path.join(ROOT_DIR, 'output.mp3')


class HotwordConfig(object):
    if platform.system() == 'Darwin':
        HOTWORD_MODEL = os.path.join(ROOT_DIR, 'snowboy/models/magic.pmdl')
        SENSITIVITY = 0.45
        GAIN = 1
    elif platform.system() == 'Linux':
        HOTWORD_MODEL = os.path.join(ROOT_DIR, 'snowboy/models/rpi_magic.pmdl')
        SENSITIVITY = 0.4
        GAIN = 2


class ReminderConfig(object):
    DB_PATH = os.path.join(ROOT_DIR, 'db/reminder.db')
    DB_TABLE = 'reminder'


class GPIOConfig(object):
    """GPIO config"""


class LogConfig(object):
    LOGGING_FORMAT = '%(asctime)s %(funcName)s:%(lineno)d [%(levelname)s] %(message)s'
    LOGGING_LOCATION = os.path.join(ROOT_DIR, 'log/raspi_assistant.log')
    LOGGING_LEVEL = logging.INFO


class ErrNo(object):
    ExceptionMap = {
        3001: QuotaError,
        3002: VerifyError,
        3003: APIError,
    }
