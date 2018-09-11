# -*- coding: utf-8 -*-
import time
from utils import *
import sys

# 从文件中获取学号，密码，邮箱
username,password,email = get_user()
# 从文件中获取cookies
# cookies = {}
cookies = get_cookies()

# 用缓存的cookies预登录
if(login_pre(cookies,username)):
  print('登录成功！')
else:
  print('登录过期！正在重新登录...')
  # 重新用学号密码登录
  if(login(username,password)):
  	print('登录成功！')
  	# 更新cookies
  	cookies_file_new = open ('cookies.txt', 'r')
  	cookies['ASP.NET_SessionId'] = cookies_file_new.readline().strip()
  	cookies['route'] = cookies_file_new.readline().strip()
  	cookies_file_new.close()
  else:
  	print('登录失败！请检查是否在login.txt正确填写学号和密码，以及密码是否正确')
  	x = input('按回车键退出')
  	sys.exit()

while True:
  print('------------------')
  print('1.查成绩')
  print('2.英语课')
  print('3.体育课')
  print('4.跨专业选课可搜索的课')
  print('0.退出')
  print('------------------')
  x = int(input('请输入序号:'))
  if(x == 0):
    break
  elif(x == 1):
    # 功能一：查成绩
    xn = input('请输入学年(如2017-2018)：')
    xq = input('请输入学期(1或2)：')
    get_score(cookies,xn, xq,username)
  elif(x == 2 or x == 3 or x== 4):
	  # 准备部分 还可以更多，所有的课程基本数据 用本来网页上的筛选条件
	  # 变量定义
	  # 英语课：hid参数
	  # 体育课：课程信息、hid参数
	  # 跨专业选课：搜索课程
	  lesson_name = []
	  lesson_sport_id = []
	  teacher_name = []
	  weekday = ['1','2','3','4','5']
	  remain = 1
	  email_remind = 2
	  scan_time = 5
	  # 查英语课
	  if(x == 2):
	  	# 获取hid参数
	  	hid_english = get_english(cookies,username)
	  # 查体育课
	  if(x == 3):
	    # 获取课程信息和hid参数
	    lesson_sport_name_id,hid_sport = get_sport(cookies,username)
	  # 跨专业选课
	  if(x == 4):
	    search_name = input('请输入课程名称用以搜索:')
	    search_result_list = search_lesson(cookies,username,search_name)
	    for index,lesson in enumerate(search_result_list):
	      print(str(index+1) + '.',end='')
	      lesson.show()
	    search_index = int(input('请选择序号:'))
	    lesson_name = [search_result_list[search_index-1].name]
	  
	  # 设置条件部分
	  n = 1
	  while n!=0:
	    # 显示菜单的同时，显示提示和当前设置值
	    print('------------------')
	    print('1.课程名称:',end=' ')
	    if(len(lesson_name) == 0):
	      if(x == 2):# 英语课 默认全部
	        print('不限',end='')
	      elif(x == 3):
	        print('请选择',end='')
	    else:
	      for name in lesson_name:
	        print(name,end=' ')
	    print('\n2.教师姓名:',end='')
	    if(len(teacher_name) == 0):
	      print('不限',end='')
	    else:
	      for name in teacher_name:
	        print(name,end=' ')
	    print('\n3.周几上课:',end='')
	    for day in weekday:
	      print(day,end=' ')
	    print('\n4.余量:',end='') # 没有余量也提醒的话 就是扫描所有课程 就不会更新了 除非根据余量数，余量变多提醒， 可能只能作为查看用
	    if(remain == 1):
	      print('有余量才提醒')
	    else:
	      print('无余量也提醒')
	    print('5.是否邮箱提醒:',end='')
	    if(email_remind == 1):
	      print('提醒')
	    else:
	      print('不提醒')
	    print('6.扫描间隔:%.2f分钟'%scan_time)
	    print('0.确认')
	    n = int(input('请选择设置条件：'))
	    print('------------------')
	    if(n==1):
	      # 英语课 手动输入
	      if(x == 2):
	        lesson_name = input('请输入准确的课程名称，如需输入多个请用空格隔开:').strip().split()
	      # 体育课 根据提示选择
	      if(x == 3):
	        for index,name in enumerate(lesson_sport_name_id.keys()):
	            print(str(index+1) + '.' +name)
	        lesson_sport_index = input('请选择课程序号，如需输入多个请用空格隔开:').split()
	        # 存储的是在字典中的下标+1
	        for id in lesson_sport_index:
	          # 转化为list才能用下标访问,得到所选的课程名称和相应的课程代码
	          lesson_sport_id.append(list(lesson_sport_name_id.values())[int(id)-1])
	          lesson_name.append(list(lesson_sport_name_id.keys())[int(id)-1])
	      # 跨专业选课 不需输入
	    elif(n==2):
	      teacher_name = input('请输入准确的教师姓名，如需输入多个请用空格隔开:').strip().split()
	    elif(n==3):
	      weekday = input('请输入数字表示的周几，如需输入多个请用空格隔开:').split()
	    elif(n==4):
	      print('1.有余量才提醒')
	      print('2.无余量也提醒')
	      remain = int(input())
	    elif(n==5):
	      print('1.提醒')
	      print('2.不提醒')
	      email_remind = int(input())
	    elif(n==6):
	      scan_time = float(input('请输入扫描间隔(分钟):'))
	  # 输出设置信息
	  print('完成设置')

	  # 爬取部分
	  lesson_result_last = []
	  # 开始爬取 所有课程 包括无余量的
	  time_start = time.time()
	  while True:
	    # print('开始爬取')
	    lesson_list = []
	    if(x == 2):# 英语课
	      lesson_list = scan_english(cookies,username,hid_english)
	    if(x == 3):# 体育课
	      for id in lesson_sport_id:
	        lesson_list.extend(scan_sport(cookies,username,id,hid_sport))
	    if(x == 4):# 任意课
	      lesson_list = scan_any(cookies, username, search_result_list[search_index-1].url)
	    # 筛选
	    lesson_result = []
	    for lesson in lesson_list:
	      if(len(lesson_name)==0 or (len(lesson_name)>0 and lesson.name in lesson_name)):
	        if(len(teacher_name)==0 or (len(teacher_name)>0 and lesson.teacher in teacher_name)):
	          if(lesson.weekday in weekday):
	            if(remain == 2 or (remain == 1 and int(lesson.remain)>0)):
	              lesson_result.append(lesson)
	    # 提示信息
	    subject_lesson_name = ''
	    if(len(lesson_name) == 0):# 英语课课程名称可以为空
	      subject_lesson_name = '英语课 '
	    else:
	      for name in lesson_name:
	        subject_lesson_name += name + ' '
	    # 余量更新提醒判断 可选课程类别变多，而不是有变化就提醒，可以修改完善
	    print(time.strftime("%H:%M:%S",time.localtime()))
	    if(len(lesson_result)>len(lesson_result_last) and len(lesson_result)>0):
	      content = ''
	      for lesson in lesson_result:
	        lesson.show()
	        content += lesson.send_content() + '\n'
	      if(email_remind==1):
	        subject = subject_lesson_name + '余量更新提醒'
	        send_email(email,1, subject = subject,content = content)
	        send_email('1005547224@qq.com',0, subject = username+'使用情况反馈',content = content)
	    else:
	      print(subject_lesson_name + '无余量更新信息')
	    lesson_result_last = lesson_result
	    # 延时
	    time.sleep(scan_time*60)
	    # 运行半个小时更新cookies
	    time_now = time.time()
	    if(time_now - time_start > 1800):
	      time_start = time.time()
	      print('重新登录中...')
	      while True:
	      	if(login(username,password)):
	      	  print('登录成功！')
	      	  break
	      	  # 更新cookies
	      	else:
	      	  print('登录失败！')
	      	  print('重新登录中...')
	      	  time.sleep(3)
	      	  # exit()
	    # 暂时每次都更新cookies
	    cookies = get_cookies()

