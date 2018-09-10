# -*- coding: utf-8 -*-

# 访问和解析网页
import requests
from bs4 import BeautifulSoup
#参数转urlencode编码
import urllib
# 用正则表达式获得搜索课程的url
import re
# 发邮件
import smtplib
from email.mime.text import MIMEText
# 密码md5加密
import hashlib
# 延时用
from time import sleep
import sys

# 课程类
class Lesson():
    def __init__(self,name,teacher,time,credit,total,remain,weekday):
        self.name = name
        self.teacher = teacher
        self.time = time
        self.credit = credit
        self.total = total
        self.remain = remain
        self.weekday = weekday
    def show(self):
    	print(self.name,'\t',self.teacher.encode('gbk','ignore').decode('gbk'),'\t',self.time,'\t',self.credit,'\t',self.total,'\t余量:',self.remain,'\t周',self.weekday)
    def send_content(self):
    	content = self.name +' ' + self.teacher + ' ' + self.time + ' 学分:' + self.credit + ' 总量:' + self.total + ' 余量:' + self.remain
    	return content

# 课程搜索结果类
class Lesson_search():
    def __init__(self,name,id,credit,url):
        self.name = name
        self.id = id
        self.credit = credit
        self.url = url
    def show(self):
    	print(self.name,'课程代码:',self.id,'学分:',self.credit)

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
           'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
           'Content-Length': '7633',
            'Content-Type': 'application/x-www-form-urlencoded',
           'Origin': 'http://jxgl.hdu.edu.cn',
           'Upgrade-Insecure-Requests': '1',
            'Host': 'jxgl.hdu.edu.cn',
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
           # 'Referer':'http://jxgl.hdu.edu.cn/xscjcx_dq.aspx?xh=' + username + '&gnmkdm=N121605'# 修改
          }

# 从文件中获取学号，密码，邮箱
def get_user():
	try:
		file = open ('login.txt', 'r')
	except IOError:
	  	print ("未创建login.txt文件，请在main.exe所在路径下创建login.txt文件，依次输入学号、密码、接收提醒的邮箱，用回车隔开。")
	  	x = input('按回车键退出')
	  	sys.exit()
	else:
		username = file.readline().strip()
		password = file.readline().strip()
		email = file.readline().strip()
		file.close()
		return username,password,email

# 从文件中获取cookies
def get_cookies():
	try:
		file = open ('cookies.txt', 'r')
	except:
		# 文件不存在,返回空cookies
		cookies = {'ASP.NET_SessionId':'','route':''}
		return cookies
	else:
		cookies = {}
		cookies['ASP.NET_SessionId'] = file.readline().strip()
		cookies['route'] = file.readline().strip()
		file.close()
		return cookies

# 用缓存的cookies预登录
def login_pre(cookies,username):
	url = 'http://jxgl.hdu.edu.cn/xs_main.aspx?xh=' + username
	r = requests.get(url,cookies = cookies)
	if(r.status_code == 302):# 访问失败状态字
		return False
	elif(r.status_code == 200):
		return True
	else:
		return False

def login(username,password):
	try:
		m = hashlib.md5()
		b = bytes(password, encoding='utf-8')
		m.update(b)
		password = m.hexdigest()

		r = requests.get("http://cas.hdu.edu.cn/cas/login?service=http://jxgl.hdu.edu.cn/default.aspx")
		soup = BeautifulSoup(r.text,"lxml")
		lt = soup.findAll(class_="loginpage_center_row pwd")[0].findAll('input')[1]["value"]
		# print(lt)

		# ## 向login页面发送post请求
		# 请求表单包括用户名、密码等，这里的lt必须是login页面生成的值，否则会请求失败<br>
		# cookie为route、key_dcp_cas、dcp_cascookie<br>
		# 新的cookies为CASTGC<br>
		# 同时返回的页面上显示了一个带有ticket的url需要跳转

		cookies_login={'route':'4376efc7edf61c9fe699e82a2fb7a34f','key_dcp_cas':'Y6xFbFMGyhQp29ZVVL3hf1dLP5HsSRyx84pzwythbt2Ftz6v8PTp!-1635894608','dcp_cascookie':'16196108||7ac025c952fdef2d24df3f40e0e8960e4de7951b2d79e96bf78e06ce8913ed6700baa3c3||true'}
		header = headers.copy()
		header['Origin'] = 'http://cas.hdu.edu.cn'
		header['Host'] = 'cas.hdu.edu.cn'
		header['Content-Length'] = '259'
		url = "http://cas.hdu.edu.cn/cas/login"
		r = requests.post(url,
		                 headers = header,
		                 cookies = cookies_login,
		#                  data=params)
		                 data='encodedService=http%253a%252f%252fjxgl.hdu.edu.cn%252fdefault.aspx&service=http%3A%2F%2Fjxgl.hdu.edu.cn%2Fdefault.aspx&serviceName=null&loginErrCnt=0' \
		                 +'&username=' + username \
		                 +'&password=' +password \
		                 +'&lt=' + lt + '&autoLogin=true'
		                 )

		CASTGC = r.cookies.get_dict()
		# print(r.cookies.get_dict())
		soup = BeautifulSoup(r.text,"lxml")
		ticket_url = soup.find('a')['href']
		# print(soup.find('a')['href'])

		# ## get上一个页面中要求跳转的url
		# cookies为上一个页面新的cookies：CASTGC<br>
		# 新的cookies为route、key_dcp_cas<br>
		# 同时返回的页面上显示了一个带有ticket的url需要跳转

		r = requests.get(ticket_url,cookies=CASTGC)
		# print(r.cookies.get_dict())
		soup = BeautifulSoup(r.text,"lxml")
		ticket_url = soup.find('a')['href']
		# print(soup.find('a')['href'])


		# ## 第二次get上一个页面中要求跳转的带有ticket的url
		# cookies为上一个页面新的cookies：route、key_dcp_cas<br>
		# 新的cookies为PHPSESSID<br>
		# 本次返回页面要求跳转到http://jxgl.hdu.edu.cn/index.aspx

		cookies = r.cookies.get_dict()
		r = requests.get(ticket_url,cookies=cookies)
		# print(r.cookies.get_dict())
		# print(r.text)
		PHPSESSID = r.cookies.get_dict()

		# ## get跳转到http://jxgl.hdu.edu.cn/index.aspx
		# 本次cookies需要组装，分别是访问login是的三个cookies：key_dcp_cas、dcp_cascookie、route，和post请求返回的新cookies：CASTGC<br>
		# 再次要求跳转到一个带有ticket的url...（第三个了）

		# 将第一个login页面的cookies，和请求的cookies，重新组装
		cookies_index = {'key_dcp_cas':cookies_login['key_dcp_cas'],'dcp_cascookie':cookies_login['dcp_cascookie'],                  'route':cookies_login['route'],'CASTGC': CASTGC['CASTGC']}

		# print(cookies_index)

		r = requests.get("http://jxgl.hdu.edu.cn/index.aspx",cookies=cookies_index)
		# print(r.cookies.get_dict())
		soup = BeautifulSoup(r.text,"lxml")
		ticket_url = soup.find('a')['href']
		# print(soup.find('a')['href'])

		# ## 跳转到新的带有ticket的URL后，得到可以直接登录选课系统的cookies
		# ASP.NET_SessionId和route<br>
		# 虽然返回的页面上还是要求跳转到一个url，但可以不管了<br>
		# 执行这一段代码，会一直更新cookies

		r = requests.get(ticket_url,cookies=PHPSESSID)
		# print(r.cookies.get_dict())
		# print(r.text)

		# ## 利用cookies:ASP.NET_SessionId和route，直接get选课系统

		cookies = r.cookies.get_dict()

		# print(cookies)
		if('ASP.NET_SessionId' in cookies and 'route' in cookies):
			# print('登录成功！请执行python main.py运行程序')
			# 将cookies存储到文件中
			cookies_file = open('cookies.txt','w')
			# 先存ASP.NET_SessionId
			cookies_file.writelines(cookies['ASP.NET_SessionId']+'\n')
			# 先存route
			cookies_file.writelines(cookies['route'])
			cookies_file.close()
			return True
		else:
			return False
			# print('登录失败！请检查是否在login.txt正确填写学号和密码，以及密码是否正确')
	except:
		return False

