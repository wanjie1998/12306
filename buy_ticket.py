# !/usr/bin/env python
# -*- coding:utf-8 -*-
# author: wanjie time:2018/6/25 0025

import re
import json
from urllib.parse import unquote
# 自己定义的文件
from login import session
from setting import *


class BuyTicket(object):
    """购票类"""
    def __init__(self, train_date, from_station, to_station):
        self.train_date = train_date
        self.from_station = from_station
        self.to_station = to_station

    # 下单的第一个请求
    @staticmethod
    def buy_ticket_one():
        url = 'https://kyfw.12306.cn/otn/login/checkUser'
        data = {
            '_json_att': ''
        }
        response = session.post(url, headers=headers, data=data)
        if response.status_code == 200:
            html = response.text
            data = json.loads(html)
            print('100006:', data)

    # 下单的第二个请求
    def buy_ticket_two(self, secret_str):
        url = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
        data = {
            'back_train_date': '2018-06-25',
            'purpose_codes': 'ADULT',
            'query_from_station_name': self.from_station,
            'query_to_station_name': self.to_station,
            'secretStr': unquote(secret_str),
            'tour_flag': 'dc',
            'train_date': self.train_date,
            'undefined': ''
        }
        response = session.post(url, headers=headers, data=data)
        if response.status_code == 200:
            html = response.text
            data = json.loads(html)
            print('100007:', data)
            if '未处理的订单' in str(data['messages']):
                print('您还有未处理的订单！！，请您先处理完未完成的订单在进行抢票！！')
                return None
            if data['status'] is True:
                return False

    # 下单的第三个请求（这个请求比较特殊，返回值中有接下来请求的必要参数）
    @staticmethod
    def buy_ticket_three():
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        data = {
            '_json_att': ''
        }
        response = session.post(url, headers=headers, data=data)
        if response.status_code == 200:
            html = response.text
            # print(html)
            result1 = re.findall("globalRepeatSubmitToken = '(.*?)';", html)[0]
            result2 = re.findall("'key_check_isChange':'(.*?)',", html)[0]
            result3 = re.findall("'leftTicketStr':'(.*?)',", html)[0]
            return result1, result2, result3

    # 下单的第四个请求
    @staticmethod
    def buy_ticket_four(repeat_submit_token):
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
        data = {
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': repeat_submit_token
        }
        response = session.post(url, headers=headers, data=data)
        if response.status_code == 200:
            html = response.text
            data = json.loads(html)
            print('100008:', data)
            if data and 'data' in data.keys():
                normal_passengers = data['data']['normal_passengers'][0]
                return normal_passengers['passenger_name'], normal_passengers['passenger_id_no'], \
                    normal_passengers['passenger_type'], normal_passengers['mobile_no']

    # 下单的第五个请求
    @staticmethod
    def buy_ticket_five(repeat_submit_token, name, passenger_type, id_num, phone_num, category):
        # # 验证有没有登录成功
        # # 个人中心链接
        # url = 'https://kyfw.12306.cn/otn/index/initMy12306'
        # response = session.get(url, headers=headers)
        # if response.status_code == 200:
        #     html = response.text
        #     print(html)
        category = seat_to_int[category]
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
        data = {
            '_json_att': '',
            'bed_level_order_num': '000000000000000000000000000000',
            'cancel_flag': '2',
            'oldPassengerStr': '{},1,{},3_'.format(name, id_num),
            'passengerTicketStr': '{},0,{},{},1,{},{},N'.format(category, passenger_type, name, id_num, phone_num),
            'randCode': '',
            'REPEAT_SUBMIT_TOKEN': repeat_submit_token,
            'tour_flag': 'dc',
            'whatsSelect': '1'
        }
        # print(data)
        response = session.post(url, headers=headers, data=data)
        # print(response)
        if response.status_code == 200:
            html = response.text
            # print(html)
            data = json.loads(html)
            print('100009:', data)
            if data['data']['submitStatus'] is True:
                return False

    # 下单的第六个请求 category表示座位类别 比如硬座，硬卧等
    @staticmethod
    def buy_ticket_six(train_location, key_check_is_change, left_ticket_str, repeat_submit_token,
                       name, id_num, phone_num, category):
        category = seat_to_int[category]
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
        data = {
            '_json_att': '',
            'choose_seats': '',
            'dwAll': 'N',
            'key_check_isChange': key_check_is_change,
            'leftTicketStr': left_ticket_str,
            'oldPassengerStr': '{},1,{},3_'.format(name, id_num),
            'passengerTicketStr': '{},0,1,{},1,{},{},N'.format(category, name, id_num, phone_num),
            'purpose_codes': '00',
            'randCode': '',
            'REPEAT_SUBMIT_TOKEN': repeat_submit_token,
            'roomType': '00',
            'seatDetailType': '000',
            'train_location': train_location,
            'whatsSelect': '1'
        }
        response = session.post(url, headers=headers, data=data)
        if response.status_code == 200:
            html = response.text
            data = json.loads(html)
            print('1000010:', data)
