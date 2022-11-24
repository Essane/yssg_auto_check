import time

import execjs
import requests
from requests.adapters import HTTPAdapter
from retrying import retry

from encrypt import EncryptClass

user_data = [
    # {
    #     "notifyToken": "0ca2e6f891b44f17b91a0e1f1e73ba70",
    #     "phone": "17772298110",
    #     "token": "eyJhbGciOiJSUzUxMiJ9.eyJBVFRSX3VzZXJObyI6IjEzNTAwMDc0NjkiLCJzdWIiOiIxMzUwMDA3NDY5IiwiaXNzIjoiY2FzLnNxZ3h5LmVkdS5jbiIsImRldmljZUlkIjoiWU1RMjZaQUhoN0lEQUZUMWNMRld2UUJQIiwiQVRUUl9pZGVudGl0eVR5cGVJZCI6IjNlNmZjNDEwNDAzMTExZWNkZGZlODViMjNjOGFjMDlkIiwiQVRUUl9hY2NvdW50SWQiOiJlNzExMzc2MGZhMjIxMWVjNWM5NThiYzFiYmU1OGY4MyIsIkFUVFJfdXNlcklkIjoiZTZmY2VjMTBmYTIyMTFlYzVjOTU4YmMxYmJlNThmODMiLCJBVFRSX2lkZW50aXR5VHlwZUNvZGUiOiJUMDEiLCJBVFRSX2lkZW50aXR5VHlwZU5hbWUiOiLmlZnogYzlt6UiLCJBVFRSX29yZ2FuaXphdGlvbk5hbWUiOiLkv6Hmga_kuI7nlLXlrZDlt6XnqIvlrabpmaIiLCJBVFRSX3VzZXJOYW1lIjoi5p2o6ZSQIiwiZXhwIjoxNjcxNzE5Mzc2LCJBVFRSX29yZ2FuaXphdGlvbklkIjoiNDAxIiwiaWF0IjoxNjY5MTI3Mzc2LCJqdGkiOiJJZC1Ub2tlbi12em1vN0hEZ1JFTkVJdk1YIiwicmVxIjoiY29tLnN1cHdpc2RvbS5zcWd4eWFwcCIsIkFUVFJfb3JnYW5pemF0aW9uQ29kZSI6IjQwMSJ9.gYDYeRQPUxWlyW2vU93uT88THX1bMe1DgFylVP5K6MJzefmtwYCeQSI6IuNnqNIj5mzwfeYnClQr2b3ag1hG75FjUPlWwXMTQ_v5s5gbToAvCxCOVJywqNePT_6KPOlJsh8rZYcQNSVH6bqSXFIYXGMOsm6o3mZ4FOop5JcRt2WhRjQ4SxPxc6Wqm8I4cnUD3MWfWuV6tOv9enDKkcipHTjhWBeE6gKwwytNX4MDV-y0x-iLI8Fo_p7y6ttyukMnB7l-3xPMk7eiR2eHg3Gb7AZr88206nrsoFHxdiCsi74yiTkAa13gxOCHM4T4IgLosYLXXxzPcaxGUBxaHy6beg"
    # },
    {
        "notifyToken": "c16903a57912476e898db289784aeeee",
        "phone": "13353610501",
        "token": "eyJhbGciOiJSUzUxMiJ9.eyJBVFRSX3VzZXJObyI6IjMyMjAwMjAyMTUiLCJzdWIiOiIxMzUwMDA3NDc1IiwiaXNzIjoiY2FzLnNxZ3h5LmVkdS5jbiIsImRldmljZUlkIjoiMzE3REVCRDgtRDAyQi00NzJFLUE4OTAtOTM1RjI0NkIyNTIyIiwiQVRUUl9pZGVudGl0eVR5cGVJZCI6IjNlNmZjNDEwNDAzMTExZWNkZGZlODViMjNjOGFjMDlkIiwiQVRUUl9hY2NvdW50SWQiOiJmMjE5NzczMGZhMjIxMWVjNWM5NThiYzFiYmU1OGY4MyIsIkFUVFJfdXNlcklkIjoiMmE1NWI1MDA0ODdiMTFlY2I4OWE2ODE1NDc0ODk1YmQiLCJBVFRSX2lkZW50aXR5VHlwZUNvZGUiOiJUMDEiLCJBVFRSX2lkZW50aXR5VHlwZU5hbWUiOiLmlZnogYzlt6UiLCJBVFRSX29yZ2FuaXphdGlvbk5hbWUiOiLkv6Hmga_kuI7nlLXlrZDlt6XnqIvlrabpmaIiLCJBVFRSX3VzZXJOYW1lIjoi546L54Kz5r2tIiwiZXhwIjoxNjcxNTEyMDMwLCJBVFRSX29yZ2FuaXphdGlvbklkIjoiNDAxIiwiaWF0IjoxNjY4OTIwMDMwLCJqdGkiOiJJZC1Ub2tlbi11Wm95SjhvUzVDYlRUQ3h6IiwicmVxIjoiY29tLnN1cHdpc2RvbS5zcWd4eWFwcCIsIkFUVFJfb3JnYW5pemF0aW9uQ29kZSI6IjQwMSJ9.gOp9yQqD7angioCqOqlhlUvuTRgB302bRtSeb9Y_oRLPplVo3UedxMzvbnv6TvKFdHigz1WPLTf2zSIVx6WVhnjxXrtNlh3K9cy18grVVAIRpY1HpBT5hbjuLlfk7PZXlsgOkOR-etl2xlWHxgJ52hCxjWZStVBvlaqPaZENM25UP-CTn1QI0DkIrg3yReMd3-aWlmOYvTGUOAmUiAdprycHs2mqKpSaWQE3Zn8GDAL5mJVQWIowjTC6zMPKGfJdiNqkzu9hbaad7amjXj7u1HOxxIkLkno67i-GdVAT6NNEYuMI95ZIJcQLox5faxii81zqz43NZZ9-ZUFAqcLhUA"
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
    resp = session.get(url="https://formflow.sqgxy.edu.cn/formflow/v1/user/getUserInfo2", headers=headers, timeout=5)
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
        """)  # 获取代码编译完成后的对象
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
    notifyList.append(str(exception))
    return True


@retry(stop_max_attempt_number=5, retry_on_exception=is_retry)
def run(item):
    result = False
    msg = None
    for count in range(5):
        count += 1
        result, msg = commit_act_form(item['token'], item['phone'])
        notify(item['notifyToken'], "打卡通知",
               "%s: 第%d打卡：%s" % (str(time.strftime("%Y-%m-%d %H:%M:%S")), count, msg))
        if result:
            break
    if not result:
        msg = "打卡失败,已重试5次！"


def main():
    item = None
    try:
        for item in user_data:
            run(item)
    except Exception as e:
        print(e.args)
        notify(item['notifyToken'], "打卡通知", '\n'.join(list(map(str, notifyList))))


def main_handler(event, context):
    return main()

# if __name__ == '__main__':
#     notify("c16903a57912476e898db289784aeeee", "测试", "内容")
#     main()
