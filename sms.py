import hashlib
import hmac
import base64
import requests
import time
from config import *


def make_signature(timestamp):
    secret_key = bytes(SMS_API_SECRET, 'UTF-8')
    method = "POST"
    uri = f'/sms/v2/services/{SMS_SERVICE_ID}/messages'
    message = method + " " + uri + "\n" + timestamp + "\n" + SMS_API_KEY
    message = bytes(message, 'UTF-8')
    return base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())


def send_sms(phone_number):
    timestamp = str(int(time.time() * 1000))
    signature = make_signature(timestamp)
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'x-ncp-apigw-timestamp': timestamp,
        'x-ncp-iam-access-key': SMS_API_KEY,
        'x-ncp-apigw-signature-v2': signature
    }
    body = {
        "type": 'sms',
        "contentType": "COMM",
        "countryCode": '82',
        "from": SMS_SENDER_NUMBER,
        "content": "119 구조 요청",
        "messages": [
            {
                "to": phone_number,
                "content": f'[응급 신고] 주소: ㅇㅇ도 ㅇㅇ시 ㅇㅇ로ㅇㅇ번길 ㅇㅇ, 작업자 끼임사고 발생, 구조 바랍니다.'
            }
        ]
        }
    SMS_URL = f'https://sens.apigw.ntruss.com/sms/v2/services/{SMS_SERVICE_ID}/messages'
    response = requests.post(SMS_URL, headers=headers, json=body)
    return response.json()
