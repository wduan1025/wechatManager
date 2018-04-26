import itchat
# reply message
@itchat.msg_register()
def text_reply(msg):
	print msg
	return "hi this is robot"

itchat.auto_login()
itchat.run()
