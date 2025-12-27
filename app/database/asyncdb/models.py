from app.database.asyncdb.mongo_handler import MongoDbHandler
from app.database.asyncdb.collections import *

class Users(MongoDbHandler):
    def __init__(self):
        super().__init__(UsersCollection)


class Tasks(MongoDbHandler):
    def __init__(self):
        super().__init__(TasksCollection)