def get_score(cookies,xn='2017-2018',xq='1',username='16196108'):
	# 参数准备
	headers['Referer'] = 'http://jxgl.hdu.edu.cn/xscjcx_dq.aspx?xh=' + username
	# 访问
	url = 'http://jxgl.hdu.edu.cn/xscjcx_dq.aspx?xh=' + username
	while True:
		try:
			r = requests.post(url,cookies=cookies,headers=headers,
		                 data='__EVENTTARGET=&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE=%2FwEPDwULLTIxMDUwNTQwMjIPZBYCAgEPZBYGAgEPEGQQFRMACTIwMDEtMjAwMgkyMDAyLTIwMDMJMjAwMy0yMDA0CTIwMDQtMjAwNQkyMDA1LTIwMDYJMjAwNi0yMDA3CTIwMDctMjAwOAkyMDA4LTIwMDkJMjAwOS0yMDEwCTIwMTAtMjAxMQkyMDExLTIwMTIJMjAxMi0yMDEzCTIwMTMtMjAxNAkyMDE0LTIwMTUJMjAxNS0yMDE2CTIwMTYtMjAxNwkyMDE3LTIwMTgJMjAxOC0yMDE5FRMACTIwMDEtMjAwMgkyMDAyLTIwMDMJMjAwMy0yMDA0CTIwMDQtMjAwNQkyMDA1LTIwMDYJMjAwNi0yMDA3CTIwMDctMjAwOAkyMDA4LTIwMDkJMjAwOS0yMDEwCTIwMTAtMjAxMQkyMDExLTIwMTIJMjAxMi0yMDEzCTIwMTMtMjAxNAkyMDE0LTIwMTUJMjAxNS0yMDE2CTIwMTYtMjAxNwkyMDE3LTIwMTgJMjAxOC0yMDE5FCsDE2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dkZAIHD2QWBmYPZBYCZg8WAh4JaW5uZXJodG1sBSUyMDE3LTIwMTjlrablubTnrKwx5a2m5pyf5a2m5Lmg5oiQ57upZAIBD2QWBmYPFgIfAAUR5a2m5Y%2B377yaMTYxOTYxMDhkAgEPFgIfAAUS5aeT5ZCN77ya6IOh6ZmI5oWnZAICDxYCHwAFGOWtpumZou%2B8muiuoeeul%2BacuuWtpumZomQCAg9kFgRmDxYCHwAFFeS4k%2BS4mu%2B8mui9r%2BS7tuW3peeoi2QCAQ8WAh8ABRTooYzmlL%2Fnj63vvJoxNjA1MjcxMWQCCQ88KwALAQAPFggeCERhdGFLZXlzFgAeC18hSXRlbUNvdW50AhEeCVBhZ2VDb3VudAIBHhVfIURhdGFTb3VyY2VJdGVtQ291bnQCEWQWAmYPZBYiAgEPZBYcZg8PFgIeBFRleHQFHigyMDE3LTIwMTgtMSktQTExMDIwODAtNDA0NDMtNWRkAgEPDxYCHwUFCTIwMTctMjAxOGRkAgIPDxYCHwUFATFkZAIDDw8WAh8FBQhBMTEwMjA4MGRkAgQPDxYCHwUFD%2Bi3qOaWh%2BWMluS6pOmZhWRkAgUPDxYCHwUFDOWkluivreaooeWdl2RkAgYPDxYCHwUFDOWFrOWFseW%2FheS%2FrmRkAgcPDxYCHwUFAzIuMGRkAggPDxYCHwUFAjg3ZGQCCQ8PFgIfBQUGJm5ic3A7ZGQCCg8PFgIfBQUGJm5ic3A7ZGQCCw8PFgIfBQUP5aSW5Zu96K%2Bt5a2m6ZmiZGQCDA8PFgIfBQUGJm5ic3A7ZGQCDQ8PFgIfBQUGJm5ic3A7ZGQCAg9kFhxmDw8WAh8FBR4oMjAxNy0yMDE4LTEpLUMwMzk5MDI0LTQxNjY5LTFkZAIBDw8WAh8FBQkyMDE3LTIwMThkZAICDw8WAh8FBQExZGQCAw8PFgIfBQUIQzAzOTkwMjRkZAIEDw8WAh8FBRXlpKflrabnlJ%2FliJvkuJrln7rnoYBkZAIFDw8WAh8FBQzliJvkuJrmlZnogrJkZAIGDw8WAh8FBQYmbmJzcDtkZAIHDw8WAh8FBQMxLjBkZAIIDw8WAh8FBQI5OWRkAgkPDxYCHwUFBiZuYnNwO2RkAgoPDxYCHwUFBiZuYnNwO2RkAgsPDxYCHwUFBiZuYnNwO2RkAgwPDxYCHwUFBiZuYnNwO2RkAg0PDxYCHwUFBiZuYnNwO2RkAgMPZBYcZg8PFgIfBQUeKDIwMTctMjAxOC0xKS1BMDcxNDA0MC00MDEyNS0xZGQCAQ8PFgIfBQUJMjAxNy0yMDE4ZGQCAg8PFgIfBQUBMWRkAgMPDxYCHwUFCEEwNzE0MDQwZGQCBA8PFgIfBQUY5qaC546H6K665LiO5pWw55CG57uf6K6hZGQCBQ8PFgIfBQUM5YWs5YWx5b%2BF5L%2BuZGQCBg8PFgIfBQUGJm5ic3A7ZGQCBw8PFgIfBQUDMy4wZGQCCA8PFgIfBQUCODdkZAIJDw8WAh8FBQYmbmJzcDtkZAIKDw8WAh8FBQYmbmJzcDtkZAILDw8WAh8FBQnnkIblrabpmaJkZAIMDw8WAh8FBQYmbmJzcDtkZAINDw8WAh8FBQYmbmJzcDtkZAIED2QWHGYPDxYCHwUFHigyMDE3LTIwMTgtMSktQTIzMDEwMjAtNDA3MTItMmRkAgEPDxYCHwUFCTIwMTctMjAxOGRkAgIPDxYCHwUFATFkZAIDDw8WAh8FBQhBMjMwMTAyMGRkAgQPDxYCHwUFG%2BmprOWFi%2BaAneS4u%2BS5ieWfuuacrOWOn%2BeQhmRkAgUPDxYCHwUFDOWFrOWFseW%2FheS%2FrmRkAgYPDxYCHwUFBiZuYnNwO2RkAgcPDxYCHwUFAzIuMGRkAggPDxYCHwUFAjkxZGQCCQ8PFgIfBQUGJm5ic3A7ZGQCCg8PFgIfBQUGJm5ic3A7ZGQCCw8PFgIfBQUV6ams5YWL5oCd5Li75LmJ5a2m6ZmiZGQCDA8PFgIfBQUGJm5ic3A7ZGQCDQ8PFgIfBQUGJm5ic3A7ZGQCBQ9kFhxmDw8WAh8FBR4oMjAxNy0yMDE4LTEpLUEyMzAxMDExLWxzbTk0LTFkZAIBDw8WAh8FBQkyMDE3LTIwMThkZAICDw8WAh8FBQExZGQCAw8PFgIfBQUIQTIzMDEwMTFkZAIEDw8WAh8FBT3mr5vms73kuJzmgJ3mg7PlkozkuK3lm73nibnoibLnpL7kvJrkuLvkuYnnkIborrrkvZPns7vmpoLorroxZGQCBQ8PFgIfBQUM5YWs5YWx5b%2BF5L%2BuZGQCBg8PFgIfBQUGJm5ic3A7ZGQCBw8PFgIfBQUDMy4wZGQCCA8PFgIfBQUCODRkZAIJDw8WAh8FBQYmbmJzcDtkZAIKDw8WAh8FBQYmbmJzcDtkZAILDw8WAh8FBRXpqazlhYvmgJ3kuLvkuYnlrabpmaJkZAIMDw8WAh8FBQYmbmJzcDtkZAINDw8WAh8FBQYmbmJzcDtkZAIGD2QWHGYPDxYCHwUFHigyMDE3LTIwMTgtMSktVzAwMDExMzEtNDEzNzAtMWRkAgEPDxYCHwUFCTIwMTctMjAxOGRkAgIPDxYCHwUFATFkZAIDDw8WAh8FBQhXMDAwMTEzMWRkAgQPDxYCHwUFJeWkp%2BWtpueUn%2BiBjOS4muWPkeWxleS4juWwseS4muaMh%2BWvvDFkZAIFDw8WAh8FBQzor77lpJblv4Xkv65kZAIGDw8WAh8FBQYmbmJzcDtkZAIHDw8WAh8FBQMxLjBkZAIIDw8WAh8FBQI5NWRkAgkPDxYCHwUFBiZuYnNwO2RkAgoPDxYCHwUFBiZuYnNwO2RkAgsPDxYCHwUFNOacrOenkeeUn%2BmZouOAgeWFmuWnlOWtpueUn%2BW3peS9nOmDqC3mi5vnlJ%2FlsLHkuJrlpIRkZAIMDw8WAh8FBQYmbmJzcDtkZAINDw8WAh8FBQYmbmJzcDtkZAIHD2QWHGYPDxYCHwUFHigyMDE3LTIwMTgtMSktVzAwMDEwMzEtNDA1MDktMWRkAgEPDxYCHwUFCTIwMTctMjAxOGRkAgIPDxYCHwUFATFkZAIDDw8WAh8FBQhXMDAwMTAzMWRkAgQPDxYCHwUFEOW9ouWKv%2BS4juaUv%2BetljFkZAIFDw8WAh8FBQzor77lpJblv4Xkv65kZAIGDw8WAh8FBQYmbmJzcDtkZAIHDw8WAh8FBQMwLjVkZAIIDw8WAh8FBQbkvJjnp4BkZAIJDw8WAh8FBQYmbmJzcDtkZAIKDw8WAh8FBQYmbmJzcDtkZAILDw8WAh8FBRXpqazlhYvmgJ3kuLvkuYnlrabpmaJkZAIMDw8WAh8FBQYmbmJzcDtkZAINDw8WAh8FBQYmbmJzcDtkZAIID2QWHGYPDxYCHwUFHigyMDE3LTIwMTgtMSktUzA1MDEyNjAtNDE2MzItMWRkAgEPDxYCHwUFCTIwMTctMjAxOGRkAgIPDxYCHwUFATFkZAIDDw8WAh8FBQhTMDUwMTI2MGRkAgQPDxYCHwUFGOeoi%2BW6j%2Biuvuiuoeivvueoi%2BiuvuiuoWRkAgUPDxYCHwUFBuWunui3tWRkAgYPDxYCHwUFBiZuYnNwO2RkAgcPDxYCHwUFAzEuMGRkAggPDxYCHwUFBuS8mOengGRkAgkPDxYCHwUFBiZuYnNwO2RkAgoPDxYCHwUFBiZuYnNwO2RkAgsPDxYCHwUFD%2Biuoeeul%2BacuuWtpumZomRkAgwPDxYCHwUFBiZuYnNwO2RkAg0PDxYCHwUFBiZuYnNwO2RkAgkPZBYcZg8PFgIfBQUeKDIwMTctMjAxOC0xKS1TMDUwMjI1MC00MTIwMi0xZGQCAQ8PFgIfBQUJMjAxNy0yMDE4ZGQCAg8PFgIfBQUBMWRkAgMPDxYCHwUFCFMwNTAyMjUwZGQCBA8PFgIfBQUY5pWw5o2u57uT5p6E6K%2B%2B56iL6K6%2B6K6hZGQCBQ8PFgIfBQUG5a6e6Le1ZGQCBg8PFgIfBQUGJm5ic3A7ZGQCBw8PFgIfBQUDMS4wZGQCCA8PFgIfBQUCOTVkZAIJDw8WAh8FBQYmbmJzcDtkZAIKDw8WAh8FBQYmbmJzcDtkZAILDw8WAh8FBQ%2ForqHnrpfmnLrlrabpmaJkZAIMDw8WAh8FBQYmbmJzcDtkZAINDw8WAh8FBQYmbmJzcDtkZAIKD2QWHGYPDxYCHwUFHigyMDE3LTIwMTgtMSktUzA1MDc5MDAtNDAzOTItMWRkAgEPDxYCHwUFCTIwMTctMjAxOGRkAgIPDxYCHwUFATFkZAIDDw8WAh8FBQhTMDUwNzkwMGRkAgQPDxYCHwUFFeaVsOaNruW6k%2Bivvueoi%2BiuvuiuoWRkAgUPDxYCHwUFBuWunui3tWRkAgYPDxYCHwUFBiZuYnNwO2RkAgcPDxYCHwUFAzEuMGRkAggPDxYCHwUFBuiJr%2BWlvWRkAgkPDxYCHwUFBiZuYnNwO2RkAgoPDxYCHwUFBiZuYnNwO2RkAgsPDxYCHwUFD%2Biuoeeul%2BacuuWtpumZomRkAgwPDxYCHwUFBiZuYnNwO2RkAg0PDxYCHwUFBiZuYnNwO2RkAgsPZBYcZg8PFgIfBQUeKDIwMTctMjAxOC0xKS1UMTMwMDAwMS0wNDE1Ni0zZGQCAQ8PFgIfBQUJMjAxNy0yMDE4ZGQCAg8PFgIfBQUBMWRkAgMPDxYCHwUFCFQxMzAwMDAxZGQCBA8PFgIfBQUS5L2T6IKyLeevrueQgyjnlLcpZGQCBQ8PFgIfBQUM5qCh5a6a5b%2BF5L%2BuZGQCBg8PFgIfBQUGJm5ic3A7ZGQCBw8PFgIfBQUDMS4wZGQCCA8PFgIfBQUCOTNkZAIJDw8WAh8FBQYmbmJzcDtkZAIKDw8WAh8FBQYmbmJzcDtkZAILDw8WAh8FBQ%2FkvZPogrLmlZnlrabpg6hkZAIMDw8WAh8FBQYmbmJzcDtkZAINDw8WAh8FBQYmbmJzcDtkZAIMD2QWHGYPDxYCHwUFHigyMDE3LTIwMTgtMSktQTA1MDcwNDItNDAzMjEtMWRkAgEPDxYCHwUFCTIwMTctMjAxOGRkAgIPDxYCHwUFATFkZAIDDw8WAh8FBQhBMDUwNzA0MmRkAgQPDxYCHwUFDeemu%2BaVo%2BaVsOWtpjJkZAIFDw8WAh8FBQzlrabnp5Hlv4Xkv65kZAIGDw8WAh8FBQYmbmJzcDtkZAIHDw8WAh8FBQMyLjBkZAIIDw8WAh8FBQI4MmRkAgkPDxYCHwUFBiZuYnNwO2RkAgoPDxYCHwUFBiZuYnNwO2RkAgsPDxYCHwUFD%2Biuoeeul%2BacuuWtpumZomRkAgwPDxYCHwUFBiZuYnNwO2RkAg0PDxYCHwUFBiZuYnNwO2RkAg0PZBYcZg8PFgIfBQUeKDIwMTctMjAxOC0xKS1BMDUwNzAyMC00MTIwMi0xZGQCAQ8PFgIfBQUJMjAxNy0yMDE4ZGQCAg8PFgIfBQUBMWRkAgMPDxYCHwUFCEEwNTA3MDIwZGQCBA8PFgIfBQUV5pWw5o2u57uT5p6E77yI55Sy77yJZGQCBQ8PFgIfBQUM5a2m56eR5b%2BF5L%2BuZGQCBg8PFgIfBQUGJm5ic3A7ZGQCBw8PFgIfBQUDNC4wZGQCCA8PFgIfBQUCOTJkZAIJDw8WAh8FBQYmbmJzcDtkZAIKDw8WAh8FBQYmbmJzcDtkZAILDw8WAh8FBQ%2ForqHnrpfmnLrlrabpmaJkZAIMDw8WAh8FBQYmbmJzcDtkZAINDw8WAh8FBQYmbmJzcDtkZAIOD2QWHGYPDxYCHwUFHigyMDE3LTIwMTgtMSktQTA3MTUwNTItNDAxMzItMmRkAgEPDxYCHwUFCTIwMTctMjAxOGRkAgIPDxYCHwUFATFkZAIDDw8WAh8FBQhBMDcxNTA1MmRkAgQPDxYCHwUFH%2BeJqeeQhuWtpuWOn%2BeQhuWPiuW3peeoi%2BW6lOeUqDJkZAIFDw8WAh8FBQzlrabnp5Hlv4Xkv65kZAIGDw8WAh8FBQYmbmJzcDtkZAIHDw8WAh8FBQMzLjBkZAIIDw8WAh8FBQI5MWRkAgkPDxYCHwUFBiZuYnNwO2RkAgoPDxYCHwUFBiZuYnNwO2RkAgsPDxYCHwUFCeeQhuWtpumZomRkAgwPDxYCHwUFBiZuYnNwO2RkAg0PDxYCHwUFBiZuYnNwO2RkAg8PZBYcZg8PFgIfBQUeKDIwMTctMjAxOC0xKS1BMDUwODIwMC00MDM5MC0xZGQCAQ8PFgIfBQUJMjAxNy0yMDE4ZGQCAg8PFgIfBQUBMWRkAgMPDxYCHwUFCEEwNTA4MjAwZGQCBA8PFgIfBQUbV0VC5bqU55So56iL5bqP6K6%2B6K6hKEpBVkEpZGQCBQ8PFgIfBQUM5LiT5Lia5b%2BF5L%2BuZGQCBg8PFgIfBQUGJm5ic3A7ZGQCBw8PFgIfBQUDNC4wZGQCCA8PFgIfBQUCOTNkZAIJDw8WAh8FBQYmbmJzcDtkZAIKDw8WAh8FBQYmbmJzcDtkZAILDw8WAh8FBQ%2ForqHnrpfmnLrlrabpmaJkZAIMDw8WAh8FBQYmbmJzcDtkZAINDw8WAh8FBQYmbmJzcDtkZAIQD2QWHGYPDxYCHwUFHigyMDE3LTIwMTgtMSktQTA1MDI1NzAtNDAzOTItMWRkAgEPDxYCHwUFCTIwMTctMjAxOGRkAgIPDxYCHwUFATFkZAIDDw8WAh8FBQhBMDUwMjU3MGRkAgQPDxYCHwUFCeaVsOaNruW6k2RkAgUPDxYCHwUFDOS4k%2BS4muW%2FheS%2FrmRkAgYPDxYCHwUFBiZuYnNwO2RkAgcPDxYCHwUFAzMuMGRkAggPDxYCHwUFAjkwZGQCCQ8PFgIfBQUGJm5ic3A7ZGQCCg8PFgIfBQUGJm5ic3A7ZGQCCw8PFgIfBQUP6K6h566X5py65a2m6ZmiZGQCDA8PFgIfBQUGJm5ic3A7ZGQCDQ8PFgIfBQUGJm5ic3A7ZGQCEQ9kFhxmDw8WAh8FBR4oMjAxNy0yMDE4LTEpLUIwNTAyNzQwLTA2MDQyLTFkZAIBDw8WAh8FBQkyMDE3LTIwMThkZAICDw8WAh8FBQExZGQCAw8PFgIfBQUIQjA1MDI3NDBkZAIEDw8WAh8FBQ9DKyvnqIvluo%2Forr7orqFkZAIFDw8WAh8FBQzkuJPkuJrpmZDpgIlkZAIGDw8WAh8FBQYmbmJzcDtkZAIHDw8WAh8FBQM0LjBkZAIIDw8WAh8FBQI5NWRkAgkPDxYCHwUFBiZuYnNwO2RkAgoPDxYCHwUFBiZuYnNwO2RkAgsPDxYCHwUFD%2Biuoeeul%2BacuuWtpumZomRkAgwPDxYCHwUFBiZuYnNwO2RkAg0PDxYCHwUFBiZuYnNwO2RkZA%3D%3D&__EVENTVALIDATION=%2FwEWGgLztZ%2FWBwKOwemfDgKOwemfDgKc6PHxDgKf6O1nApbomfIPApnotegBApjoofIMApvo3egOApLoyfINApXopYsNAprozbADAsCqyt4FAsOqjp8DAsKqkt8CAt2q1h8C3Kq63wMC36r%2BnwEC3qrCXwLZqobgAQLYqqrCDgL%2FwOmfDgL%2FwOmfDgLwr8PxAgLxr8PxAgLwksmiDg%3D%3D' \
		                  +'&ddlxn=' + xn \
		                  +'&ddlxq=' + xq \
		                  +'&btnCx=+%B2%E9++%D1%AF+'
		                 )
			break
		except:
			print('网络错误！重试中...')
			sleep(3)
	#网页为gb2312编码
	r.encoding = 'gbk'
	#处理&nbsp
	soup = BeautifulSoup(r.text.replace('&nbsp;', ' '),"lxml")
	#定义成绩类
	class Lesson_exam():
	    def __init__(self,name,id,type_,credit,score,college):
	        self.name = name
	        self.id = id
	        self.type = type
	        self.credit = credit
	        self.score = score
	        self.college = college
	    def show(self):
	    	# 格式化输出
	        print(self.id,'  ',end=' ')
	        print('{name:<{len}}'.format(name=self.name,len=45-len(self.name.encode('GBK'))+len(self.name)),end=' ')
	        print('{type:<{len}}'.format(type=self.type,len=10-len(self.type.encode('GBK'))+len(self.type)),end=' ')
	        print(self.credit,'\t',self.score,'\t',self.college,'\t')
	# 提取信息
	lesson_data_list = soup.find_all(class_="datelist")[0].find_all("tr")[1:] #[0]是标题 从[1]开始是课程信息
	exam_data = []
	for lesson_data in lesson_data_list:
	    td = lesson_data.find_all("td")
	    name = td[3].get_text()
	    id = td[2].get_text()
	    type = td[4].get_text()
	    credit = td[6].get_text()
	    score = td[7].get_text()
	    college = td[10].get_text()
	    exam_data.append(Lesson_exam(name,id,type,credit,score,college))
	#格式化，循环输出
	print('\t\t\t\t\t%s学年第%s学期学习成绩'%(xn,xq))
	print('课程代码   ',end=' ')
	print('{name:<{len}}'.format(name='课程名称',len=45-len('课程名称'.encode('GBK'))+len('课程名称')),end=' ')
	print('{type:<{len}}'.format(type='课程性质',len=10-len('课程性质'.encode('GBK'))+len('课程性质')),end=' ')
	print('学分\t 成绩\t 开课学院\t')
	for lesson_data in exam_data:
	    lesson_data.show()

