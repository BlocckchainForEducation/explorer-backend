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
# -----------------------------------------------------------------------------

import logging
from pymongo import MongoClient

from config.config import MongoDBConfig

import subscriber_b4e.b4e_subscriber.blockchain_get_data as blockchain_services

LOGGER = logging.getLogger(__name__)


class Database(object):
    """Simple object for managing a connection to a postgres database
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

    def drop_fork(self, block_num):
        """Deletes all resources from a particular block_num
                """
        delete = {"block_num": {"$gte": block_num}}

        try:
            self.b4e_record_collection.delete_many(delete)
            self.b4e_block_collection.delete_many(delete)
            self.b4e_transaction_collection.delete_many(delete)

        except Exception as e:
            print(e)

    def fetch_last_known_blocks(self, count):
        try:
            blocks = list(self.b4e_block_collection.find().sort("block_num", -1))
            return blocks[:count]
            # if not found res will not contain ['hits']['hits'][0]['_source']
        except IndexError:
            print("not found block")
            return None

    def fetch_block(self, block_num):
        if not block_num:
            return None

        query = {"block_num": block_num}
        try:
            block = self.b4e_block_collection.find_one(query)
            return block
        except Exception as e:
            print(e)
            return None

    def insert_block(self, block_dict):
        try:
            block_num = block_dict.get('block_num')
            key = {'block_num': block_num}
            data = {"$set": block_dict}
            self.insert_transaction(block_dict=block_dict)
            if (not block_num):
                return
            res = self.b4e_block_collection.update_one(key, data, upsert=True)

            return res
        except Exception as e:
            print(e)
            return None

    def insert_transaction(self, block_dict):
        try:
            block_num = block_dict.get('block_num')
            block_id = block_dict.get('block_id')

            transactions = blockchain_services.get_transaction_from_block(block_id=block_id)
            if not transactions:
                return None
            for transaction in transactions:
                transaction_id = transaction['transaction_id']
                transaction['block_num'] = block_num
                key = {'transaction_id': transaction_id}
                data = {"$set": transaction}
                self.insert_transaction_family(transaction)

                res = self.b4e_transaction_collection.update_one(key, data, upsert=True)

            return True
        except Exception as e:
            return None

    def insert_transaction_family(self, transaction):

        try:
            family_name = transaction['header']['family_name']
            key = {'family_name': family_name}

            family = self.b4e_transaction_family_collection.find_one(key)
            try:
                total_transaction = family['total_transaction']
                if total_transaction:
                    total_transaction += 1
                else:
                    total_transaction = 1
            except Exception as e:
                total_transaction = 1

            family = {
                'family_name': family_name,
                'total_transaction': total_transaction,
            }

            data = {"$set": family}
            res = self.b4e_transaction_family_collection.update_one(key, data, upsert=True)

            return True
        except Exception as e:
            return None
