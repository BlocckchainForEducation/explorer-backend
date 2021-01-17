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
        self.b4e_actor_collection = None
        self.b4e_record_collection = None
        self.b4e_voting_collection = None
        self.b4e_vote_collection = None
        self.b4e_environment_collection = None
        self.b4e_class_collection = None
        self.b4e_block_collection = None
        self.b4e_transaction_collection = None

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
        self.b4e_actor_collection = self.b4e_db[MongoDBConfig.ACTOR_COLLECTION]
        self.b4e_record_collection = self.b4e_db[MongoDBConfig.RECORD_COLLECTION]
        self.b4e_voting_collection = self.b4e_db[MongoDBConfig.VOTING_COLLECTION]
        self.b4e_vote_collection = self.b4e_db[MongoDBConfig.VOTE_COLLECTION]
        self.b4e_environment_collection = self.b4e_db[MongoDBConfig.ENVIRONMENT_COLLECTION]
        self.b4e_class_collection = self.b4e_db[MongoDBConfig.CLASS_COLLECTION]
        self.b4e_block_collection = self.b4e_db[MongoDBConfig.BLOCK_COLLECTION]
        self.b4e_transaction_collection = self.b4e_db[MongoDBConfig.TRANSACTION_COLLECTION]

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

    def num_institutions(self):
        key = {"role": "INSTITUTION"}
        actors = list(self.b4e_actor_collection.find(key))
        return len(actors)

    def num_active_institutions(self):
        key = {"role": "INSTITUTION", "status": "ACTIVE"}
        actors = list(self.b4e_actor_collection.find(key))
        return len(actors)

    def num_point_a_seasion(self):
        key = {"record_type": "CERTIFICATE"}
        records = list(self.b4e_record_collection.find(key))
        groups = defaultdict(list)
        for obj in records:
            groups[obj['manager_public_key']].append(obj)


def timestamp_to_datetime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)


def to_time_stamp(date_time):
    return datetime.datetime.timestamp(date_time)
