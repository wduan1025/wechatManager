#coding:utf8
import itchat
import re
from itchat.content import *
from ocr import *
from db import *
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime


itchat.auto_login()
print "Initializing..."
'''
CONFIGURATION
'''
TEST = True

TARGET_LIST = ["Maskerism", "Liuyang", "Jokee"] # just for spam use
INIT_SCORE = 1 # initial score for user
if TEST:
	DB_NAME = "test_database"
	CHATROOM_NAME = 'ceshi'
	CHATROOM_NAME_CH = u"测试"
	CHATROOM_OWNER_NAME = "sirius"
	PROBLEM_TITLE = "non-overlapping intervals"
else:
	DB_NAME = "wechatDB"
	CHATROOM_NAME = 'shuati'
	CHATROOM_NAME_CH = u"刷题"
	CHATROOM_OWNER_NAME = "sirius"
	PROBLEM_TITLE = ""

'''
SET UP
'''
#timer
sched = BackgroundScheduler()

#sched.add_job(dailyUpdate, "cron", day_of_week = "mon-fri", hour = "0-23", minute = "0-59", second = "3")

#wechat
FRIENDS = itchat.get_friends(update=True)[1:]
FRIEND_NAME_TO_KEY = {friend.PYQuanPin: friend.UserName for friend in FRIENDS}
FRIEND_KEY_TO_NAME = {c:i for i,c in FRIEND_NAME_TO_KEY.items()}


CHATROOMS = itchat.get_chatrooms()
chatroom = itchat.search_chatrooms(CHATROOM_NAME_CH)[0]
CHATROOM_KEY = chatroom.UserName
chatroom = itchat.update_chatroom(CHATROOM_KEY, detailedMember = True)
MEMBERS = chatroom['MemberList']

MEMBER_KEY_TO_NAME = {m['UserName']: m['PYQuanPin'] for m in MEMBERS}
MEMBER_SCORE = {m['PYQuanPin']: INIT_SCORE for m in MEMBERS}

#database
scoreDB = ScoreDB(DB_NAME)
scoreDB.checkOut(MEMBER_KEY_TO_NAME.values())
scoreDB.show()

'''
running
'''
def send_friend(message, name):
	target = [friendName for friendName in FRIEND_NAME_TO_KEY.keys() if name in friendName]
	if len(target) > 1:
		print "ambiguous friend name "
		return
	elif len(target) == 0:
		print "name not found in friends"
		return
	itchat.send(message, FRIEND_NAME_TO_KEY[target[0]])
	print "message:",message, "sent to ", name

def send_chatroom(message, room_id):
	itchat.send(message, room_id)
	print "message:",message, "sent to ", room_id

@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
def text_reply(msg):
	try:
		senderName = FRIEND_KEY_TO_NAME[msg.FromUserName]
	except:
		return
	#info = "%s:%s"%(msg["Type"], msg["Text"])
	#itchat.send(info, msg.FromUserName)

@itchat.msg_register([TEXT], isGroupChat = True)
def get_group_anouncement(msg):
	'''
	获取群公告
	'''
	global PROBLEM_TITLE
	chatroomName = msg.User.PYQuanPin
	if chatroomName != CHATROOM_NAME:
		return
	senderKey = msg["FromUserName"]
	senderName = MEMBER_KEY_TO_NAME[senderKey]
	# 首先判断是否群主所发.目前没有办法自动获取群主信息
	if senderName != CHATROOM_OWNER_NAME:
		return
	#send_friend(msg['Text'], "bot")
	#解析problem title, 如果不包含，返回 "";如果有其它错误，返回None
	print PROBLEM_TITLE
	problemTitle = re.findall(r"([0-9a-zA-Z ]+)\n", msg['Text'].split("\n")[0]+"\n")
	if len(problemTitle) != 1:
		return
	PROBLEM_TITLE = problemTitle[0].strip()
	print "problem title is ",PROBLEM_TITLE
	
	
	
	


@itchat.msg_register([PICTURE], isGroupChat = True)
def downloa_files(msg):
	'''
	处理打卡图片
	'''
	chatroomName = msg.User.PYQuanPin
	if chatroomName != CHATROOM_NAME:
		return
	senderKey = msg["FromUserName"]
	senderName = MEMBER_KEY_TO_NAME[senderKey]
	if senderKey[:2] == "@@":
		print "strange user name"
	print "a picture from %s @ %s"%(senderName, CHATROOM_NAME)
	savePath = "cache/"+senderName+".jpg"
	msg["Text"](savePath)
	# check uploaded image contains today's problem
	s = get_problem_title(savePath)
	print "ocr result: ", s
	if PROBLEM_TITLE == "":
		PROBLEM_TITLE = s
	distance = get_edit_distance(s, PROBLEM_TITLE)
	if distance < 5:
		send_chatroom(u"打卡成功", CHATROOM_KEY)
		scoreDB.addPoint(senderName, 1)

#时间响应，定时对scoreDB 进行udpate
@sched.scheduled_job("cron", args = [scoreDB], day_of_week = "mon-sun", hour = "0-23", minute = "0-59", second = "3")
def dailyUpdate(db):
	db.dailyUpdate()
	db.show()
	deleteFromChatroom()

#从群里删人
def deleteFromChatroom():
	

#将新加入群的人添加到db
def onAddMember():
	pass

sched.start()
itchat.run()
#import _thread
#_thread.start_new_thread(itchat.run(), ())
#_thread.start_new_thread(sched.start(), ())
