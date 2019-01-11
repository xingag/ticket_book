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
@time: 2018/11/11
@description：抢票【实用】
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import time
from datetime import datetime
import configparser
from utils import get_current_date


# 使用selenium登录的时候，不会保留之前保存的cookie信息，授权的信息都不存在
# 由于12306验证码的复杂性，这里手动输入验证码

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
        # self.person_center_url = 'https://kyfw.12306.cn/otn/index/initMy12306'

        # 个人中心url【改版后】
        self.person_center_url = 'https://kyfw.12306.cn/otn/view/index.html'

        # 查询票的url
        self.search_ticket_url = 'https://kyfw.12306.cn/otn/leftTicket/init'

        # 选择乘客的url
        self.choose_passenger_url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'

        # 刷票时间间隔【默认为：5秒】
        self.refresh_interval = 1

    def wait_input(self):

        self.from_station = input('请输入始发地：')

        self.to_station = input('请输入目的地：')

        # 出发时间，时间格式必须是：yyyy-MM-dd
        self.depart_time = input('出发时间【格式必须是 yyyy-MM-dd 】：')

        # 乘客【们】
        self.passengers = input('乘客姓名（如果有多个乘客，用逗号隔开）：').split(",")

        # 车次类型
        self.train_types = input('请选择车次类型【G：高铁：D：动车；Z：直达； T：特快； K：快速；L：其他(包含临客L) / 多种车次用逗号分开】：').split(",")

        # 座位类型【选择一种车次】
        self.seat_type = input('请输入座位类型【0：商务座；10：一等座；11：二等座；20：高级软卧；21：软卧；22：动卧；23：硬卧；30：软座；31：硬座；4：无座；5：其他】')

        # 定时刷票【0：立即刷票；14：30：00 具体时间点开始刷票】
        self.timer = input('抢票时间【0：立即；HH：mm：ss：具体的时间开始刷票】')

    def _login(self):
        """
        登录
        :return: 内部方法，不想被外部调用；但是依旧是可以被外部调用的
        """

        # 1.打开登录页面
        self.driver.get(self.login_url)

        # 2.读取配置文件中的用户名和密码
        config = configparser.ConfigParser()
        config.read('user.cfg')
        username = config.get('user', 'username')
        password = config.get('user', 'password')

        # 2.用户名、密码输入框、登录按钮
        usernameInput = self.driver.find_element_by_id('username')
        passwordInput = self.driver.find_element_by_id('password')
        loginBtn = self.driver.find_element_by_id('loginSub')

        # 3.写入数据到输入框中
        usernameInput.clear()
        passwordInput.clear()
        usernameInput.send_keys(username)
        passwordInput.send_keys(password)

        # 4.手动输入验证码
        # 10秒点击一次登录按钮
        # try:
        while loginBtn:
            time.sleep(10)

            # 循环执行，这里可能导致loginBtn为空
            loginBtn = self.driver.find_element_by_id('loginSub')

            if loginBtn:
                loginBtn.click()
            else:
                print('退出循环，当前url：%s' % (self.driver.current_url))
                break

        # except Exception as e:
        #     print('产生异常了,当前url：' + self.driver.current_url)
        #     print(e)

        # 5.显示等待完全加载出【个人中心页面】
        WebDriverWait(self.driver, 1000).until(
            EC.url_to_be(self.person_center_url))

        # print('登录成功，到个人中心页面')

    def _search_proc(self):
        """定时抢票"""

        # 1.跳转到查票的界面
        self.driver.get(self.search_ticket_url)

        # 2.选择单程
        self.driver.find_element_by_xpath('//label[@for="dc"]').click()
        # 之所以要設置一個等待，是因為我在測試的時候發現，如果操作過快，在最後點擊搜索的時候，會卡在搜索狀態，一直顯示正在搜索。。。。。。
        time.sleep(1)

        # 3.出发地输入框、目的地输入框、出发时间输入框
        fromStationInput = self.driver.find_element_by_id("fromStationText")
        toStationInput = self.driver.find_element_by_id("toStationText")
        departTimeInput = self.driver.find_element_by_id("train_date")

        # 4.1 选择出发地
        # 点击，输入出发地，列表中选择目的城市
        ActionChains(self.driver).click(fromStationInput).send_keys(self.from_station).perform()
        try:
            list_0 = self.driver.find_elements_by_xpath('//div[@id="panel_cities"]//div/span[1]')
            for vb in list_0:
                if vb.text == self.from_station:
                    time.sleep(1)
                    vb.click()
                    break
                else:
                    print('过滤掉这个城市')
        except:
            pass
        time.sleep(1)

        # 4.2 选择目的地
        ActionChains(self.driver).click(toStationInput).send_keys(self.to_station).perform()
        try:
            list_01 = self.driver.find_elements_by_xpath('//div[@id="panel_cities"]//div/span[1]')
            for vb2 in list_01:
                if vb2.text == self.to_station:
                    time.sleep(1)
                    vb2.click()
                    break
                else:
                    print('过滤掉这个城市')
        except:
            pass
        time.sleep(1)

        # 5.选择出发时间
        js = "document.getElementById('train_date').removeAttribute('readonly')"  # del train_date readonly property
        self.driver.execute_script(js)
        departTimeInput.clear()

        # 出发时间：默认是今天
        if not self.depart_time:
            self.depart_time = get_current_date()

        ActionChains(self.driver).click(departTimeInput).send_keys(self.depart_time).perform()
        time.sleep(1)

        # 6.显示等待【查询按钮】可以被点击
        WebDriverWait(self.driver, 1000).until(EC.element_to_be_clickable((By.ID, "query_ticket")))

        # 7.定时抢票
        # 7.1 立即开始抢票
        if self.timer == '0' or not self.timer:
            return

        # 7.2 定时抢票，等待
        # 假设 15:00:00 开始放票，提前 5 分钟开始刷票
        else:
            timer_h = self.timer.split(':')[0]
            timer_m = self.timer.split(':')[1]
            timer_s = self.timer.split(':')[2]
            while True:
                # 当前时间
                current_time = time.localtime()
                print(time.localtime())
                if (current_time.tm_hour == int(timer_h) and current_time.tm_min >= int(
                        timer_m) and current_time.tm_sec >= int(timer_s)):
                    # if (current_time.tm_hour == 14 and current_time.tm_min >= 55 and current_time.tm_sec >= 0):
                    print(u'开始刷票')
                    break
                else:
                    # 程序等待中，每30秒打印一下时间
                    if current_time.tm_sec % 30 == 0:
                        print('等待中,当前时间：%s' % (time.strftime('%H:%M:%S', current_time)))

                    print('还未到时间，休眠1秒钟')
                    time.sleep(1)

                print('==' * 40)

    def _order_ticket(self):
        """
        订票
        :return:
        """

        # 查询次数
        query_times = 0
        # 当前时间
        time_begin = time.time()

        # 在 python 中，for … else 表示这样的意思，for 中的语句和普通的没有区别，else 中的语句会在循环正常执行完（即 for 不是通过 break 跳出而中断的）的情况下执行，while … else 也是一样。
        while True:

            print('再查询一次')

            # 退出外层循环
            break_outer_loop = False

            # 4.点击【查询按钮】
            self.driver.find_element_by_id("query_ticket").click()

            # 5.等待票信息的出现【注意：这里必须等待】
            # queryLeftTable tbody元素下有元素的时候代表有【车次信息】可以供预定
            WebDriverWait(self.driver, 1000).until(
                EC.presence_of_element_located((By.XPATH, ".//tbody[@id='queryLeftTable']/tr")))

            # 6. 选择车次的种类【模拟点击】
            train_type_dict = {
                'G': '//input[@name="cc_type" and @value="G"]',  # 高铁
                'D': '//input[@name="cc_type" and @value="D"]',  # 动车
                'Z': '//input[@name="cc_type" and @value="Z"]',  # 直达
                'T': '//input[@name="cc_type" and @value="T"]',  # 特快
                'K': '//input[@name="cc_type" and @value="K"]',  # 快速
                'L': '//input[@name="cc_type" and @value="QT"]',  # 其他【包含临客】
            }

            # 选中车次类型
            # 点击对应的车次进行筛选；否则默认选择【高铁】
            for train_type in self.train_types:
                if train_type in train_type_dict.keys():
                    self.driver.find_element_by_xpath(train_type_dict[train_type]).click()

            # 7.获取过滤后的车次列表
            trains = self._get_trains()

            # print(trains)
            # 某个元素没有某个属性 - not（）函数
            # // tbody[ @ id = 'queryLeftTable'] / tr[not (@ style='display:none;')]

            # 8.过滤掉没有用的数据
            # 【拥有 datatran 属性的 tr 标签】【过滤不需要的信息：存储车次信息的tr标签】
            tr_lists = self.driver.find_elements_by_xpath(".//tbody[@id='queryLeftTable']/tr[not(@datatran)]")

            # 9.遍历每一辆火车的车票数据
            for key, tr_element in enumerate(tr_lists):

                # 9.0 是否是最后一个车次
                is_last_train = key == len(tr_lists) - 1

                # 9.1 获取车次名称
                train_number = tr_element.find_element_by_class_name('number').text

                # 9.2 获取车次座次的数目【11 种座位】
                # 9.2.1 商务座、特等座的数目
                special_seat_td_content = tr_element.find_element_by_xpath('.//td[2]').text
                # 9.2.2 一等座
                first_seat_td_content = tr_element.find_element_by_xpath('.//td[3]').text
                # 9.2.3 二等座：第 4 个 td 标签里面的文本内容
                second_seat_td_content = tr_element.find_element_by_xpath('.//td[4]').text
                # 9.2.4 高级软卧
                high_soft_wo_seat_td_content = tr_element.find_element_by_xpath('.//td[5]').text
                # 9.2.5 软卧
                soft_wo_seat_td_content = tr_element.find_element_by_xpath('.//td[6]').text
                # 9.2.6 动卧
                dong_wo_seat_td_content = tr_element.find_element_by_xpath('.//td[7]').text
                # 9.2.7 硬卧
                ying_wo_seat_td_content = tr_element.find_element_by_xpath('.//td[8]').text
                # 9.2.8 软座
                soft_seat_td_content = tr_element.find_element_by_xpath('.//td[9]').text
                # 9.2.9 硬座
                ying_seat_td_content = tr_element.find_element_by_xpath('.//td[10]').text
                # 9.2.10 无座
                no_seat_td_content = tr_element.find_element_by_xpath('.//td[11]').text
                # 9.2.11 其他
                other_seat_td_content = tr_element.find_element_by_xpath('.//td[12]').text

                # 0：商务座、特等座
                # 10：一等座； 11：二等座
                # 20：高级软卧； 21：软卧； 22：动卧； 23：硬卧
                # 30：软座； 31：硬座
                # 4：无座
                # 5：其他

                nums_seat = {
                    '0': special_seat_td_content,
                    '10': first_seat_td_content,
                    '11': second_seat_td_content,
                    '20': high_soft_wo_seat_td_content,
                    '21': soft_wo_seat_td_content,
                    '22': dong_wo_seat_td_content,
                    '23': ying_wo_seat_td_content,
                    '30': soft_seat_td_content,
                    '31': ying_seat_td_content,
                    '4': no_seat_td_content,
                    '5': other_seat_td_content
                }

                # 9.3 选择的座位类型【默认是：高铁二等座】
                choose_seat_content = nums_seat[
                    self.seat_type] if self.seat_type in nums_seat.keys() else second_seat_td_content

                # 9.4 如果【有】或者【数字】代表有票
                if choose_seat_content == '有' or choose_seat_content.isdigit():

                    # 9.4.1 找到预定按钮
                    orderBtn = tr_element.find_element_by_class_name('btn72')

                    # 7.4.2 点击预定按钮
                    orderBtn.click()

                    if self._sure_ticket():
                        print('成功抢到一张车票:%s' % (train_number))
                        # 退出整个循环，包含外层循环
                        break_outer_loop = True
                        break
                else:
                    # info = "所有的车次都没有票" if is_last_train else train_number + "暂时没有足够的票"
                    # print(info)
                    if is_last_train:
                        print('MD，Fuck！所有列车的票都被抢光了！1 秒后重新刷票~')
                        # 正常循环结束，执行for...else语句
                    else:
                        print(train_number + "暂时没有足够的票")
                        # 退出for循环，继续执行while循环
            else:
                # 刷新时间间隔
                time.sleep(self.refresh_interval)

            # 退出外层循环
            if break_outer_loop:
                break

        else:
            print('此处不会调用')
            pass

    def _sure_ticket(self):
        """
        选择乘客，确定订单
        :return:
        """
        # 9.4.3 等待来到【选择乘客】的界面
        WebDriverWait(self.driver, 1000).until(EC.url_to_be(self.choose_passenger_url))

        # 9.4.4 等待【所有乘客】信息被加载进来
        WebDriverWait(self.driver, 1000).until(
            EC.presence_of_element_located((By.XPATH, './/ul[@id="normal_passenger_id"]/li')))

        # 9.4.5 获取所有乘客的Label标签
        passenger_labels = self.driver.find_elements_by_xpath('.//ul[@id="normal_passenger_id"]/li/label')

        # 9.4.6 选中乘客【指定点击事件】
        for passenger_label in passenger_labels:
            name = passenger_label.text
            if name in self.passengers:
                # 选中这个乘客
                passenger_label.click()

        # 9.4.7 获取提交订单的按钮【执行点击操作】
        submitBtn = self.driver.find_element_by_id("submitOrder_id")
        submitBtn.click()

        # 注意：【确认对话框】需要时间加载，这里需要显示等待
        # 对话框出现【显示等待】
        WebDriverWait(self.driver, 1000).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'dhtmlx_wins_body_outer')))

        # 确认按钮出现【显示等待】
        WebDriverWait(self.driver, 1000).until(
            EC.presence_of_element_located((By.ID, 'qr_submit_id')))

        # 9.4.8 获取确定按钮，指定点击事件
        confirmBtn = self.driver.find_element_by_id('qr_submit_id')

        # 9.4.9 确定订票
        while True:
            try:
                # self.driver.switch_to.frame(self.driver.find_element_by_xpath('//*[@id="body_id"]/iframe[2]'))

                # 多次点击
                confirmBtn.click()
                while confirmBtn:
                    confirmBtn.click()

                time.sleep(3)
                return True
            except Exception as e:
                print(u'产生异常了')
                print(e)
                time.sleep(3)
                return False

        # confirmBtn.click()
        #
        # # 9.4.9 有可能此时【确定订票按钮】此时还不能进行点击，所有循环点击
        # try:
        #     while confirmBtn:
        #         confirmBtn.click()
        #
        #     return True
        # except:
        #     return True

    def _get_trains(self):
        """
        获取查询列表中所有车次信息
        :return:
        """
        # 车次
        che_ci = []

        # 出发站点
        start_c = []

        # 目的地站点
        end_c = []

        # 出发时间
        start_t = []

        # 到达时间
        end_t = []

        # 路程时间
        total_time = []

        # 商务座、特等座
        seat_nums_vip = []

        # 一等座
        seat_nums_first = []

        # 二等座
        seat_nums_second = []

        # 高级软卧
        seat_nums_lie_advance_soft = []

        # 软卧
        seat_nums_lie_soft = []

        # 动卧
        seat_nums_lie_dong = []

        # 硬卧
        seat_nums_lie_ying = []

        # 软座
        seat_nums_norm_soft = []

        # 硬座
        seat_nums_norm = []

        # 无座
        seat_nums_no = []

        # 其他
        seat_nums_other = []

        # 注意：这里要过滤掉【已经停运】的车次
        # 不包含某个属性
        # che_ci_elements = self.driver.find_elements_by_xpath(
        #     '//tbody[@id="queryLeftTable"]//tr[not(@datatran)]')

        che_ci_elements = self.driver.find_elements_by_xpath(
            '//tr[@style="display:none;"]')

        for che_ci_element in che_ci_elements:
            che_ci.append(che_ci_element.get_attribute('datatran'))

        print('==' * 60)
        print(che_ci)
        print('==' * 60)

        start_c_elements = self.driver.find_elements_by_xpath('//strong[@class="start-s"]')
        for start_c_element in start_c_elements:
            start_c.append(start_c_element.text)

        end_c_elements = self.driver.find_elements_by_xpath('//div[@class="cdz"]/strong[2]')
        for end_c_element in end_c_elements:
            end_c.append(end_c_element.text)

        start_t_elements = self.driver.find_elements_by_xpath('//div[@class="cds"]/strong[1]')
        for start_t_element in start_t_elements:
            start_t.append(start_t_element.text)

        end_t_elements = self.driver.find_elements_by_xpath('//div[@class="cds"]/strong[2]')
        for end_t_element in end_t_elements:
            end_t.append(end_t_element.text)

        total_time_elements1 = self.driver.find_elements_by_xpath('//div[@class="ls"]/strong[1]')
        total_time_elements2 = self.driver.find_elements_by_xpath('//div[@class="ls"]/span[1]')

        for index, value in enumerate(total_time_elements1):
            if len(total_time_elements2) > index:
                total_time.append('历时：%s,%s' % (value.text, total_time_elements2[index].text))
            else:
                total_time.append('历时：格式未知')
        # 组装成一个新的列表中
        trains = []
        for temp in zip(che_ci, start_c, end_c, start_t, end_t, total_time):
            train_name, start_position, end_position, start_time, end_time, desc = temp
            trains.append({
                'train_name': train_name,
                'start_position': start_position,
                'end_position': end_position,
                'start_time': start_time,
                'end_time': end_time,
                'desc': desc,
            })

        return trains

    def run(self):
        # 1.输入必要的信息
        self.wait_input()

        # 2.登录【手动登录】
        self._login()

        # 4.刷票
        self._search_proc()

        # 5.订票【个人中心 - 选择车次界面】
        # self._order_ticket()


if __name__ == '__main__':
    spider = QiangPiaoSpider()

    # 开始抢票
    spider.run()
