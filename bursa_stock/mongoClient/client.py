from pymongo import MongoClient


class mongoClient:
    def __init__(self,url="mongodb+srv://wkm97:1504750@klse-s6tb2.mongodb.net/test?retryWrites=true&w=majority", database="klse"):
        self.url = url
        self.database_name = database
        self.client = None
        self.db = None
    
    def conn(self):
        self.client = MongoClient(self.url)
        self.db = self.client.get_database(self.database_name)
    def close(self):
        self.client.close()
    
    def changeDB(self, database_name):
        self.database_name = database_name
        self.db = self.client.get_database(self.database_name)