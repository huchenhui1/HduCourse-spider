# 基于网络爬虫的选课系统捡漏提醒工具

## 简介

每次为了排出理想的课表，都会耗费不少时间和精力。

对于英语课，跨文化交际等比较热门难以选到，有时候甚至选不到课。对于体育课，无线电、乒乓球等热门课较难选到。对于专业课，一般是允许签课的，但可能有些老师不允许。对于基础必修课，部分热门老师的课抢不到，理学院的课一般不让签课如物原课。对于公选课，抢不到就算了吧，反正也是为了水...

但在开学初，课程余量还是会有变动，因为开学初还允许换课，而且还存在囤课现象。针对这一情况，如果能勤奋地登录选课系统查看，有时候是可以捡漏到想要的课的。但手动登录选课系统查看比较麻烦，使用本工具可以自动获取课程余量信息，实现捡漏提醒。

主要功能：可自动获取英语课、体育课、跨专业选课中可搜索到的专业基础课的课程余量信息，并可设置筛选条件，符合条件的课程有余量时可发送邮件提醒。

其它功能：查成绩

本工具仅对于HDU正方教务管理系统使用。

## 运行环境

**Python版本**

Python 3.5 | Anaconda | Windows 7

**Python爬虫HTML解析库——Beautiful Soup**

Beautiful Soup 是一个可以从HTML或XML文件中提取数据的Python库，简单来说，它能将HTML的标签文件解析成树形结构，然后方便地获取到指定标签的对应属性。

**Python HTTP 库——Requests**

requests是一个Python第三方库，通过urllib3实现自动发送HTTP/1.1请求，它能轻松的实现cookies，登陆验证，代理设置等操作。比Python内置的urllib模块更方便好用。

## 实现过程

1. 模拟登录选课系统，获取cookies
2. 使用Requests库发起带有cookies的请求，模拟访问选课系统
3. 通过设定参数，访问选课系统中的目标页面
4. 使用beautiful soup解析网页，获取课程信息
5. 使用SMTP发邮件提醒

具体实现过程计划写博客。

## 问题记录

1. [正方教务管理系统模拟登录具体实现过程(未写)]()
2. [正方教务管理系统爬取课程信息(未写)]()
3. [Python3中的md5加密](https://blog.csdn.net/qq_38607035/article/details/82591931)
4. [requests库的使用(未写)]()
5. [用python进行URL编码](https://blog.csdn.net/qq_38607035/article/details/82594822)
6. [使用python发送QQ邮件](https://blog.csdn.net/qq_38607035/article/details/82594695)
7. [将python脚本打包成可执行exe文件](https://blog.csdn.net/qq_38607035/article/details/82592602)
8. [Python异常UnicodeEncodeError: 'gbk' codec can't encode character '\ufffd'](https://blog.csdn.net/qq_38607035/article/details/82595032)
9. [Python异常UnicodeEncodeError: 'gbk' codec can't encode character '\xa0](https://blog.csdn.net/qq_38607035/article/details/82595170)

## 运行方法

本工具目前仅支持DOS命令窗口操作，未实现客户端GUI界面交互操作。

1. 在main.exe所在路径下创建login.txt文件，依次输入学号，密码，接收提醒的邮箱，用回车隔开。为保证及时接收到提醒，请在相关社交软件上开启邮箱的收件提醒功能。

2. 运行main.exe启动程序，选择功能，对照选课系统上的课程信息，根据文字提示操作，一次只能选择一类课程。
3. 如果需要选择多类课程，可多开main.exe运行。
4. 退出直接关闭。

## Todo

1. 公选课爬取
2. 用Tkinter，做成客户端，UI界面操作
3. 开多线程？
4. 用服务器？
5. 加入自动选课功能

## 声明

由于本工具无自动选课功能，所以对换课行为没有大影响。

本工具仅供学习交流与个人使用，不得大范围传播与牟利。