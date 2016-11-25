# coding: utf-8
import logging
import time
import traceback

from snowboy import snowboydecoder

from settings import (BasicConfig as BC, HotwordConfig as HWC)
from utils import AudioHandler
from voicetools import BaiduVoice, Emotibot

logger = logging.getLogger()

# FUNC_MAP = {
#     Keyword(['备忘录', ]).value: 'memo_today',
#     Keyword(['提醒', ]).value: 'memo_today',
#     Keyword(['备忘录', '今天']).value: 'memo_today',
#     Keyword(['提醒', '今天']).value: 'memo_today',
#     Keyword(['备忘录', '明天']).value: 'memo_tomo',
#     Keyword(['提醒', '明天']).value: 'memo_tomo',
#     Keyword(['备忘录', '播放']).value: 'play_memo_today',
#     Keyword(['提醒', '播放']).value: 'play_memo_today',
#     Keyword(['备忘录', '播放', '明天']).value: 'play_memo_tomo',
#     Keyword(['提醒', '播放', '明天']).value: 'play_memo_tomo',
#     Keyword(['备忘录', '删除']).value: 'del_all_memo',
#     Keyword(['提醒', '删除']).value: 'del_all_memo',
#     Keyword(['备忘录', '删除', '最后']).value: 'del_last_memo',
#     Keyword(['提醒', '删除', '最后']).value: 'del_last_memo',
#     Keyword(['备忘录', '删除', '第一条']).value: 'del_first_memo',
#     Keyword(['提醒', '删除', '第一条']).value: 'del_first_memo'
# }
FUNC_MAP = dict()


class BaseHandler(object):

    def __init__(self, baidu_token=None):
        if not baidu_token:
            try:
                token = BaiduVoice.get_baidu_token(BC.VOICE_API_KEY, BC.VOICE_SECRET)
                self.token = token['access_token']
            except Exception, e:
                logger.warn(
                    '==Get baidu voice token failed==: %s', traceback.format_exc())
                raise e
        else:
            self.token = baidu_token
        self.bv = BaiduVoice(self.token)
        self.audio_handler = AudioHandler()
        self.detector = snowboydecoder.HotwordDetector(
            HWC.HOTWORD_MODEL, sensitivity=HWC.SENSITIVITY, audio_gain=HWC.GAIN)

    def __repr__(self):
        return '<BaseHandler>'

    def receive(self, data, rate):
        try:
            return self.bv.asr(data, rate)
        except Exception:
            logger.warn('==Baidu ASR failed==: %s', traceback.format_exc())

    def process(self, results):
        logger.info('==Recognition result==: %s', results[0])
        return FUNC_MAP.get("None", 'default'), results[0]

    def execute(self, func_name, result):
        func = getattr(ActionHandler, func_name)
        return func(self, result)

    def feedback(self, content=None):
        if content:
            try:
                with open(BC.OUTPUT_MP3_NAME, 'w') as w:
                    w.write(self.bv.tts(content))
            except Exception:
                logger.warn('==Baidu TTS failed==: %s', traceback.format_exc())
            else:
                self.audio_handler.aplay()

    def worker(self, data, rate):
        try:
            start = time.time()
            results = self.receive(data, rate)
            func, result = self.process(results)
            chat_start = time.time()
            content = self.execute(func, result)
            chat_end = time.time()
            self.feedback(content)
            end = time.time()
            logger.info("User: %s\nMirror: %s\nCost(s): %.2f Chat(s): %.2f" %
                        (results[0], content, end-start, chat_end-chat_start))

        except Exception:
            logger.warn('==worker failed==: %s', traceback.format_exc())
            # self.feedback('say it again')


class ActionHandler(object):

    """docstring for ActionHandler"""

    @staticmethod
    def default(base_handler, result):
        robot = Emotibot(BC.APP_ID, BC.USER_ID)
        try:
            content = robot.ask_emotibot(result)
        except Exception:
            logger.warn(traceback.format_exc())
            return '没有找到问题的答案'
        else:
            return content

#     @staticmethod
#     def _memo(date, base_handler):
#         base_handler.feedback('请说出记录内容')
#         audio = base_handler.audio_handler.arecord(6, is_buffer=True)
#         cache_handler = CacheHandler()
#         cache_handler.zset(date, audio, timestamp(), 86400*3)
#         return '完成记录'

#     @staticmethod
#     def memo_today(base_handler, result):
#         return ActionHandler._memo(
#             date=datetime.date.today().strftime('%Y-%m-%d'),
#             base_handler=base_handler
#             )

#     @staticmethod
#     def memo_tomo(base_handler, result):
#         return ActionHandler._memo(
#             date=(datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
#             base_handler=base_handler
#             )

#     @staticmethod
#     def play_memo(date, base_handler):
#         cache_handler = CacheHandler()
#         audio = cache_handler.zget(date, 0, -1)
#         if audio:
#             for item in audio:
#                 base_handler.audio_handler.aplay(item, is_buffer=True)
#             return '播放结束'
#         else:
#             base_handler.feedback('未找到记录')
#             return None

#     @staticmethod
#     def play_memo_tomo(base_handler, result):
#         return ActionHandler.play_memo(
#             date=(datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
#             base_handler=base_handler
#             )

#     @staticmethod
#     def play_memo_today(base_handler, result):
#         return ActionHandler.play_memo(
#             date=datetime.date.today().strftime('%Y-%m-%d'),
#             base_handler=base_handler
#             )

#     @staticmethod
#     def del_memo(date, start, end):
#         cache_handler = CacheHandler()
#         cache_handler.zdel(date, start, end)
#         return '删除成功'

#     @staticmethod
#     def del_last_memo(base_handler, result):
#         return ActionHandler.del_memo(
#             date=datetime.date.today().strftime('%Y-%m-%d'),
#             start=-1,
#             end=-1
#             )

#     @staticmethod
#     def del_first_memo(base_handler, result):
#         return ActionHandler.del_memo(
#             date=datetime.date.today().strftime('%Y-%m-%d'),
#             start=0,
#             end=0
#             )

#     @staticmethod
#     def del_all_memo(base_handler, result):
#         return ActionHandler.del_memo(
#             date=datetime.date.today().strftime('%Y-%m-%d'),
#             start=0,
#             end=-1
#             )
