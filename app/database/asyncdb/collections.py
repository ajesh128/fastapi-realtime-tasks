from app.database.asyncdb.core import db
from app.database.constant import DbNameConstants

UsersCollection = db[DbNameConstants.UsersCollectionDb]
TasksCollection = db[DbNameConstants.TasksCollectionDb]
