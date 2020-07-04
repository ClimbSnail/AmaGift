
import itchat	# sudo pip3 install itchat
import time

# 微信对象
class Wechat(object):

    def __init__(self, name = "filehelper"):
        self.itchat = itchat
        self.name = name

    def run(self):
        try:
            #self.itchat.auto_login(hotReload = True)  # 会弹出网页二维码，扫描即可，登入你的微信账号，True保持登入状态
            self.itchat.auto_login()  # 会弹出网页二维码，扫描即可，登入你的微信账号，True保持登入状态
            # my_friend = self.itchat.search_friends(name="")  # name改成你朋友在你微信的备注
            # self.receiver = [name["UserName"] for name in my_friend]
            self.receiver = []
            self.receiver.append(self.name)  # 添加微信号
            self.emergency = self.name
        except Exception as err:
            print(err.__traceback__.tb_frame.f_globals["__file__"],
              "\tLines：", err.__traceback__.tb_lineno)  # 发生异常所在的文件
            print(err)


    def send_to(self, message, receiver):
        try:
            self.itchat.send(message, toUserName=receiver)
        # 每隔86400秒发送一次，也就是每天发一次
        # Timer(10, send_news).start()
        except:
            self.send_to_me("服务器出错啦！")

    def send_all(self, message):
        try:
            for receiver in self.receiver:
                self.itchat.send(message, toUserName=receiver)
        except:
            self.send_to_me("服务器出错啦！")

    def send_to_me(self, message):
        try:
            self.itchat.send(message, toUserName=self.emergency)
        except:
            pass

    def __del__(self):
        nowtime = time.time()
        self.send_to_me("客户端已掉线"+ str(nowtime))


if __name__ == "__main__":

    wc = Wechat("filehelper")
    wc.run()
    print("Hello")
    wc.send_to_me("监控程序已启动！")
    while True:
        pass