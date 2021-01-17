# Copyright 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

import asyncio
import logging
from pymongo import MongoClient
from collections import defaultdict

import datetime

from config.config import MongoDBConfig

LATEST_BLOCK_NUM = """
SELECT max(block_num) FROM blocks
"""
LOGGER = logging.getLogger(__name__)


class Database(object):
    """Manages connection to the postgres database and makes async queries
    """

    def __init__(self):
        self.mongo = None
        self.b4e_db = None
        self.b4e_block_collection = None
        self.b4e_transaction_collection = None
        self.b4e_transaction_family_collection = None

    def connect(self, host=MongoDBConfig.HOST, port=MongoDBConfig.PORT, user_name=MongoDBConfig.USER_NAME,
                password=MongoDBConfig.PASSWORD):
        if (user_name != "" and password != ""):
            url = f"mongodb://{user_name}:{password}@{host}:{port}"
            self.mongo = MongoClient(url)
        else:
            self.mongo = MongoClient(host=host, port=int(port))
        self.create_collections()

    def create_collections(self):
        self.b4e_db = self.mongo[MongoDBConfig.DATABASE]
        self.b4e_block_collection = self.b4e_db[MongoDBConfig.BLOCK_COLLECTION]
        self.b4e_transaction_collection = self.b4e_db[MongoDBConfig.TRANSACTION_COLLECTION]
        self.b4e_transaction_family_collection = self.b4e_db[MongoDBConfig.TRANSACTION_FAMILY_COLLECTION]

    def disconnect(self):
        self.mongo.close()

    def commit(self):
        pass

    def rollback(self):
        pass

    async def create_auth_entry(self,
                                public_key,
                                encrypted_private_key,
                                hashed_password):
        pass

    async def fetch_agent_resource(self, public_key):
        pass

    async def fetch_all_agent_resources(self):
        pass

    async def fetch_auth_resource(self, public_key):
        pass

    async def fetch_record_resource(self, record_id):
        pass

    async def fetch_all_record_resources(self):
        pass

    def get_transaction(self, transaction_id):
        key = {'transaction_id': transaction_id}
        transaction = self.b4e_transaction_collection.find_one(key)
        LOGGER.info("transaction", transaction)
        return transaction

    def get_transaction_num(self):
        res = self.b4e_transaction_collection.find().count()
        return res

    def get_block_num(self):
        return self.b4e_block_collection.find().count()

    def get_family_num(self):
        return self.b4e_transaction_family_collection.find().count()

    def get_transaction_family_num(self, family_name):
        key = {'family_name': family_name}
        res = self.b4e_transaction_family_collection.find_one(key)
        if not res:
            return 0
        return res['total_transaction']


def timestamp_to_datetime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)


def to_time_stamp(date_time):
    return datetime.datetime.timestamp(date_time)