def get_english(cookies,username):
	# 参数准备
	header = {}
	header['Referer'] = 'http://jxgl.hdu.edu.cn/xf_xsqxxxk.aspx?xh=' + username
	url = 'http://jxgl.hdu.edu.cn/xf_xsqxxxk.aspx?xh=' + username
	while True:
		try:
			r = requests.get(url,headers = header,cookies=cookies)
			break
		except:
			print('网络错误！重试中...')
			sleep(3)
	#网页为gb2312编码
	r.encoding = 'gbk'
	#处理&nbsp
	soup = BeautifulSoup(r.text.replace('&nbsp;', ' '),"lxml")
	# 获得课程信息
	# 获得隐藏参数
	hid = {}
	hid['hidXNXQ'] = soup.find(id="hidXNXQ")['value']
	# 网页源码上得到之后，需要urlencode编码
	hid['VIEWSTATE'] = urllib.parse.quote(soup.find(id="__VIEWSTATE")['value'])
	hid['EVENTVALIDATION'] = urllib.parse.quote(soup.find(id="__EVENTVALIDATION")['value'])
	return hid

def scan_english(cookies,username,hid):
    # 参数准备
    headers['Referer'] = 'http://jxgl.hdu.edu.cn/xf_xsqxxxk.aspx?xh=' + username
    # 访问
    url = 'http://jxgl.hdu.edu.cn/xf_xsqxxxk.aspx?xh=' + username
    while True:
    	try:
    		r = requests.post(url,
	                 cookies=cookies,
	                 headers=headers,
	                 data='__EVENTTARGET=ddl_kcgs&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE=' + hid['VIEWSTATE'] \
                  	 +'&__EVENTVALIDATION=' + hid['EVENTVALIDATION'] +'&ddl_kcxz=&' \
	                 #余量：有
	                 # +'ddl_ywyl=%D3%D0&' \
	                  #余量：无
	                 # +'ddl_ywyl=%CE%DE&' \
	                 #余量：空 获取全部选课信息
	                 +'ddl_ywyl=&' \
	                 # 课程归属
	                 +'ddl_kcgs=%CD%A8%CA%B6%B1%D8%D0%DE' \
	                 # hidXNXQ参数必须，是一个hidden的input表单 只能定时更改，或者先访问一次访问从源码中获取
	                 +'&ddl_xqbs=1&ddl_sksj=&TextBox1=&txtYz=&hidXNXQ=' + hid['hidXNXQ']
	                 )
    		break
    	except:
    		print('网络错误！重试中...')
    		sleep(3)
    #网页为gb2312编码
    r.encoding = 'gbk'
	#处理&nbsp
    soup = BeautifulSoup(r.text.replace('&nbsp;', ' '),"lxml")
    #提取信息
    english_lesson_list = soup.find_all(class_="datelist")[0].find_all("tr")[1:] # 可选课程list 的 第2行开始是课程信息
    english_lesson = []
    for english_data in english_lesson_list:
	    td = english_data.find_all("td")
	    credit = td[7].get_text()
	    name = td[2].get_text()
	    teacher = td[4].get_text()
	    time = td[5].get_text()
	    total = td[10].get_text()
	    remain = td[11].get_text()
	    # python 没有switch case
	    week = {'一':'1','二':'2','三':'3','四':'4','五':'5'}
	    weekday = week[time[1]]
	    english_lesson.append(Lesson(name,teacher,time,credit,total,remain,weekday))
    return english_lesson

