# !/usr/bin/env python
# -*- coding:utf-8 -*-
# author: wanjie time:2018/6/26 0026

import json
import requests
from urllib.parse import urlencode
from json.decoder import JSONDecodeError
# 自己定义的文件
from login import session
from setting import *


class CheckTicket(object):
    """余票监控类"""
    def __init__(self, train_date, from_station, to_station):
        # 用来记录列车序号
        self.order = 0
        # 用来记录车票类别
        self.category = ''
        # 车站代号
        self.station_to_code = get_station()
        self.train_date = train_date
        self.from_station = from_station
        self.to_station = to_station

    # 获取索引页信息，获取每辆车的信息
    def _get_page_index(self, from_station_no, to_station_no):
        url = 'https://kyfw.12306.cn/otn/leftTicket/query?'
        data = {
            'leftTicketDTO.train_date': self.train_date,
            'leftTicketDTO.from_station': from_station_no,
            'leftTicketDTO.to_station': to_station_no,
            'purpose_codes': 'ADULT'
        }
        url = url + urlencode(data)
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            html = response.text
            data = json.loads(html)
            if data and 'data' in data.keys():
                for item in data['data']['result']:
                    yield item

    # 获取车票价格
    def _get_ticket_price(self, from_station_no, seat_types, to_station_no, train_no):
        url = 'https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice?'
        data = {
            'train_no': train_no,
            'from_station_no': from_station_no,
            'to_station_no': to_station_no,
            'seat_types': seat_types,
            'train_date': self.train_date
        }
        # print('请求参数：', data)
        url = url + urlencode(data)
        # print(url)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            html = response.text
            data = json.loads(html)
            if data and 'data' in data.keys():
                price_dict = data['data']
                return price_dict
            # print('json串解析后的结果：', data)

    # 解析车票价格
    def _parse_ticket_price(self, from_station_no, seat_types, to_station_no, train_no):
        try:
            price_dict = self._get_ticket_price(from_station_no, seat_types, to_station_no, train_no)
        except(JSONDecodeError, Exception):
            pass
        else:
            seat_to_price = {}
            for key in price_dict.keys():
                if key in mark_to_seat.keys():
                    seat_to_price[mark_to_seat[key]] = price_dict[key]
            return seat_to_price
        return '本次获取价格失败！'

    # 解析索引页信息
    def parse_page_index(self, number):
        from_station_no = self.station_to_code[self.from_station]
        to_station_no = self.station_to_code[self.to_station]
        # 用来保存所有有票的车辆
        all_train_own_ticket = []
        index = 0
        for item in self._get_page_index(from_station_no, to_station_no):
            result_list = str(item).split('|')
            if result_list[0] != '' and result_list[0] != 'null':
                if number == 0:
                    information = '序号：%d, 车次：%s，发车时间：%s，到达时间：%s，历时：%s，商务特等座：%s，一等座：%s，' \
                                  '二等座：%s，软卧：%s，硬卧：%s，硬座：%s，无座：%s'\
                                  % (index, result_list[3], result_list[8], result_list[9], result_list[10],
                                     result_list[32], result_list[31], result_list[30], result_list[23],
                                     result_list[28], result_list[29], result_list[26])
                    print(information)
                    # print('\n----------------------------------------------\n')
                all_train_own_ticket.append(result_list)
                index += 1
        while True:
            if number == 0:
                # 查询价格
                while True:
                    i = input('请输入您想获取车票价格的车次的序号（N/n表示获取结束）：')
                    try:
                        if i == 'n' or i == 'N':
                            break
                        if -1 < int(i) < index:
                            from_station_no = all_train_own_ticket[int(i)][16]
                            seat_types = all_train_own_ticket[int(i)][35]
                            to_station_no = all_train_own_ticket[int(i)][17]
                            train_no = all_train_own_ticket[int(i)][2]
                            # 获取车票价格
                            price_dict = self._parse_ticket_price(from_station_no, seat_types, to_station_no,
                                                                  train_no)
                            print(price_dict)
                    except(ValueError, Exception):
                        print('输入不合法，请重新输入！！')

                # 选择车票
                while True:
                    order = input('您想购买那一辆车的车票，输入前面的序号：')
                    try:
                        if 0 <= int(order) <= index:
                            order = int(order)
                            break
                    except(ValueError, Exception):
                        print('输入不合法请重新输入')
                print('1代表商务特等座，2代表一等座，3代表二等座，4代表软卧，5代表硬卧，6代表硬座，不支持抢无座车票')
                while True:
                    category = input('您想购买该车辆的什么票：')
                    if category in [str(i) for i in range(1, 8)]:
                        break
                    else:
                        print('输入不合法请重新输入')
                category = int_to_seat[category]
                self.order = order
                self.category = category
                # 检查是否有票
                check_list = all_train_own_ticket[order]
                if check_list[data_to_int[category]] == '':
                    print('该车次没有售卖%s票，请重新选择！！' % category)
                else:
                    print('开始抢票！！')
                    break
            else:
                order = self.order
                category = self.category
                break
        # print('order:', order)
        # print('category:', category)
        remainder = all_train_own_ticket[order][data_to_int[category]]
        print('10005:', all_train_own_ticket[order])
        print(all_train_own_ticket[order][0], all_train_own_ticket[order][15], category, remainder)
        # for i, item in enumerate(all_train_own_ticket[order]):
        #     print(i, item)
        return all_train_own_ticket[order][0], all_train_own_ticket[order][15], category, remainder


# def main():
#     train_date = '2018-07-20'
#     from_station = '杭州'
#     to_station = '六安'
#     # category = '硬座'
#     check_ticket = CheckTicket()
#     secret_str, train_location, category = check_ticket.parse_page_index(train_date, from_station, to_station)
#     print(secret_str)
#     print(train_location)
#     print(category)
# 
# 
# if __name__ == '__main__':
#     main()
