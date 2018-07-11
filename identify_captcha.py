# !/usr/bin/env python
# -*- coding:utf-8 -*-
# author: wanjie time:2018/6/30 0030

import io
import numpy as np
import tensorflow as tf
from PIL import Image
from aip import AipOcr
# 自己定义的文件
from setting import english_to_chinese

APP_ID = '11050413'
API_KEY = '2icNR8CBBO1jamKrRvsivK1N'
SECRET_KEY = '0xEc7dGonTPRTMWV23swC6mbomRWv4tL'


class IdentifyCaptchaPicture(object):
    """识别验证码类"""
    def __init__(self):
        self.output_graph = 'output_graph.pb'
        self.output_labels = 'output_labels.txt'
        self.captcha_picture = 'captcha_picture.jpg'
        self.english_to_chinese = english_to_chinese
        self.id_to_something = self._id_to_something()
        self.client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

    # 读取 output_labels.txt 文件
    def _id_to_something(self):
        id_to_something = {}
        with open(self.output_labels, 'r') as f:
            lines = f.readlines()
            for index, line in enumerate(lines):
                line = line.strip()
                id_to_something[index] = line
        return id_to_something

    # 根据 id 找到 分类
    def _find_string_by_id(self, id_test):
        if id_test in self.id_to_something:
            return self.id_to_something[id_test]
        else:
            return None

    # 切割验证码
    def _cut_captcha_picture(self):
        image = Image.open(self.captcha_picture)

        one = image.crop((5, 41, 71, 107))
        two = image.crop((77, 41, 143, 107))
        three = image.crop((149, 41, 215, 107))
        four = image.crop((221, 41, 287, 107))
        five = image.crop((5, 113, 71, 179))
        six = image.crop((77, 113, 143, 179))
        seven = image.crop((149, 113, 215, 179))
        eight = image.crop((221, 113, 287, 179))
        all_picture_after_cut = [one, two, three, four, five, six, seven, eight]
        return all_picture_after_cut

    # 识别验证码的文字
    def _identify_captcha_picture_text(self):
        image = Image.open(self.captcha_picture)

        text = image.crop((124, 0, 287, 26))
        image_byte_array = io.BytesIO()
        text.save(image_byte_array, format='PNG')
        text = image_byte_array.getvalue()
        text = self.client.basicGeneral(text)['words_result']
        try:
            return text[0]['words']
        except(IndexError, Exception):
            return ''

    # 识别验证码
    def identify_captcha_picture(self):
        all_picture_after_cut = self._cut_captcha_picture()
        with tf.gfile.FastGFile(self.output_graph, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            tf.import_graph_def(graph_def, name='')

        with tf.Session() as sess:
            text = self._identify_captcha_picture_text()
            print('识别出的文字是：', text)
            correct_choose = []
            softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
            # 遍历每张切割好的图片
            for index, one_picture in enumerate(all_picture_after_cut):
                image_byte_array = io.BytesIO()
                one_picture.save(image_byte_array, format='PNG')
                one_picture = image_byte_array.getvalue()
                prediction = sess.run(softmax_tensor, feed_dict={'DecodeJpeg/contents:0': one_picture})
                prediction = np.squeeze(prediction)

                # 找到概率最大的分类
                top_1 = np.argmax(prediction, axis=0)
                something = self._find_string_by_id(top_1)
                something_chinese = self.english_to_chinese[something]
                # print('100001:', text)
                for one_word in something_chinese:
                    if one_word in text:
                        correct_choose.append(str(index+1))
                        break
                print('%s %0.5f%%' % (something_chinese, prediction[top_1] * 100))
                # print('\n-----------------------------------------------\n')
            # print('correct_choose:', correct_choose)
            return correct_choose


# def main():
#     identify_picture = IdentifyCaptchaPicture()
#     identify_picture.identify_captcha_picture()
#
#
# if __name__ == '__main__':
#     main()