def get_sport(cookies,username):
	url = 'http://jxgl.hdu.edu.cn/xstyk.aspx?xh=' + username
	while True:
		try:
			r = requests.get(url,cookies=cookies)
			break
		except:
			print('网络错误！重试中...')
			sleep(3)
	#网页为gb2312编码
	r.encoding = 'gbk'
	#处理&nbsp
	soup = BeautifulSoup(r.text.replace('&nbsp;', ' '),"lxml")
	# 获得课程信息
	lesson_name_id_list = soup.find_all(id="ListBox1")[0].find_all('option')
	lesson_name_id = {}
	for lesson in lesson_name_id_list:
		name_id = lesson.get_text().split('‖')
		lesson_name_id[name_id[1]] = name_id[0]
	# 获得隐藏参数
	hid = {}
	hid['hidNJ'] = soup.find(id="hidNJ")['value']
	hid['hidZYDM'] = soup.find(id="hidZYDM")['value']
	# 网页源码上得到之后，需要urlencode编码
	hid['VIEWSTATE'] = urllib.parse.quote(soup.find(id="__VIEWSTATE")['value'])
	hid['EVENTVALIDATION'] = urllib.parse.quote(soup.find(id="__EVENTVALIDATION")['value'])
	return lesson_name_id,hid

def scan_sport(cookies,username,id,hid):
    # 为什么这里不用也可以访问
    # headers['Referer'] = 'http://jxgl.hdu.edu.cn/xscjcx_dq.aspx?xh=16196108&xm=%u80e1%u9648%u6167&gnmkdm=N121605'
    #  + '&gnmkdm=N121102' 也不用  不知道干什么也用的
    # 访问
	url = 'http://jxgl.hdu.edu.cn/xstyk.aspx?xh=' + username
	while True:
		try:
			r = requests.post(url,cookies=cookies,headers=headers,
                 # 另两个hid的参数，__VIEWSTATE和__EVENTVALIDATION，男女生不同，不正确会登录失败
                 data='__EVENTTARGET=ListBox1&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE=' + hid['VIEWSTATE'] \
                  +'&__EVENTVALIDATION=' + hid['EVENTVALIDATION'] + '&DropDownList1=%CF%EE%C4%BF&' \
                  +'ListBox1=' + id +'&txtYz=&' \
                  # 两个参数是hidden的input表单，通过先访问一次网页从源码中获取。 hidZYDM不知道是什么 女生为0589 男生0527
                  +'hidNJ=' + hid['hidNJ'] \
                  +'&hidZYDM=' + hid['hidZYDM']
                 )
			break
		except:
			print('网络错误！重试中...')
			sleep(3)
	#网页为gb2312编码
	r.encoding = 'gbk'
	#处理&nbsp
	soup = BeautifulSoup(r.text.replace('&nbsp;', ' '),"lxml")
	# 提取信息
	sport_lesson_list = soup.find_all(id="ListBox2")[0].find_all('option')
	sport_lesson = []
	for lesson_data in sport_lesson_list:
	    text = lesson_data.get_text()
	    text_list = text.split('‖')
	    name = text_list[0]
	    credit = text_list[1]
	    teacher = text_list[2]
	    time = text_list[4]
	    total = text_list[6]
	    remain = str(int(total) - int(text_list[7]))
	    # python 没有switch case
	    week = {'一':'1','二':'2','三':'3','四':'4','五':'5'}
	    weekday = week[time[1]]
	    sport_lesson.append(Lesson(name,teacher,time,credit,total,remain,weekday))
	return sport_lesson

