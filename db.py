#coding:utf8
from pymongo import MongoClient

client = MongoClient()

class ScoreDB:
	'''
	data model:{
		"name":string,
		"score":int(0,1,2),
		"updated":int(0,1)
	}
	'''
	def __init__(self, db_name):
		self.client = MongoClient()
		self.db = client[db_name]
		self.scores = self.db["scores"]
	
	def checkOut(name_list):
		for name in name_list:
			if self.scores.find_one({"name":name}) is None:
				self.scores.insert({"name":name, "score":2})

	def insert(self, info):
		# insert new person with initial score
		self.scores.insert_one(info)
	
	def addPoint(self, user_name, points):
		# 加分
		if self.scores.find_one({"name":user_name})["updated"] == 1:
			return
		self.scores.update_one({"name":user_name}, {"$inc":{"score":points}, "$set":{"updated":1}})

	def dailyUpdate(self):
		# 每天固定时间减一分
		self.scores.update_many({}, {"$inc": {"score":-1}, "$set": {"updated":0}})
	
	def kickOut(self):
		# 找出0分的人
		kickOutObjs = self.scores.find({"score":{"$lt":1}})
		kickOutNames = []
		for obj in kickOutObjs:
			kickOutNames.append(obj["name"])
			self.scores.delete_one(obj)
		return kickOutNames

	def show(self):
		allEntries = self.scores.find({})
		for i in allEntries:
			print i
if __name__ == "__main__":
	anne = {"name":"anne", "score":0}
	krog = {"name":"krog", "score":0}

	name_list = ["mike", "jerry","perl","silver","anne","krog"]
	scoreDB = ScoreDB("test_database")
	scoreDB.show()
	
	print "test kickOut and insert"
	print scoreDB.kickOut()
	scoreDB.show()
	print "recover"
	scoreDB.insert(anne)
	scoreDB.insert(krog)
	scoreDB.show()
	
	print "test dailyUpdate and addOnePoint"
	scoreDB.dailyUpdate()
	scoreDB.show()
	print "recover"
	for name in name_list:
		scoreDB.addPoint(name, 1)
	scoreDB.show()
