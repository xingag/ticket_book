#!/usr/bin/env python  
# encoding: utf-8  

""" 
@version: v1.0 
@author: xag 
@license: Apache Licence  
@contact: xinganguo@gmail.com 
@site: http://www.xingag.top 
@software: PyCharm 
@file: ticket_book.py
@time: 2018/10/22 18:54 
@description：12306抢票
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


# 使用selenium登录的时候，不会保留之前保存的cookie信息，授权的信息都不存在


class QiangPiaoSpider(object):
    """
    抢票类
    """

    def __init__(self):
        self.driver_path = "/usr/local/bin/chromedriver"
        self.driver = webdriver.Chrome(executable_path=self.driver_path)

        # 登录url
        self.login_url = 'https://kyfw.12306.cn/otn/login/init'

        # 个人中心url
        self.person_center_url = 'https://kyfw.12306.cn/otn/index/initMy12306'

        # 查询票的url
        self.search_ticket_url = 'https://kyfw.12306.cn/otn/leftTicket/init'

        # 选择乘客的url
        self.choose_passenger_url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'

    def wait_input(self):
        # 始发地
        self.from_station = input("出发地：")

        # 目的地
        self.to_station = input('目的地：')

        # 出发时间，时间格式必须是：yyyy-MM-dd
        self.depart_time = input('出发时间：')

        # 乘客【们】
        self.passengers = input('乘客姓名（如果有多个乘客，用逗号隔开）：').split(",")

        # 车次【们】
        self.trains = input('车次（如果有多个车次，用逗号隔开）：')

    def _login(self):
        """
        登录
        :return: 内部方法，不想被外部调用；但是依旧是可以被外部调用的
        """

        # 1.打开登录界面
        self.driver.get(self.login_url)

        # 2.手动登录
        # 等待用户输入用户名和密码、验证码
        # EC_url_to_be 当前的url是否相同
        WebDriverWait(self.driver, 1000).until(
            EC.url_to_be(self.person_center_url))
        print('登录成功')

    def _order_ticket(self):
        """
        订票
        :return:
        """
        # 1.跳转到查票的界面
        self.driver.get(self.search_ticket_url)
        print('到查票界面')

        # 2.等待出发地、目的地、出发日期是否输入正确
        # 注意：input标签：开放标签，非闭合标签；利用input中的value值来判断是否一致，不能使用闭合标签中的text来判断【EC.text_to_be_present_in_element】
        WebDriverWait(self.driver, 1000).until(
            EC.text_to_be_present_in_element_value((By.ID, "fromStationText"), self.from_station))

        WebDriverWait(self.driver, 1000).until(
            EC.text_to_be_present_in_element_value((By.ID, "toStationText"), self.to_station))

        WebDriverWait(self.driver, 1000).until(
            EC.text_to_be_present_in_element_value((By.ID, "train_date"), self.depart_time))

        # 3.等待查询按钮是否可以点击
        WebDriverWait(self.driver, 1000).until(EC.element_to_be_clickable((By.ID, "query_ticket")))

        # 4.如果按钮可以被点击，就执行点击事件【点击查询按钮】
        self.driver.find_element_by_id("query_ticket").click()

        # 5.等待票信息的出现【注意：这里必须等待】
        # queryLeftTable tbody元素下有元素的时候代表有【车次信息】可以供预定
        WebDriverWait(self.driver, 1000).until(
            EC.presence_of_element_located((By.XPATH, ".//tbody[@id='queryLeftTable']/tr")))

        # 6.过滤掉所有【拥有 datatran 属性的 tr 标签】【过滤不需要的信息：存储车次信息的tr标签】
        tr_lists = self.driver.find_elements_by_xpath(".//tbody[@id='queryLeftTable']/tr[not(@datatran)]")

        # 7.遍历列表
        for tr_element in tr_lists:
            # 7.1 获取车次名称
            train_number = tr_element.find_element_by_class_name('number').text

            print('当前车次%s' % train_number)

            # 7.2 如果车次符合所选择的车次
            if train_number in self.trains:
                # 7.2.1 二等座：第 4 个 td 标签里面的文本内容
                second_seat_td_content = tr_element.find_element_by_xpath('.//td[4]').text

                # 7.2.2 如果【有】或者【数字】代表有票
                if second_seat_td_content == '有' or second_seat_td_content.isdigit:
                    print(train_number + "有票")

                    # 7.2.3 找到预定按钮
                    orderBtn = tr_element.find_element_by_class_name('btn72')

                    # 7.2.4 点击预定按钮
                    orderBtn.click()

                    # 7.2.5 等待来到【选择乘客】的界面
                    WebDriverWait(self.driver, 1000).until(EC.url_to_be(self.choose_passenger_url))
                    print('到达选择乘客的界面')

                    # 7.2.6 等待【所有乘客】信息被加载进来
                    WebDriverWait(self.driver, 1000).until(
                        EC.presence_of_element_located((By.XPATH, './/ul[@id="normal_passenger_id"]/li')))

                    # 7.2.7 获取所有乘客的Label标签
                    passenger_labels = self.driver.find_elements_by_xpath('.//ul[@id="normal_passenger_id"]/li/label')

                    # 7.2.8 选中乘客
                    for passenger_label in passenger_labels:
                        name = passenger_label.text
                        if name in self.passengers:
                            # 选中这个乘客
                            passenger_label.click()

                    # 7.2.9 获取【提交订单的按钮】，执行点击操作
                    submitBtn = self.driver.find_element_by_id("submitOrder_id")
                    submitBtn.click()

                    # 注意：确认对话框需要时间加载，这里需要显示等待
                    # 对话框出现【显示等待】
                    WebDriverWait(self.driver, 1000).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'dhtmlx_wins_body_outer')))

                    # 确认按钮出现【显示等待】
                    WebDriverWait(self.driver, 1000).until(
                        EC.presence_of_element_located((By.ID, 'qr_submit_id')))

                    confirmBtn = self.driver.find_element_by_id('qr_submit_id')

                    # 确定订票
                    confirmBtn.click()

                    # 有可能此时【确定订票按钮】此时还不能进行点击，所有循环点击
                    while confirmBtn:
                        confirmBtn.click()
                        confirmBtn = self.driver.find_element_by_id('qr_submit_id')

                    return

                else:
                    print(train_number + "无票")

            else:
                print("没有选择这个车次：" + train_number)

            print("==" * 40)

    def run(self):
        # 1.输入必要的信息
        self.wait_input()

        # 2.登录【手动登录】
        self._login()

        # 3.订票【个人中心 - 选择车次界面 - 选择乘客】
        self._order_ticket()


if __name__ == '__main__':
    spider = QiangPiaoSpider()

    # 开始抢票
    spider.run()
