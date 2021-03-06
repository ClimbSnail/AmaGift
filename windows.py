
#import tkinter
#from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import tkinter.font as tkFont
import tkutils as tku
from PIL import Image, ImageTk	# pip3 install pillow
import codecs
import time
import json
import os

class MainWindows(object):

    def __init__(self, root, title = "顶定制化监测工具", lock = None):
        self.root = root
        self.lock = lock
        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                if self.winclose_callback != None:
                    self.winclose_callback()
                root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)
        # 获取屏幕分辨率
        screenWidth = self.root.winfo_screenwidth()
        screenHeight = self.root.winfo_screenheight()
        # print(screenWidth, screenHeight)

        self.root.title(title)           #窗口名
        self.root.geometry('1200x750+10+10')
        tku.center_window(self.root)  # 将窗体移动到屏幕中央
        self.root.iconbitmap("./favicon.ico")  # 窗体图标
        #self.root.resizable(False, False)  # 设置窗体不可改变大小
        self.root.attributes("-alpha", 0.95)  # 虚化，值越小虚化程度越高
        self.my_ft1 = tkFont.Font(family="微软雅黑", size=12, weight=tkFont.BOLD)   # 定义字体
        self.my_ft2 = tkFont.Font(family="微软雅黑", size=14, weight=tkFont.BOLD)   # 定义字体
        self.wechar_login = False
        self.run_status = False
        self.task_run_res = []
        self.winclose_callback = None # 窗口关闭的回调函数
        self.getUserData("./init_config.cfg")
        # 状态信息所在字段的位置
        self.task_status_ind = len(self.gui["fields"].strip().split())-1
        self.tree_map_ind = {
            "curchoose": 0,
            "remainder": 1,
            "facevalue": 2,
            "price": 3,
            "salesrate": 4,
            "num": 5,
            "percentage": 6,
            "status":7
        }

    def getUserData(self, path):
        fp = codecs.open(path, "r", "utf8")
        self.set_data = json.load(fp)
        fp.close()
        self.system_init = self.set_data["system_init"]
        self.gui = self.set_data["gui"]
        self.taskinfo = self.set_data["taskinfo"]

        self.refresh_time = int(self.taskinfo["updatatime"]) if self.taskinfo["updatatime"] != "" else 10

    def letf_init(self):
        self.left_frame = tk.Frame(self.root, bg = "DimGray")
        label_text = [ value for key, value in self.gui.items() if key not in ["currency", "fields"] ]
        labels = []

        for text in label_text:  # 第一个小部件插入数据
            labels.append( text )

        ind = self.tree_map_ind["curchoose"]
        choose_label = tk.Label(self.left_frame, text=labels[ind], font=self.my_ft1, bg=self.left_frame['bg'])
        choose_label.pack()
        # 单选按钮
        self.radio_frames = []
        self.RadioManager = tk.IntVar()  # IntVar 是tkinter的一个类，可以管理单选按钮
        self.RadioList = [] # 单选按钮列表
        each_num = 2
        self.radio_texts = self.gui["currency"].strip().split()  # 单选按钮的值
        for pos in range(len(self.radio_texts)):
            if pos % each_num == 0:
                self.radio_frames.append( tk.Frame(self.left_frame) )
            self.RadioList.append(
                tk.Radiobutton(self.radio_frames[pos//each_num], variable=self.RadioManager,
                               value=pos, text=self.radio_texts[pos], width=10, bg="DimGray") )
            self.RadioList[pos].pack(side=tk.LEFT)
            if (pos+1) % each_num == 0: # 本行单选框已放满
                self.radio_frames[pos // each_num].pack()
        # 设置第一个未默认
        self.RadioManager.set(0)

        # 剩余frame
        remainder_frame = tk.Frame(self.left_frame, bg=self.left_frame['bg'])
        # 销售率
        ind = self.tree_map_ind["remainder"]
        salesrate_label = tk.Label(remainder_frame, text=labels[ind], font=self.my_ft1, bg=remainder_frame['bg'])
        salesrate_label.pack(side=tk.LEFT, anchor='sw')
        tk.Label(remainder_frame, text=">", font=self.my_ft1, bg=remainder_frame['bg'])\
            .pack(side=tk.LEFT, anchor='sw', padx=4)
        self.remainder = tk.Text(remainder_frame, font=self.my_ft2, width = 8, height=1, highlightcolor="LightGrey")
        self.remainder.pack(side=tk.LEFT, padx=10)  # 将小部件放置到窗口中
        remainder_frame.pack(side=tk.TOP, padx=10, pady=8)

        # 面值字体
        face_val_frame = tk.Frame(self.left_frame, bg=self.left_frame['bg'])
        ind = self.tree_map_ind["facevalue"]
        face_val_label = tk.Label(face_val_frame, text=labels[ind], font=self.my_ft1, bg=face_val_frame['bg'])
        face_val_label.pack(side=tk.TOP,  padx=10, pady=5)
        # 面值范围框
        self.face_val_min = tk.Text(face_val_frame, font=self.my_ft2, width = 8, height=1, highlightcolor="LightGrey")
        self.face_val_min.pack(side=tk.LEFT)  # 将小部件放置到窗口中
        tk.Label(face_val_frame, text="<", font=self.my_ft1, bg=face_val_frame['bg'])\
            .pack(side=tk.LEFT, anchor='sw', padx=4)
        self.face_val_max = tk.Text(face_val_frame, font=self.my_ft2, width = 8, height=1, highlightcolor="LightGrey")
        self.face_val_max.pack(side=tk.LEFT)  # 将小部件放置到窗口中
        face_val_frame.pack(side=tk.TOP, pady=8)

        # 价格Frame
        price_frame = tk.Frame(self.left_frame, bg=self.left_frame['bg'])
        # 价格
        ind = self.tree_map_ind["price"]
        price_label = tk.Label(price_frame, text=labels[ind], font=self.my_ft1, bg=price_frame['bg'])
        price_label.pack(side=tk.TOP, pady=5)
        # 价格框
        self.price_min = tk.Text(price_frame, font=self.my_ft2, width = 8, height=1, highlightcolor="LightGrey")
        self.price_min.pack(side=tk.LEFT)  # 将小部件放置到窗口中
        tk.Label(price_frame, text="<", font=self.my_ft1, bg=price_frame['bg'])\
            .pack(side=tk.LEFT, anchor='sw', padx=4)
        self.price_max = tk.Text(price_frame, font=self.my_ft2, width = 8, height=1, highlightcolor="LightGrey")
        self.price_max.pack(side=tk.LEFT)  # 将小部件放置到窗口中
        price_frame.pack(side=tk.TOP, padx=10, pady=8)

        # 销售率frame
        salesrate_frame = tk.Frame(self.left_frame, bg=self.left_frame['bg'])
        # 销售率
        ind = self.tree_map_ind["salesrate"]
        salesrate_label = tk.Label(salesrate_frame, text=labels[ind], font=self.my_ft1, bg=salesrate_frame['bg'])
        salesrate_label.pack(side=tk.LEFT, anchor='sw')
        self.salesrate = tk.Text(salesrate_frame, font=self.my_ft2, width = 8, height=1, highlightcolor="LightGrey")
        self.salesrate.pack(side=tk.LEFT, padx=10)  # 将小部件放置到窗口中
        salesrate_frame.pack(side=tk.TOP, padx=10, pady=8)

        # 销售数量Frame
        num_frame = tk.Frame(self.left_frame, bg=self.left_frame['bg'])
        # 销售数量
        ind = self.tree_map_ind["num"]
        num_label = tk.Label(num_frame, text=labels[ind], font=self.my_ft1, bg=num_frame['bg'])
        num_label.pack(side=tk.TOP,  padx=10, pady=5)
        # 销售范围框
        self.num_min = tk.Text(num_frame, font=self.my_ft2, width = 8, height=1, highlightcolor="LightGrey")
        self.num_min.pack(side=tk.LEFT)  # 将小部件放置到窗口中
        tk.Label(num_frame, text="<", font=self.my_ft1, bg=num_frame['bg'])\
            .pack(side=tk.LEFT, anchor='sw', padx=4)
        self.num_max = tk.Text(num_frame, font=self.my_ft2, width = 8, height=1, highlightcolor="LightGrey")
        self.num_max.pack(side=tk.LEFT)  # 将小部件放置到窗口中
        num_frame.pack(side=tk.TOP, padx=10, pady=8)

        # 销售百分比Frame
        percent_frame = tk.Frame(self.left_frame, bg=self.left_frame['bg'])
        # 销售百分比
        ind = self.tree_map_ind["percentage"]
        percent_label = tk.Label(percent_frame, text=labels[ind], font=self.my_ft1, bg=percent_frame['bg'])
        percent_label.pack(side=tk.TOP,  padx=10, pady=5)
        # 销售百分比范围框
        self.percent_min = tk.Text(percent_frame, font=self.my_ft2, width = 8, height=1, highlightcolor="LightGrey")
        self.percent_min.pack(side=tk.LEFT)  # 将小部件放置到窗口中
        tk.Label(percent_frame, text="<", font=self.my_ft1, bg=percent_frame['bg'])\
            .pack(side=tk.LEFT, anchor='sw', padx=4)
        self.percent_max = tk.Text(percent_frame, font=self.my_ft2, width = 8, height=1, highlightcolor="LightGrey")
        self.percent_max.pack(side=tk.LEFT)  # 将小部件放置到窗口中
        percent_frame.pack(side=tk.TOP, padx=10, pady=8)

        # 添加按钮
        self.add_button = tk.Button(self.left_frame, text="添加任务", bg="LightBlue",
                                command=self.add_task, font=self.my_ft1, height=1, fg="white", width=10)
        self.add_button.pack(side=tk.TOP, expand=tk.YES, anchor=tk.CENTER)

        self.wechat_img = ImageTk.PhotoImage(Image.open('./Stop_Wechat.ico'))
        self.img_frame = tk.Button(self.left_frame, relief=tk.FLAT, image = self.wechat_img,
                                   bg="DimGray", command=self.wechat_click)
        self.img_frame.pack(side=tk.BOTTOM)

    def add_task(self):
        print("添加任务")
        try:
            radio_val = self.RadioManager.get()
            curchoose = self.radio_texts[radio_val]
            remainder = self.remainder.get(0.0, tk.END).strip()
            face_val_min = self.face_val_min.get(0.0, tk.END).strip()
            face_val_max = self.face_val_max.get(0.0, tk.END).strip()
            price_min = self.price_min.get(0.0, tk.END).strip()
            price_max = self.price_max.get(0.0, tk.END).strip()
            num_min = self.num_min.get(0.0, tk.END).strip()
            num_max = self.num_max.get(0.0, tk.END).strip()
            salesrate = self.salesrate.get(0.0, tk.END).strip()
            percent_min = self.percent_min.get(0.0, tk.END).strip()
            percent_max = self.percent_max.get(0.0, tk.END).strip()

            if curchoose=="" or face_val_min=="" or face_val_max=="" or price_min=="" or price_max=="" or num_min=="" or \
                num_max == "" or salesrate=="" or percent_min=="" or percent_max=="":
                return False
            # 构建插入的条目
            field_info = [curchoose, remainder, face_val_min+'-'+face_val_max, price_min+'-'+price_max, salesrate,
                          num_min+'-'+num_max, percent_min+'-'+percent_max]
            taskkey = "task"+str(len(self.tree.get_children())+1)
        except Exception as err:
            return False

        if None != self.lock:
            self.lock.acquire()  # 获得锁
        item = self.tree.insert("", tk.END, text=taskkey, values=field_info)  #给第末行添加数据，索引值可重复
        self.tree.set(item, column=self.task_status_ind, value="已关闭")
        if None != self.lock:
            self.lock.release()  # 释放锁
        return True

    def updata_task_res(self):

        if None != self.lock:
            self.lock.acquire()  # 获得锁
        for item, pos in zip(self.tree.get_children(),range(len(self.tree.get_children()))):
            text = self.tree.item(item, "values")[self.task_status_ind]
            text = text.split('(')[0]
            text = text+"(有数据)" if self.task_run_res[pos] == 1 else text
            self.tree.set(item, column=self.task_status_ind, value=text)
        if None != self.lock:
            self.lock.release()  # 释放锁

    def wechat_click(self):
        if self.wechar_login == False:
            self.wechar_login = True
        else:
            self.wechar_login = False

    def set_wechat_status(self, status):
        if status == True:
            self.wechat_img = ImageTk.PhotoImage(Image.open('./Run_Wechat.ico'))
            self.img_frame["image"] = self.wechat_img
        else:
            self.wechat_img = ImageTk.PhotoImage(Image.open('./Stop_Wechat.ico'))
            self.img_frame["image"] = self.wechat_img


    def top_init(self):
        # 获取当前双击行的值
        def ldoubleTree(event):
            for item in self.tree.selection():
                item_text = self.tree.item(item, "values")
                print(item_text)
            if len(self.tree.selection()) != 0:
                self.del_button.configure(fg="red")   # 设置删除文本颜色

        def rsingleTree(event):
            x, y, widget = event.x, event.y, event.widget
            item = widget.item(widget.focus())
            itemText = item['text']
            itemValues = item['values']
            iid = widget.identify_row(y)
            column = event.widget.identify_column(x)
            print ('\n&&&&&&&& def selectItem(self, event):')
            print ('item = ', item)
            print('itemValues = ',itemValues)

            for item in self.tree.selection():
                print("len = ", len(self.tree.item(item, "values")))
                if "已关闭" in self.tree.item(item, "values")[self.task_status_ind]:
                    self.tree.set(item, column=self.task_status_ind, value="运行中")
                else:
                    self.tree.set(item, column=self.task_status_ind, value="已关闭")

        self.top_frame = tk.Frame(self.root, bg = "LightGrey")  # , width = 200, height=1000
        list_two = tk.Listbox(self.top_frame)
        top_kind = self.gui["fields"].strip().split(" ")

        self.scrollbar = tk.Scrollbar(self.root,)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(self.top_frame, show = "headings", height = 14,
                                 yscrollcommand=self.scrollbar.set, selectmode = tk.BROWSE)
        # height为显示多少行数据 headings为只显示表头
        s = ttk.Style()
        s.configure('Treeview', rowheight=40)  # repace 40 with whatever you need
        self.tree["columns"] = top_kind
        self.task_status_ind = top_kind.index("状态")
        width_list = [80, 40, 120, 150, 60, 100, 100, 100]
        for col, width in zip(self.tree["columns"], width_list):
            self.tree.column(col, width=width, anchor="center")  #设置列
            self.tree.heading(col, text=col)  # #设置显示的表头名

        for tasknum in range(int(self.taskinfo["tasknum"])):
            taskkey = "task"+str(tasknum+1)
            onetaskinfo = self.taskinfo[taskkey]
            field_info = [value for value in onetaskinfo.values()]
            self.tree.insert("", tk.END, text=taskkey, values=field_info)  #给第末行添加数据，索引值可重复
        # 遍历Treeview中所有的行
        for item in self.tree.get_children():
            self.tree.set(item, column=self.task_status_ind, value="已关闭")

        self.tree.grid()
        self.tree.pack(expand = True, fill = tk.BOTH)  # 设置表格最大化
        # 鼠标事件
        self.tree.bind('<Double-1>', ldoubleTree)    # 左键双击
        self.tree.bind('<3>', rsingleTree)    # 右键单击
        # self.tree.bind("<Control-a>", ldoubleTree)  # ctrl+A
        # self.tree.bind('<ButtonRelease-1>', treeviewClick)  # 单机释放回调处理
        # self.tree.bind('<<TreeviewSelect>>', selectTree)

    def start_task(self):
        """
        任务开始运行函数，start_button触发
        """
        if self.start_button["fg"] == "white":
            print("任务已开始")
            self.time_enter.configure(state="disabled")   # 设置时间文本状态不可写
            self.start_button.configure(fg="green")   # 设置文本颜色
            self.stop_button.configure(fg="white")   # 设置文本颜色
            self.run_status = True

    def stop_task(self):
        if self.stop_button["fg"] == "white":
            print("任务已停止")
            self.time_enter.configure(state="normal")   # 设置时间文本状态可写
            self.start_button.configure(fg="white")   # 设置文本颜色
            self.stop_button.configure(fg="green")   # 设置文本颜色
            self.run_status = False

    def del_colTreeview(self):
        if self.del_button["fg"] == "white":
            return None
        for item in self.tree.selection():
            item_text = self.tree.item(item, "values")
            self.tree.delete(item)  # 删除行
            print(item_text)
        self.del_button.configure(fg="white")  # 设置删除文本颜色

    def save_config(self):
        text_src = self.save_button["text"]
        self.save_button["text"] = "成功"
        self.save_button.update()
        task_num = len(self.tree.get_children())
        self.taskinfo = {"tasknum":str(task_num), "updatatime":str(self.refresh_time)}
        for item, pos in zip(self.tree.get_children(),range(task_num)):
            task = {}
            task["curchoose"] = self.tree.item(item, "values")[self.tree_map_ind["curchoose"]]
            task["remainder"] = self.tree.item(item, "values")[self.tree_map_ind["remainder"]]
            task["facevalue"] = self.tree.item(item, "values")[self.tree_map_ind["facevalue"]]
            task["price"] = self.tree.item(item, "values")[self.tree_map_ind["price"]]
            task["salesrate"] = self.tree.item(item, "values")[self.tree_map_ind["salesrate"]]
            task["num"] = self.tree.item(item, "values")[self.tree_map_ind["num"]]
            task["percentage"] = self.tree.item(item, "values")[self.tree_map_ind["percentage"]]
            self.taskinfo["task"+str(pos+1)] = task
        self.set_data["taskinfo"] = self.taskinfo
        fp = codecs.open("./init_config.cfg", "w", "utf8")
        json.dump(self.set_data, fp, indent=2)
        fp.close()
        time.sleep(0.5)
        self.save_button["text"] = text_src

    def bottom_init(self):
        bottom_bg = "AliceBlue"
        self.bottom_frame = tk.Frame(self.root, bg = bottom_bg)

        # 刷新文本字体
        time_text = tk.Label(self.bottom_frame, text="刷新时间(秒)", font=self.my_ft2, bg=self.bottom_frame['bg'])
        time_text.pack(side=tk.LEFT, padx=10, pady=50)  # 将小部件放置到窗口中

        # 刷新时间输入
        def time_enter_submit(ev = None):
            time_text = self.time_enter.get()
            self.refresh_time = int(time_text) if time_text != "" or time_text != None else self.refresh_time
            # 设置边框
            self.time_enter.configure(relief=tk.GROOVE)
            self.time_enter.configure(fg='LightBlue')   # 设置参数
            # FLAT SUNKEN RAISED GROOVE RIDGE
            print(self.refresh_time)

        self.time_enter = tk.Entry(self.bottom_frame, font=self.my_ft2, width = 5, highlightcolor="LightGrey")
        self.time_enter.bind("<Return>", time_enter_submit) # 绑定enter键的触发
        self.time_enter.pack(side=tk.LEFT, padx=0, pady=50)  # 将小部件放置到窗口中
        self.time_enter.insert(0, str(self.refresh_time))

        self.start_button = tk.Button(self.bottom_frame, text="开始任务", bg="LightBlue",
                                command=self.start_task, font=self.my_ft2, fg="white", width=10)
        self.start_button.pack(side=tk.LEFT, anchor=tk.CENTER, padx=10, pady=50)

        self.stop_button = tk.Button(self.bottom_frame, text="停止任务", bg="LightBlue",
                                command=self.stop_task, font=self.my_ft2, height=1, fg="white", width=10)
        self.stop_button.pack(side=tk.LEFT, expand=tk.YES, anchor=tk.CENTER, padx=5)

        self.del_button = tk.Button(self.bottom_frame, text="删除任务", bg="LightBlue",
                                command=self.del_colTreeview, font=self.my_ft2, height=1, fg="white", width=10)
        self.del_button.pack(side=tk.LEFT, expand=tk.YES, anchor=tk.CENTER, padx=5)

        self.save_button = tk.Button(self.bottom_frame, text="保存配置", bg="LightBlue",
                                command=self.save_config, font=self.my_ft2, height=1, fg="white", width=10)
        self.save_button.pack(side=tk.LEFT, expand=tk.YES, anchor=tk.CENTER, padx=5)

    def run(self, callback = None):
        # 窗口关闭后的回调函数
        self.winclose_callback = callback
        # 绘制窗口
        self.left_frame.pack(side=tk.LEFT, anchor=tk.CENTER, fill='y', padx=5, pady=5)
        self.top_frame.pack(side=tk.TOP, anchor=tk.CENTER, fill='x', padx=5, pady=5)
        self.bottom_frame.pack(side=tk.BOTTOM, anchor=tk.CENTER, fill='x', padx=5, pady=5)

    def __del__(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()  # 创建窗口对象的背景色
    win = MainWindows(root, "定制化监测工具")
    win.letf_init()
    win.top_init()
    win.bottom_init()
    win.run()
    # 进入消息循环 父窗口进入事件循环，可以理解为保持窗口运行，否则界面不展示
    root.mainloop()