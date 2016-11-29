# coding: utf-8
import base64
from .exceptions import APIError
from .clients import emotibotclient, baiduclient
from .utils import get_mac_address


class Emotibot(object):
    """A client for request Turing Robot.

    Attributes:
        key: The key string got from http://www.tuling123.com.
    """
    def __init__(self, appid, userid):
        self.appid = appid
        self.userid = userid

    def ask_emotibot(self, question):
        params = {
            "cmd": "chat",
            "appid": self.appid,
            "userid": self.userid,
            "text": question
        }
        ret = emotibotclient.query(params)
        code = ret.get('return')
        if code == 0:
            return Emotibot.json_parser(ret.get('data'))
        else:
            raise APIError('Cannot handle this ret code: %s' % code)

    @staticmethod
    def json_parser(retdata):
        func_list = ['tts']
        try:
            reply = retdata[0].get('value')
            fun_type = retdata[0].get('cmd')
            if fun_type == 'news':
                articles = retdata[0].get('data')
                # picurl = [random.choice(item['imageUrls']).get(
                #     'url', '') if item['imageUrls'] else '' for item in articles][:5]
                title = [item['title'] for item in articles.get('items')][:5]
                reply = ",".join(title)

            elif fun_type == 'reminder':
                func_list.append('reminder')
                args = [reply, retdata]
                return func_list, args

            elif fun_type == 'cooking':
                articles = retdata[0].get('data')
                title = [item['title'] for item in articles][:5]
                reply = ",".join(title)

            elif fun_type == 'kuaidi':
                if len(retdata) == 1:
                    reply = retdata[0].get('value')
                elif len(retdata) > 1:
                    titles = []
                    for data in retdata:
                        titles.append(data.get('value'))
                    reply = ",".join(title)

            elif fun_type == 'concert':
                articles = retdata[0].get('data')

                # picurl = [item['imgUrl'] for item in articles][:5]
                title = [item['title'] for item in articles][:5]
                reply = ",".join(title)

            elif fun_type == 'music':
                # returned msg with music type
                reply = u'微信端暂时不支持音乐播放'

            elif fun_type == 'movie':
                movie = retdata[0].get('data').get('answer')
                reply = ",".join(movie)

            elif fun_type == 'taxi':
                # returned msg with taxi type
                info = retdata[0].get('data')
                taxi_dic = {u"出租车": 1, u"专车": 2, u"快车": 3, u"代驾": 5}
                if info:
                    biz = taxi_dic.get(info.get('info').get("type"))
                    to = info.get('info').get("to")

                    if biz:
                        if to:
                            location = to.get("location")
                            maptype = to.get("maptype")
                            lat = location.get("lat")
                            lng = location.get("lng")
                            url = "http://common.diditaxi.com.cn/general/webEntry?maptype=%s&tolat=%s&tolng=%s&biz=%s" % \
                                  (maptype, lat, lng, biz)
                        else:
                            url = "http://common.diditaxi.com.cn/general/webEntry?maptype=baidu&biz=%s" % biz
                    else:
                        url = "http://common.diditaxi.com.cn/general/webEntry?maptype=baidu&biz=1"
                reply = u'滴滴打车可以为您提供打车服务'
                # reply = u'想要打车吗？点击链接可以为您提供打车服务：<a href="%s">%s</a>' % (url, u"滴滴打车")

            elif fun_type == 'voice':
                # returned msg with food_recommend type
                url = retdata[0].get('value')
                reply = u'点击链接听听我给您作的曲吧！(^o^)  <a href="%s">%s</a>' % (url, u'歌曲')

            elif fun_type == '':
                contents = []
                if len(retdata) == 1:
                    reply = retdata[0].get('value')
                else:
                    for data in retdata:
                        if data.get('cmd') == 'image':
                            continue
                        else:
                            contents.append(data.get('value'))

                    reply = ",".join(contents)

            else:
                reply = '不支持该功能，敬请期待.'

        except ValueError:
            reply = u"原谅我太年轻，不懂你说的是啥～"

        except Exception as e:
            print str(e)
            reply = u"访问次数上限，明天请早。"

        return func_list, [reply]


class BaiduVoice(object):
    """A client for request Turing Robot.

    Attributes:
        token: The token string got from https://openapi.baidu.com/oauth/2.0/token.
        cuid: Unique identification of user, default is MAC address.
    """
    def __init__(self, token):
        self.token = token
        self.cuid = get_mac_address()

    def asr(self, data, rate, format_='wav',
            cuid=None, ptc=1, lan='zh'):
        """Constructs and sends an Automatic Speech Recognition request.

        Args:
            file_: the open file with methods write(), close(), tell(), seek()
                   set through the __init__() method.
            format_:(optional) the audio format, default is 'wav'
            cuid:(optional) Unique identification of user, default is MAC address.
            ptc:(optional) nbest results, the number of results.
            lan:(optional) language, default is 'zh'.
        Returns:
            A list of recognition results.
        Raises:
            ValueError
            RecognitionError
            VerifyError
            APIError
            QuotaError
        """
        data = b''.join(data)
        speech = base64.b64encode(data)
        size = len(data)
        print "wav length:", size
        # if format_ != 'wav':
        #     raise ValueError('Unsupported audio format')

        json_data = {
            'channel': 1,
            'speech': speech, 'len': size,
            'rate': rate,
            'format': format_,
            'token': self.token,
            'cuid': cuid or self.cuid,
            'ptc': ptc,
            'lan': lan
        }

        return baiduclient.asr(json_data)

    def tts(self, tex, lan='zh', ctp=1,
            cuid=None, spd=5, pit=5, vol=5, per=0):
        """Constructs and sends an Text To Speech request.

        Args:
            tex: The text for conversion.
            lan:(optional) language, default is 'zh'.
            ctp:(optional) Client type, default is 1.
            cuid:(optional) Unique identification of user, default is MAC address.
            spd:(optional) speed, range 0-9, default is 5.
            pit:(optional) pitch, range 0-9, default is 5.
            vol:(optional) volume, range 0-9, default is 5.
            per:(optional) voice of male or female, default is 0 for female voice.
        Returns:
            A binary string of MP3 format audio.
        Raises:
            ValueError
            VerifyError
            APIError
        """
        params = {
            'tex': tex,
            'lan': lan,
            'tok': self.token,
            'ctp': ctp,
            'cuid': cuid or self.cuid,
            'spd': spd,
            'pit': pit,
            'vol': vol,
            'per': per
        }
        return baiduclient.tts(params)

    @staticmethod
    def get_baidu_token(api_key, secret_key):
        """Get Baidu Voice Service token by api key and secret.

        Functions of other args of response are not confirmed, so the whole
        response dict will be returned, you can access the token by ret['access_token'].
        """
        params = {
            'grant_type': 'client_credentials',
            'client_id': api_key,
            'client_secret': secret_key
        }
        return baiduclient.get_token(params)
