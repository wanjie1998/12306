# !/usr/bin/env python
# -*- coding:utf-8 -*-
# author: wanjie time:2018/6/25 0025

import re
import time
import json
import requests
# 自己定义的文件
from setting import *
from identify_captcha import IdentifyCaptchaPicture

# 定义一个session，用于保持登陆状态
session = requests.session()
# 取消验证SSL
session.verify = False


class Login(object):
    """登录类"""
    def __init__(self):
        self.identify_captcha_picture = IdentifyCaptchaPicture()

    # 用于下载验证码图片
    @staticmethod
    def download_captcha_picture():
        url = 'https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=' \
              'E&module=login&rand=sjrand&0.1205810415186287'
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            captcha_picture = response.content
            with open('captcha_picture.jpg', 'wb') as f:
                f.write(captcha_picture)

    # 用于识别验证码 别人写好的接口 有的时候不能用
    @staticmethod
    def _identify_captcha_picture():
        time.sleep(1)
        url = 'http://littlebigluo.qicp.net:47720/'
        files = {
            'file': ('captcha_picture.jpg', open('captcha_picture.jpg', 'rb'), 'image/jpeg')
        }
        response = session.post(url, files=files, headers=headers)
        if response.status_code == 200:
            html = response.text
            things = re.findall('<B>(.*?)</B>', html)[0]
            serial_number = re.findall('<B>(.*?)</B>', html)[1]
            things_list = str(things).split(' ')
            serial_number_list = str(serial_number).split(' ')
            print('识别出的文字为：', things_list)
            print('图片编号为：', serial_number_list)
            return serial_number_list

    # 登录
    def login(self):
        # # 验证码人工识别
        # coordinates = input('请输入验证码的坐标：')
        # coordinates = coordinates.split(',')
        # # 通过别人的接口识别验证码
        # coordinates = self._identify_captcha_picture()
        # 验证码机器学习输入
        coordinates = self.identify_captcha_picture.identify_captcha_picture()
        print('机器识别出来的结果：', coordinates)
        answer = ''
        for i in coordinates:
            answer += locate[i]
        # 验证码校验链接
        url = 'https://kyfw.12306.cn/passport/captcha/captcha-check'
        data = {
            'answer': answer,
            'login_site': 'E',
            'rand': 'sjrand'
        }
        response = session.post(url, headers=headers, data=data)
        if response.status_code == 200:
            html = response.text
            data = json.loads(html)
            print('100001:', data)
            if data['result_code'] == '4':
                print('验证码校验成功！！')

                # 登录链接
                url = 'https://kyfw.12306.cn/passport/web/login'
                data = {
                    'appid': 'otn',
                    'password': password,
                    'username': username
                }
                response = session.post(url, headers=headers, data=data)
                if response.status_code == 200:
                    html = response.text
                    data = json.loads(html)
                    print('100002:', data)

                    # 登录的再次验证
                    url = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
                    data = {
                        'appid': 'otn'
                    }
                    response = session.post(url, headers=headers, data=data)
                    tk = ''
                    if response.status_code == 200:
                        html = response.text
                        data = json.loads(html)
                        print('100003:', data)
                        tk = data['newapptk']

                    # 登陆的再次验证
                    url = 'https://kyfw.12306.cn/otn/uamauthclient'
                    data = {
                        'tk': tk
                    }
                    response = session.post(url, headers=headers, data=data)
                    if response.status_code == 200:
                        html = response.text
                        data = json.loads(html)
                        print('100004:', data)

                    # # 验证有没有登录成功
                    # # 个人中心链接
                    # url = 'https://kyfw.12306.cn/otn/index/initMy12306'
                    # response = session.get(url, headers=headers)
                    # if response.status_code == 200:
                    #     html = response.text
                    #     print(html)
            else:
                print('验证码校验失败，正在重新发送...')
                time.sleep(1)
                self.download_captcha_picture()
                self.login()


# def main():
#     login = Login()
#     login.download_captcha_picture()
#     login.login()
#
#
# if __name__ == '__main__':
#     main()