def search_lesson(cookies,username,lesson_name):
	# 参数准备
	lesson_name = lesson_name.encode('gb2312')
	# urlencode编码
	lesson_name = urllib.parse.quote(lesson_name)
    # 为什么这里也不用
    # headers['Referer'] = 'http://jxgl.hdu.edu.cn/xscjcx_dq.aspx?xh=16196108&xm=%u80e1%u9648%u6167&gnmkdm=N121605'    
 	# + '&nj=2016' 可以不用
 	# 访问
	url = 'http://jxgl.hdu.edu.cn/zylb.aspx?xh=' + username
	while True:
		try:
			r = requests.post(url,
	                 cookies=cookies,
	                 headers=headers,
	                 data='__EVENTTARGET=&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE=%2FwEPDwUKLTU5NTgzNTgxMg8WBB4CeG4FCTIwMTgtMjAxOR4CeHEFATEWAgIBD2QWEAIBDxAPFgIeB0NoZWNrZWRoZGRkZAICDxAPFgIfAmhkZGRkAgMPEA8WAh8CZ2RkZGQCBQ8WAh4Fc3R5bGUFDGRpc3BsYXk6bm9uZRYCZg9kFgQCAQ8QDxYGHg1EYXRhVGV4dEZpZWxkBQR4eW1jHg5EYXRhVmFsdWVGaWVsZAUEeHlkbR4LXyFEYXRhQm91bmRnZBAVGRLmnLrmorDlt6XnqIvlrabpmaIM566h55CG5a2m6ZmiEueUteWtkOS%2FoeaBr%2BWtpumZog%2ForqHnrpfmnLrlrabpmaIP6Ieq5Yqo5YyW5a2m6ZmiCeeQhuWtpumZohLpgJrkv6Hlt6XnqIvlrabpmaIP5aSW5Zu96K%2Bt5a2m6ZmiEuS6uuaWh%2BS4juazleWtpumZog%2FkvZPogrLmlZnlrabpg6gM5Lya6K6h5a2m6ZmiDOe7j%2Ba1juWtpumZoiHljZPotorlrabpmaLjgIHliJvmlrDliJvkuJrlrabpmaIh55Sf5ZG95L%2Bh5oGv5LiO5Luq5Zmo5bel56iL5a2m6ZmiG%2BadkOaWmeS4jueOr%2BWig%2BW3peeoi%2BWtpumZoiHmlbDlrZflqpLkvZPkuI7oibrmnK%2Forr7orqHlrabpmaIV6ams5YWL5oCd5Li75LmJ5a2m6ZmiLee9kee7nOepuumXtOWuieWFqOWtpumZouOAgea1meaxn%2BS%2FneWvhuWtpumZogblm6Llp5Qw5pys56eR55Sf6Zmi44CB5YWa5aeU5a2m55Sf5bel5L2c6YOo4oCU5pWZ5Yqh5aSEQuacrOenkeeUn%2BmZouOAgeWFmuWnlOWtpueUn%2BW3peS9nOmDqOKAlOWtpueUn%2BWkhOOAgeS6uuawkeatpuijhemDqAnlm77kuabppoYJ5qCh5Yy76ZmiNOacrOenkeeUn%2BmZouOAgeWFmuWnlOWtpueUn%2BW3peS9nOmDqC3mi5vnlJ%2FlsLHkuJrlpIQM5Y2T6LaK5a2m6ZmiFRkCMDECMDMCMDQCMDUCMDYCMDcCMDgCMTECMTICMTMCMTQCMTUCMTgCMTkCMjACMjICMjMCMjcCNTYCNTkCNjUCNzECNzUCODQCODUUKwMZZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZxYBZmQCAg8PFgIeBFRleHQFCDE2MTk2MTA4ZGQCBw8WAh8DBQxkaXNwbGF5Om5vbmUWAmYPZBYCZg8QDxYGHwQFBHp5bWMfBQUEenlkbR8GZ2QQFQQh5py65qKw6K6%2B6K6h5Yi26YCg5Y%2BK5YW26Ieq5Yqo5YyWDOi9pui%2BhuW3peeoixXmtbfmtIvlt6XnqIvkuI7mioDmnK845py65qKw6K6%2B6K6h5Yi26YCg5Y%2BK5YW26Ieq5Yqo5YyWKOWNk%2Bi2iuW3peeoi%2BW4iOiuoeWIkikVBAQwMTAxBDAxMDUEMDE5MAQwMTk3FCsDBGdnZ2dkZAIJDxYCHwMFDWRpc3BsYXk6YmxvY2sWAgIFDzwrAAsAZAILDxYCHwMFDGRpc3BsYXk6bm9uZRYCZg9kFgICAQ8QDxYGHwQFAm5qHwUFAm5qHwZnZBAVEwQyMDE4BDIwMTcEMjAxNgQyMDE1BDIwMTQEMjAxMwQyMDEyBDIwMTEEMjAxMAQyMDA5BDIwMDgEMjAwNwQyMDA2BDIwMDUEMjAwNAQyMDAzBDIwMDIEMjAwMQQyMDAwFRMEMjAxOAQyMDE3BDIwMTYEMjAxNQQyMDE0BDIwMTMEMjAxMgQyMDExBDIwMTAEMjAwOQQyMDA4BDIwMDcEMjAwNgQyMDA1BDIwMDQEMjAwMwQyMDAyBDIwMDEEMjAwMBQrAxNnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnFgECAmQCDQ8WAh8DBQxkaXNwbGF5Om5vbmVkGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYFBQJ6eAUCengFAmZ4BQJmeAUCY3g%3D&__EVENTVALIDATION=%2FwEWPgLvwa9ZAg4CYmYCnuSP5QoCjovpiAYCjovRiAYCjovViAYCjovZiAYCjovdiAYCjovBiAYCjouFiwYCkYvpiAYCkYvtiAYCkYvRiAYCkYvViAYCkYvZiAYCkYuFiwYCkYuJiwYCkIvliAYCkIvtiAYCkIvRiAYCkIvBiAYClYvdiAYClYuJiwYClIvZiAYCl4vpiAYCl4vZiAYChovViAYChovZiAYCl5fWoA4Cl5eGsw0C0PSb%2FgEC0PSP%2BAIC7NGy6wYC%2BOOIvQEC%2BeOIvQEC%2BuOIvQEC94yi0w0C1pTPmwICneSP5QoC3vOEkwUC3vPQ%2BwcC3vP8nA8C3vOIsAQC3vOU1Q0C3vOg7goC3vPMgwIC3vPYpAsC3vPkeQK1ytbgBwK1yuKFDwK1ys7sCQK1ytqBAQK1yubaDgK1yvL%2FBwK1yp6TDwK1yqq0BAK1yrbJDQK1ysLiCgKM54rGBgK7q7GGCA%3D%3D&' \
	                  +'cx=cx&DropDownList2=01&' \
	                  +'TextBox1=' + lesson_name + '&RadioButtonList1=2&Button3=%C8%B7%B6%A8&'\
	                  # 这里没用到，可以为空 本来是2016
	                  +'DropDownList1='
	                 )
			break
		except:
			print('网络错误！重试中...')
			sleep(3)
	#网页为gb2312编码
	r.encoding = 'gbk'
	#处理&nbsp
	soup = BeautifulSoup(r.text.replace('&nbsp;', ' '),"lxml")
	# 提取信息
	result_list = soup.find_all(class_="datelist")[0].find_all('tr')[1:]
	lesson_search_result_list = []
	for result in result_list:
	    name = result.find_all('td')[0].get_text()
	    id = result.find_all('td')[1].get_text()
	    credit = result.find_all('td')[2].get_text()
	    url = result.find_all('td')[0].a['onclick']
	    url = 'http://jxgl.hdu.edu.cn/' + re.search("xsxjs.*xh=",url).group() + username
	    lesson_search_result_list.append(Lesson_search(name,id,credit,url))
	return lesson_search_result_list

