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
import time
from elasticsearch import Elasticsearch
from config.config import ElasticSearchConfig

LOGGER = logging.getLogger(__name__)


class Database(object):
    """Simple object for managing a connection to a postgres database
    """

    def __init__(self):
        self.es = None

    def connect(self, host=ElasticSearchConfig.HOST, port=ElasticSearchConfig.PORT):
        self.es = Elasticsearch([{"host": host, "port": port}])
        # print("db connected")

    def create_indexes(self):

        if not self.es.indices.exists(index=ElasticSearchConfig.MINISTRY_INDEX):
            try:
                res = self.es.indices.create(index=ElasticSearchConfig.MINISTRY_INDEX)

                res = self.es.indices.create(index=ElasticSearchConfig.INSTITUTION_INDEX)

                res = self.es.indices.create(index=ElasticSearchConfig.TEACHER_INDEX)

                res = self.es.indices.create(index=ElasticSearchConfig.STUDENT_INDEX)

                res = self.es.indices.create(index=ElasticSearchConfig.RECORD_INDEX)

                mapping = {
                    "mappings": {
                        "properties": {
                            "block_num": {"type": "long"}
                        }
                    }
                }
                res = self.es.indices.create(index=ElasticSearchConfig.BLOCK_INDEX, body=mapping)
                return res
            except Exception as e:
                print("already exist", e)
        print("created index")

    def disconnect(self):
        self.es = None

    def commit(self):
        pass

    def rollback(self):
        pass

    def drop_fork(self, block_num):
        """Deletes all resources from a particular block_num
                """
        query = {
            "query": {
                "range": {
                    "block_num": {
                        "gte": block_num
                    }
                }
            }
        }
        try:
            self.es.delete_by_query(index=ElasticSearchConfig.RECORD_INDEX, body=query)
            self.es.delete_by_query(index=ElasticSearchConfig.MINISTRY_INDEX, body=query)
            self.es.delete_by_query(index=ElasticSearchConfig.INSTITUTION_INDEX, body=query)
            self.es.delete_by_query(index=ElasticSearchConfig.TEACHER_INDEX, body=query)
            self.es.delete_by_query(index=ElasticSearchConfig.STUDENT_INDEX, body=query)
            self.es.delete_by_query(index=ElasticSearchConfig.BLOCK_INDEX, body=query)
        except Exception as e:
            print(e)

    def fetch_last_known_blocks(self, count):
        body = {
            'size': count,
            'query': {
                'match_all': {}
            },
            "sort": [
                {"block_num": {"order": "desc"}}
            ]
        }

        try:
            res = self.es.search(index=ElasticSearchConfig.BLOCK_INDEX, body=body)

            blocks = []
            for i in res['hits']['hits']:
                blocks.append(i["_source"])
            return blocks
            # if not found res will not contain ['hits']['hits'][0]['_source']
        except IndexError:
            print("not found block")
            return None

    def fetch_block(self, block_num):
        if not block_num:
            return None
        body = {
            "query": {
                "match": {
                    "block_num": block_num
                }
            }
        }
        try:
            res = self.es.search(index=ElasticSearchConfig.BLOCK_INDEX, body=body)
            block = res['hits']['hits'][0]['_source']
            return block
        except Exception as e:
            # print(e)
            return None

    def insert_block(self, block_dict):
        try:
            # print(block_dict)
            res = self.es.index(index=ElasticSearchConfig.BLOCK_INDEX, id=block_dict['block_num'], body=block_dict)
            return res
        except Exception as e:
            print(e)
            return None

    def insert_ministry(self, ministry_dict):
        try:
            res = self.es.index(index=ElasticSearchConfig.MINISTRY_INDEX, id=ministry_dict['ministry_public_key'],
                                body=ministry_dict)
            return res
        except Exception as e:
            print(e)
            return None

    def insert_institution(self, institution_dict):
        try:
            res = self.es.index(index=ElasticSearchConfig.INSTITUTION_INDEX,
                                id=institution_dict['institution_public_key'],
                                body=institution_dict)
            return res
        except Exception as e:
            print(e)
            return None

    def insert_teacher(self, teacher_dict):
        try:
            res = self.es.index(index=ElasticSearchConfig.TEACHER_INDEX, id=teacher_dict['teacher_public_key'],
                                body=teacher_dict)
            return res
        except Exception as e:
            print(e)
            return None

    def insert_student(self, student_dict):
        try:
            res = self.es.index(index=ElasticSearchConfig.STUDENT_INDEX, id=student_dict['student_public_key'],
                                body=student_dict)
            return res
        except Exception as e:
            print(e)
            return None

    def insert_record(self, record_dict):
        try:
            res = self.es.index(index=ElasticSearchConfig.RECORD_INDEX, id=record_dict['record_id'],
                                body=record_dict)
            return res
        except Exception as e:
            print(e)
            return None
