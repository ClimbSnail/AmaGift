
import itchat	# sudo pip3 install itchat
import time

# 微信对象
class Wechat(object):

    def __init__(self):
        self.itchat = itchat
        pass

    def run(self):
        #self.itchat.auto_login(hotReload = True)  # 会弹出网页二维码，扫描即可，登入你的微信账号，True保持登入状态
        self.itchat.auto_login()  # 会弹出网页二维码，扫描即可，登入你的微信账号，True保持登入状态
        my_friend = self.itchat.search_friends(name="wuhao")  # name改成你朋友在你微信的备注
        self.receiver = [name["UserName"] for name in my_friend]
        self.receiver.append("filehelper")  # 添加微信号
        self.emergency = "filehelper"


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

    wc = Wechat()
    wc.run()
    print("Hello")
    wc.send_to_me("监控程序已启动！")
    while True:
        pass