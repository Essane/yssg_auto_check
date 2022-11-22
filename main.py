import requests
import time
import json
import execjs
from requests.adapters import HTTPAdapter
import os
from encrypt import EncryptClass

# barkToken = "uruobYztCzx9BaDnT5CxKc"
# token = "eyJhbGciOiJSUzUxMiJ9.eyJBVFRSX3VzZXJObyI6IjMyMjAwMjAyMTUiLCJzdWIiOiIxMzUwMDA3NDc1IiwiaXNzIjoiY2FzLnNxZ3h5LmVkdS5jbiIsImRldmljZUlkIjoiMzE3REVCRDgtRDAyQi00NzJFLUE4OTAtOTM1RjI0NkIyNTIyIiwiQVRUUl9pZGVudGl0eVR5cGVJZCI6IjNlNmZjNDEwNDAzMTExZWNkZGZlODViMjNjOGFjMDlkIiwiQVRUUl9hY2NvdW50SWQiOiJmMjE5NzczMGZhMjIxMWVjNWM5NThiYzFiYmU1OGY4MyIsIkFUVFJfdXNlcklkIjoiMmE1NWI1MDA0ODdiMTFlY2I4OWE2ODE1NDc0ODk1YmQiLCJBVFRSX2lkZW50aXR5VHlwZUNvZGUiOiJUMDEiLCJBVFRSX2lkZW50aXR5VHlwZU5hbWUiOiLmlZnogYzlt6UiLCJBVFRSX29yZ2FuaXphdGlvbk5hbWUiOiLkv6Hmga_kuI7nlLXlrZDlt6XnqIvlrabpmaIiLCJBVFRSX3VzZXJOYW1lIjoi546L54Kz5r2tIiwiZXhwIjoxNjcxNTEyMDMwLCJBVFRSX29yZ2FuaXphdGlvbklkIjoiNDAxIiwiaWF0IjoxNjY4OTIwMDMwLCJqdGkiOiJJZC1Ub2tlbi11Wm95SjhvUzVDYlRUQ3h6IiwicmVxIjoiY29tLnN1cHdpc2RvbS5zcWd4eWFwcCIsIkFUVFJfb3JnYW5pemF0aW9uQ29kZSI6IjQwMSJ9.gOp9yQqD7angioCqOqlhlUvuTRgB302bRtSeb9Y_oRLPplVo3UedxMzvbnv6TvKFdHigz1WPLTf2zSIVx6WVhnjxXrtNlh3K9cy18grVVAIRpY1HpBT5hbjuLlfk7PZXlsgOkOR-etl2xlWHxgJ52hCxjWZStVBvlaqPaZENM25UP-CTn1QI0DkIrg3yReMd3-aWlmOYvTGUOAmUiAdprycHs2mqKpSaWQE3Zn8GDAL5mJVQWIowjTC6zMPKGfJdiNqkzu9hbaad7amjXj7u1HOxxIkLkno67i-GdVAT6NNEYuMI95ZIJcQLox5faxii81zqz43NZZ9-ZUFAqcLhUA"
# phone = "13353610501"

barkToken = os.environ['BARKTOKEN']
token = os.environ['token']
phone = os.environ['phone']

session = requests.session()
session.trust_env = False
session.mount('http://', HTTPAdapter(max_retries=5))
session.mount('https://', HTTPAdapter(max_retries=5))


def notify(title, content):
    session.get("https://api.day.app/%s/%s/%s" % (barkToken, title, content))


def generate_data_header():
    headers = {
        "Accept": "application/json, text/plain, */*",
        "authorization": "Bearer " + token,
        "Origin": "https://form-design-m.sqgxy.edu.cn",
        "User-Agent": "Mozilla/5.0 (Linux; Android 8.1.0; Pixel Build/OPM4.171019.021.P1; wv) AppleWebKit/537.36 ("
                      "KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.87 Mobile Safari/537.36 SuperApp"
    }
    resp = session.get(url="https://formflow.sqgxy.edu.cn/formflow/v1/user/getUserInfo2", headers=headers)
    if not resp.json()['flag']:
        return False, resp.json()['msg']
    headers.update({
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://form-design-m.sqgxy.edu.cn/write?yyid=72f91523-1002-43cb-b29a-7f99a8a2e28b&token=[token]",
    })
    with open('data.txt', 'r', encoding="utf-8") as f:
        data = f.read()
    t = time.strftime("%Y-%m-%d %H:%M:%S")
    data = data.replace("[time]", t).replace("[name]", resp.json()['data']['name']).replace("[code]",
                                                                                            resp.json()['data'][
                                                                                                'accountName']).replace(
        "[phone]", phone)
    return data, headers


def get_next_task_approval():
    data, headers = generate_data_header()
    data = {
        "deploymentId": "dc4cef742faf441f834bb7265f78da29",
        "jsonv": json.dumps(data),
        "outid": ""
    }
    try:
        resp = session.post(url="https://formflow.sqgxy.edu.cn/formflow/v1/process/getNextTaskApproval", data=data,
                            headers=headers)
        if not resp.json()['flag']:
            return False, resp.json()['msg']
        return True
    except Exception:
        return False, "error"


def commit_act_form():
    try:
        data, headers = generate_data_header()
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
                            headers=headers, timeout=5)
        return resp.json()['flag'], resp.json()['msg']
    except Exception as err:
        return False, str(err.args)


if __name__ == '__main__':
    result = False
    msg = None
    count = 0
    try:
        while count < 5:
            count += 1
            result, msg = commit_act_form()
            if result:
                msg = "打卡成功!"
                break
        if not result:
            msg = "打卡失败,已重试5次！"
    except Exception as err:
        msg = str(err.args)
    finally:
        notify("打卡通知", msg)
