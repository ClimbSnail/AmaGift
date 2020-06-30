from windows import *
from wechat import *
import threading
import time
import ctypes
import inspect

def _async_raise(thread):
    """
    释放进程
    :param thread: 进程对象
    :param exctype:
    :return:
    """
    try:
        tid = thread.ident
        #tid = ctypes.c_long(tid)
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

    def __init__(self, win):
        self.wechat_login_flag = False
        self.wc = Wechat()
        self.win_close = False
        self.task_list = []
        self.spider_thread = threading.Thread(target=self.MySpider, args=(win,))
        # 微信登入处理
        self.wechat_thread = threading.Thread(target=self.login_WeChat, args=(win,))

        self.spider_thread.start()
        self.wechat_thread.start()

    def MySpider(self, win):
        while True:
            if win.run_status == True:
                self.task_list = self.get_task_list(win)

            time.sleep( win.refresh_time ) # 刷新时间
            print("Spider线程休眠！")

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
                    print(err)
            time.sleep(1.0)
            print("WeChat休眠！")

    def get_task_list(self, win):
        win.task_status_ind = 6  # 状态信息所在字段的位置

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

    root = tk.Tk()  # 创建窗口对象的背景色
    win = MainWindows(root, "定制化监测工具")
    win.letf_init()
    win.top_init()
    win.bottom_init()

    ctrl = Control(win)
    win.run(callback = ctrl.release)

    # 进入消息循环 父窗口进入事件循环，可以理解为保持窗口运行，否则界面不展示
    root.mainloop()