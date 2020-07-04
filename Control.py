from windows import *
from wechat import *
import threading
import re
import time
import ctypes
import inspect
import requests
from lxml import etree
from playsound import PlaySound	#



def _async_raise(thread):
    """
    释放进程
    :param thread: 进程对象
    :param exctype:
    :return:
    """
    try:
        tid = thread.ident
        # tid = ctypes.c_long(tid)
        exctype = SystemExit
        """raises the exception, performs cleanup if needed"""
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")
    except Exception as err:
        print(err)

class Control(object):

    def __init__(self, win, data_lock):
        self.__system = "windows"

        if self.__system == "windows":
            self.player = PlaySound()

        self.wechat_login_flag = False
        self.wc = Wechat(win.system_init["wechat_alarm"])
        self.win_close = False
        self.task_list = []
        self.reObject = re.compile(r'[\,\(\)%]')
        self.link_map = {
            "/images/icon_s_a.png":"amazon",
            "/images/icon_s_i.png":"iTunes",
            "/images/icon_s_g.png":"GooglePlay",
            "/images/icon_s_r.png":"Rakten",
            "/images/icon_s_n.png":"NANACO",
            "/images/icon_s_w.png":"WebMoney"
        }
        self.kind_map = {
            "amazon":0,
            "iTunes":1,
            "GooglePlay":2,
            "Rakten":3,
            "NANACO":4,
            "WebMoney":5
        }
        self.spider_thread = threading.Thread(target=self.MySpider, args=(win, data_lock))
        # 微信登入处理
        self.wechat_thread = threading.Thread(target=self.login_WeChat, args=(win,))

        self.spider_thread.start()
        self.wechat_thread.start()


    def login_WeChat(self, win):
        while True:
            if self.win_close == False and win.wechar_login == True and self.wechat_login_flag == False:
                try:
                    self.wc.run()
                    print("监控程序已启动！")
                    self.wc.send_to_me("监控程序已启动！")
                    win.set_wechat_status(True)
                    self.wechat_login_flag = True
                except Exception as err:
                    print(err.__traceback__.tb_frame.f_globals["__file__"],
			          "\tLines：", err.__traceback__.tb_lineno)  # 发生异常所在的文件
                    print(err)
            time.sleep(1.0)
            print("WeChat休眠！")

    def MySpider(self, win, data_lock):
        while True:
            try:
                if win.run_status == True:
                    task_list, kind = self.get_task_list(win, data_lock)
                    data_list = []
                    for ind in kind:
                        data_list = data_list + self.get_data(win.system_init["link"], ind)
                    data_list = self.deal_data(data_list)
                    print(task_list)
                    print(data_list)
                    res = []
                    task_run_res = [0]*len(task_list)
                    for reality in data_list:
                        for expectation, pos in zip(task_list, range(len(task_list))):
                            if expectation !=[] and True == self.compare(expectation, reality):
                                res.append(reality)
                                task_run_res[pos] = 1
                                break
                    print("*"*20)
                    win.task_run_res = task_run_res
                    win.updata_task_res()
                    for history in res:
                        print(history)
                    if len(res)!=0:
                        self.playMusic(win.system_init["alarm"])
                    if self.wechat_login_flag == True:
                        for history in res:
                            self.wc.send_to_me(str(history))
                            print(history)
                    print("*"*20)
            except Exception as err:
                print(err.__traceback__.tb_frame.f_globals["__file__"],
			  "\tLines：", err.__traceback__.tb_lineno)  # 发生异常所在的文件
                print(err)
            time.sleep( win.refresh_time ) # 刷新时间
            print("Spider线程休眠！")

    def deal_data(self, data_list):
        new_data_list = []
        for line in data_list:
            new_line_data = []
            new_line_data.append( self.link_map[line[0]] )
            new_line_data.append( int(self.reObject.sub("", line[1])) )
            new_line_data.append( int(self.reObject.sub("", line[2])) )
            new_line_data.append( int(self.reObject.sub("", line[3])) )
            new_line_data.append( float(line[4]) )
            new_line_data.append( int(self.reObject.sub("", line[6])) )
            new_line_data.append( float(self.reObject.sub("", line[7])) )
            new_data_list.append( new_line_data )
        return new_data_list

    def get_data(self, url, currency):
        """
        得到指定网页并解析里面的数据成列表
        """
        data_list = []
        try:
            re = requests.post(url=url, data={"g_type": currency})
            re.encoding = 'utf-8'  # 编码格式
            html = etree.HTML(re.text)
            trs = html.xpath('/html/body/section/section/div[3]/section/article/div/table/tr')
            for tr in trs[1:]:
                tds = tr.xpath('./td')
                td_text = []
                td_text = td_text + tds[0].xpath('./img/@src')
                for td in tds[1:5]:
                    try:
                        td_text = td_text + td.xpath('./span/text()')
                    except Exception as err:
                        print(err)

                td_text = td_text + tr.xpath('./td[@class="pc"]/text()')
                td_text = td_text + tds[6].xpath('./text()')
                data_list.append(td_text)
        except Exception as err:
            print(err)
        return data_list

    def compare(self, expectation, reality):
        if expectation[0] != reality[0]:
            return False
        if expectation[1]!=0 and expectation[1]>reality[1]:
            return False
        if expectation[2]!=0 or expectation[3]!=0:
            if expectation[2]>reality[2] or reality[2]>expectation[3]:
                return False
        if expectation[4]!=0 or expectation[5]!=0:
            if expectation[4]>reality[3] or reality[3]>expectation[5]:
                return False
        # if expectation[6] != reality[4]:
        #     return False
        if expectation[7]!=0 or expectation[8]!=0:
            if expectation[7]>reality[5] or reality[5]>expectation[8]:
                return False
        if expectation[9]!=0 or expectation[10]!=0:
            if expectation[9]>reality[6] or reality[6]>expectation[10]:
                return False
        return True

    def get_task_list(self, win, data_lock):
        index = win.task_status_ind  # 状态信息所在字段的位置
        task_list = []
        kind = []
        # -------------此处记得加上线程锁--------------------#
        data_lock.acquire()  # 获得锁
        # 遍历Treeview中所有的行
        for item in win.tree.get_children():
            task = []
            if "运行中" in win.tree.item(item, "values")[index]:

                link_ind = self.kind_map[win.tree.item(item, "values")[0]]
                if link_ind not in kind:
                    kind.append(link_ind)
                task.append(win.tree.item(item, "values")[win.tree_map_ind["curchoose"]])
                task.append(int(win.tree.item(item, "values")[win.tree_map_ind["remainder"]]))
                facevalue = win.tree.item(item, "values")[win.tree_map_ind["facevalue"]].split("-")
                task = task + [int(facevalue[0]), int(facevalue[1])]
                price = win.tree.item(item, "values")[win.tree_map_ind["price"]].split("-")
                task = task + [int(price[0]), int(price[1])]
                task.append(int(win.tree.item(item, "values")[win.tree_map_ind["salesrate"]]) )
                num = win.tree.item(item, "values")[win.tree_map_ind["num"]].split("-")
                task = task + [int(num[0]), int(num[1])]
                percent = win.tree.item(item, "values")[win.tree_map_ind["percentage"]].split("-")
                task = task + [float(percent[0]), float(percent[1])]
            task_list.append(task)

        data_lock.release()  # 释放锁
        return task_list, kind

    def playMusic(self, musicPath):
        """
        播放音乐
        :param musicPath: 要播放音乐文件所在的路径
        :return:None
        """
        # 判断路径是否存在
        if not os.path.exists(musicPath):
            print("Can not found path !")
        try:
            if self.__system == "windows":
                if ".mp3" in musicPath:
                    self.player.play(musicPath)
                    self.player.stop()
                    self.player.close()
        except Exception as err:
            print(err)

    def release(self):
        try:
            _async_raise(self.spider_thread)
            print("spider_thread was release!")
        except Exception as err:
            print(err)

        try:
            _async_raise(self.wechat_thread)
            print("wechat_thread was release!")
        except Exception as err:
            print(err)

        self.win_close = True

    def __del__(self):
        pass


if __name__ == "__main__":

    lock = threading.Lock()  # 信号量
    root = tk.Tk()  # 创建窗口对象的背景色
    win = MainWindows(root, "定制化监测工具", lock)
    win.letf_init()
    win.top_init()
    win.bottom_init()

    ctrl = Control(win, lock)
    win.run(callback = ctrl.release)

    # 进入消息循环 父窗口进入事件循环，可以理解为保持窗口运行，否则界面不展示
    root.mainloop()