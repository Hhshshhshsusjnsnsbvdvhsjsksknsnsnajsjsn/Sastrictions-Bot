# ---------------------------------------------------
# File Name: DB.py
# Author: NeonAnurag
# ---------------------------------------------------

import motor.motor_asyncio
from config import DB_NAME, DB_URI

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

    # UPDATED: Added username argument
    def new_user(self, id, name, username):
        return dict(
            id = id,
            name = name,
            username = username,
            session = None,
            verify_token = None,
            verify_date = None
        )
    
    # UPDATED: Added username argument
    async def add_user(self, id, name, username):
        user = self.new_user(id, name, username)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def set_session(self, id, session):
        await self.col.update_one({'id': int(id)}, {'$set': {'session': session}})

    async def get_session(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('session')

    # ---------------------------------------
    # NEW VERIFICATION METHODS
    # ---------------------------------------

    async def update_verify_token(self, id, token):
        await self.col.update_one({'id': int(id)}, {'$set': {'verify_token': token}})

    async def get_verify_token(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('verify_token')

    async def update_verify_date(self, id, date):
        await self.col.update_one({'id': int(id)}, {'$set': {'verify_date': date, 'verify_token': None}})

    async def get_verify_date(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('verify_date')

    # ---------------------------------------
    # NEW USERNAME UPDATE METHOD (FIXED)
    # ---------------------------------------

    async def update_username(self, id, username):
        """Updates the username for an existing user"""
        await self.col.update_one({'id': int(id)}, {'$set': {'username': username}})

db = Database(DB_URI, DB_NAME)
