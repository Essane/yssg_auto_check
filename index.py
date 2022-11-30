# -- coding:UTF-8 --
import time
import execjs
import requests
from requests.adapters import HTTPAdapter
from retrying import retry

from encrypt import EncryptClass

user_data = [
    {
        "notifyToken": "",
        "phone": "",
        "token": ""
    }
]

notifyList = []
session = requests.session()
session.trust_env = False
session.mount('http://', HTTPAdapter(max_retries=5))
session.mount('https://', HTTPAdapter(max_retries=5))


def notify(notify_token, title, content):
    data = {
        "token": notify_token,
        "title": title,
        "content": content,
    }
    requests.post(url="http://www.pushplus.plus/send/", data=data)


def generate_data_header(token, phone):
    headers = {
        "Accept": "application/json, text/plain, */*",
        "authorization": "Bearer " + token,
        "Origin": "https://form-design-m.sqgxy.edu.cn",
        "User-Agent": "Mozilla/5.0 (Linux; Android 8.1.0; Pixel Build/OPM4.171019.021.P1; wv) AppleWebKit/537.36 ("
                      "KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.87 Mobile Safari/537.36 SuperApp"
    }
    resp = session.get(
        url="https://formflow.sqgxy.edu.cn/formflow/v1/user/getUserInfo2", headers=headers, timeout=5)
    if not resp.json()['flag']:
        return False, resp.json()['msg']
    headers.update({
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://form-design-m.sqgxy.edu.cn/write?yyid=72f91523-1002-43cb-b29a-7f99a8a2e28b&token=" + token,
    })
    with open('data.txt', 'r', encoding="utf-8") as f:
        data = f.read()
    t = time.strftime("%Y-%m-%d %H:%M:%S")
    data = data.replace("[time]", t).replace("[name]", resp.json()['data']['name']).replace("[code]",
                                                                                            resp.json()['data'][
                                                                                                'accountName']).replace(
        "[phone]", phone)
    return data, headers


def commit_act_form(token, phone):
    try:
        data, headers = generate_data_header(token, phone)
        t = str(int(time.time()))
        key = "formflow" + t[:8]
        aes = EncryptClass(key)
        data = {
            "obj": aes.encrypt(data),
            "idUser": "",
            "idUserList": ""
        }
        ctx = execjs.compile("""
            function getUUid() {
                var t = (new Date).getTime()
                  , e = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (function(e) {
                    var n = (t + 16 * Math.random()) % 16 | 0;
                    return t = Math.floor(t / 16),
                    ("x" === e ? n : 7 & n | 8).toString(16)
                }
                ));
                return e
            };
        """)
        headers.update({
            "visitor": "0",
            "timeStr": t,
            "uuid": ctx.call("getUUid")
        })
        resp = session.post(url="https://formflow.sqgxy.edu.cn/formflow/v1/process/commitActForm", data=data,
                            headers=headers)
        return resp.json()['flag'], resp.json()['msg']
    except Exception as err:
        return False, str(err.args)


def is_retry(exception):
    notifyList.append("%s: 第%d次打卡：%s" % (
        str(time.strftime("%Y-%m-%d %H:%M:%S")), len(notifyList)+1, str(exception)))
    return True


@retry(stop_max_attempt_number=5, retry_on_exception=is_retry)
def run(item):
    result = False
    msg = None
    result, msg = commit_act_form(item['token'], item['phone'])
    if not result:
        raise RuntimeError(msg)
    return result, msg


def main():
    result = False
    msg = None
    msgList = []
    item = None
    for item in user_data:
        try:
            result, msg = run(item)
            print(result, msg)
        except Exception as e:
            print(e.args)
        finally:
            if not result:
                msg = '\n'.join(list(map(str, notifyList)))
            notify(item['notifyToken'], "打卡通知", msg)
            msgList.append(msg)
    return msgList


def main_handler(event, context):
    return main()

# if __name__ == '__main__':
#     main()