def scan_any(cookies,username,url=''):
	# headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
 #               'Origin': 'http://jxgl.hdu.edu.cn',
 #               'Host': 'jxgl.hdu.edu.cn',
 #              }
 	# 为什么这里都不用headers
 	# 访问
 	while True:
 		try:
 			r = requests.get(url,cookies=cookies)
 			break
 		except:
 			print('网络错误！重试中...')
 			sleep(3)
 	#网页为gb2312编码
 	r.encoding = 'gbk'
 	#处理&nbsp
 	soup = BeautifulSoup(r.text.replace('&nbsp;', ' '),"lxml")
 	# 提取信息
 	name_credit = soup.find_all(id="Label1")[0].get_text()
 	lesson_name = name_credit.split()[0][5:]
 	lesson_credit = name_credit.split()[1][3:]
 	lesson_data_list = soup.find_all(id="xjs_table")[0].find_all("tr")[1:]
 	lesson = []
 	for lesson_data in lesson_data_list:
 		td = lesson_data.find_all("td")
 		name = lesson_name
 		credit = lesson_credit
 		teacher = td[1].get_text()
 		time = td[5].get_text()
 		total = td[11].get_text()
 		remain = str(int(total) - int(td[14].get_text()))
 		week = {'一':'1','二':'2','三':'3','四':'4','五':'5'}
 		weekday = week[time[1]]
 		lesson.append(Lesson(name,teacher,time,credit,total,remain,weekday))
 	return lesson

def send_email(msg_to,subject="选课余量更新提醒",content="这是我使用python smtplib及email模块发送的邮件"):
	msg_from='1005547224@qq.com'                                 #发送方邮箱
	passwd='znthkhrkoyiybaji'                                   #填入发送方邮箱的授权码
	# msg_to                                 #收件人邮箱                   
	msg = MIMEText(content)
	msg['Subject'] = subject
	msg['From'] = msg_from
	msg['To'] = msg_to
	try:
	    s = smtplib.SMTP_SSL("smtp.qq.com",465)
	    # s.starttls()
	    s.login(msg_from, passwd)
	    s.sendmail(msg_from, msg_to, msg.as_string())
	    print ("邮件发送成功")
	except smtplib.SMTPException:
	    print ("邮件发送失败")
	finally:
	    s.quit()