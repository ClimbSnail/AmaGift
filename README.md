### 用户数据监控程序(带界面)

监控网站 <https://ama-gift.com/list.php>
![](https://gitee.com/ClimbSnailQ/Project_Image/raw/master/Note/AmaGift.jpg)

1. 使用python编写
2. `pip3 install requests pillow itchat lxml -i https://mirrors.aliyun.com/pypi/simple/`

2. GUI使用python下的tkinter
3. 使用pyinstaller打包程序 `pyinstaller --icon favicon.ico -F Control.py wechat.py windows.py tkutils.py`

### 程序介绍
Control.py	为整个程序的入口程序

init_config.cfg	为初始化文件
coming.mp3	为检测到数据时的提示音(在init_config.cfg中可配置)
