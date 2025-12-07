# ---------------------------------------------------
# File Name: DB.py
# Author: NeonAnurag
# GitHub: https://github.com/MyselfNeon/
# Telegram: https://t.me/MyelfNeon
# YouTube: https://youtube.com/@MyselfNeon
# Created: 2025-10-21
# Last Modified: 2025-10-22
# Version: Latest
# License: MIT License
# ---------------------------------------------------

import motor.motor_asyncio
from config import DB_NAME, DB_URI

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            session = None,
            verify_token = None,
            verify_date = None
        )
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
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
        """Stores the generated token for the user"""
        await self.col.update_one({'id': int(id)}, {'$set': {'verify_token': token}})

    async def get_verify_token(self, id):
        """Retrieves the stored token"""
        user = await self.col.find_one({'id': int(id)})
        return user.get('verify_token')

    async def update_verify_date(self, id, date):
        """Stores the time the user successfully verified and clears the used token"""
        await self.col.update_one({'id': int(id)}, {'$set': {'verify_date': date, 'verify_token': None}})

    async def get_verify_date(self, id):
        """Retrieves the verification timestamp"""
        user = await self.col.find_one({'id': int(id)})
        return user.get('verify_date')

db = Database(DB_URI, DB_NAME)
