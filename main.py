# coding: utf-8
import os
import sys
import signal

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)
interrupted = False


from utils import init_logging_handler
from handler import BaseHandler
logger = init_logging_handler()


def signal_handler(signal, frame):
    global interrupted
    logger.info("Interrupted...")
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted


# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)


def setup_GPIO():
    # import RPi.GPIO as GPIO
    # GPIO.setmode(GPIO.BCM)
    pass


def loop():
    logger.info("Initializing...")
    handler = BaseHandler()
    try:
        handler.detector.start(handler.worker, interrupt_check=interrupt_callback, sleep_time=0.03)
    except KeyboardInterrupt:
        pass
    # GPIO.cleanup()
    handler.detector.terminate()
    logger.info("Assistant closed...")

if __name__ == '__main__':
    loop()
