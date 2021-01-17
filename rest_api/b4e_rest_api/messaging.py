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

from sawtooth_rest_api.messaging import Connection
from sawtooth_rest_api.protobuf import client_batch_submit_pb2
from sawtooth_rest_api.protobuf import validator_pb2

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import secp256k1

from rest_api.b4e_rest_api.errors import ApiBadRequest
from rest_api.b4e_rest_api.errors import ApiInternalError
from rest_api.b4e_rest_api import transaction_creation

import logging
import asyncio
import time
import datetime
import uuid
from config.config import Test, MongoDBConfig

import nest_asyncio

LOGGER = logging.getLogger(__name__)

from pymongo import MongoClient


class Messenger(object):
    def __init__(self, validator_url):
        self._connection = Connection(validator_url)
        self._context = create_context('secp256k1')
        self._crypto_factory = CryptoFactory(self._context)
        self._batch_signer = self._crypto_factory.new_signer(
            self._context.new_random_private_key())

    def open_validator_connection(self):
        self._connection.open()

    def close_validator_connection(self):
        self._connection.close()

    def open_db_collection(self):
        try:
            host = MongoDBConfig.HOST
            port = MongoDBConfig.PORT
            user_name = MongoDBConfig.USER_NAME
            password = MongoDBConfig.PASSWORD

            LOGGER.warning(
                "connect to monggo db host: " + host + "-port: " + port)
            if (user_name != "" and password != ""):
                url = f"mongodb://{user_name}:{password}@{host}:{port}"
                self.mongo = MongoClient(url)
            else:
                self.mongo = MongoClient(host=host, port=int(port))

            self.b4e_db = self.mongo[Test.DATABASE]
            self.test_collection = self.b4e_db[Test.TEST_COLLECTION]
        except Exception as e:
            LOGGER.warning(e)

    def close_db_collection(self):
        self.mongo.close()

    def get_new_key_pair(self):
        private_key = self._context.new_random_private_key()
        public_key = self._context.get_public_key(private_key)
        return public_key.as_hex(), private_key.as_hex()

    async def send_set_b4e_environment(self, timestamp):
        public_key, private_key = self.get_new_key_pair()
        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))
        batch = transaction_creation.make_set_b4e_environment(transaction_signer, timestamp)

        await self._send_and_wait_for_commit(batch)

    async def send_create_institution(self, private_key,
                                      profile,
                                      timestamp):

        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))
        batch_signer = transaction_signer

        batch = transaction_creation.make_create_institution(transaction_signer,
                                                             batch_signer,
                                                             profile,
                                                             timestamp)
        await self._send_and_wait_for_commit(batch)
        transaction_id = batch.transactions[0].header_signature
        return transaction_id

    async def send_create_teacher(self, private_key,
                                  profile,
                                  timestamp):

        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))
        batch_signer = transaction_signer

        batch = transaction_creation.make_create_teacher(transaction_signer,
                                                         batch_signer,
                                                         profile,
                                                         timestamp)
        await self._send_and_wait_for_commit(batch)
        transaction_id = batch.transactions[0].header_signature
        return transaction_id

    async def send_create_teachers(self, private_key,
                                   profiles,
                                   timestamp):

        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))
        batch_signer = transaction_signer

        list_batches = transaction_creation.make_create_teachers(transaction_signer,
                                                                 batch_signer,
                                                                 profiles,
                                                                 timestamp)

        list_transaction_id = self.submit_multi_batches(list_batches)
        return list_transaction_id

    async def send_create_edu_officer(self, private_key,
                                      profile,
                                      timestamp):

        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))
        batch_signer = transaction_signer

        batch = transaction_creation.make_create_edu_officer(transaction_signer,
                                                             batch_signer,
                                                             profile,
                                                             timestamp)
        await self._send_and_wait_for_commit(batch)
        transaction_id = batch.transactions[0].header_signature
        return transaction_id

    async def send_create_edu_officers(self, private_key,
                                       profiles,
                                       timestamp):

        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))
        batch_signer = transaction_signer

        list_batches = transaction_creation.make_create_edu_officers(transaction_signer,
                                                                     batch_signer,
                                                                     profiles,
                                                                     timestamp)
        list_transaction_id = self.submit_multi_batches(list_batches)
        return list_transaction_id

    async def send_create_vote(self, private_key,
                               elector_public_key,
                               accepted,
                               timestamp):

        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))
        issuer_public_key = transaction_signer.get_public_key().as_hex()
        batch_signer = transaction_signer

        batch = transaction_creation.make_create_vote(transaction_signer,
                                                      batch_signer,
                                                      issuer_public_key,
                                                      elector_public_key,
                                                      accepted,
                                                      timestamp)
        await self._send_and_wait_for_commit(batch)
        transaction_id = batch.transactions[0].header_signature
        return transaction_id

    async def send_create_class(self, private_key,
                                teacher_public_key,
                                edu_officer_public_key,
                                class_id,
                                timestamp):

        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))
        batch_signer = transaction_signer

        batch = transaction_creation.make_create_class(transaction_signer,
                                                       batch_signer,
                                                       teacher_public_key,
                                                       edu_officer_public_key,
                                                       class_id,
                                                       timestamp)
        await self._send_and_wait_for_commit(batch)
        transaction_id = batch.transactions[0].header_signature
        return transaction_id

    async def send_create_classes(self, private_key,
                                  classes,
                                  timestamp):

        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))
        batch_signer = transaction_signer

        list_batches = transaction_creation.make_create_classes(transaction_signer,
                                                                batch_signer,
                                                                classes,
                                                                timestamp)
        list_transaction_id = self.submit_multi_batches(list_batches)
        return list_transaction_id

    async def send_create_record(self, private_key,
                                 owner_public_key,
                                 manager_public_key,
                                 record_id,
                                 record_type,
                                 record_data,
                                 timestamp):

        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))
        batch_signer = transaction_signer

        batch = transaction_creation.make_create_record(transaction_signer,
                                                        batch_signer,
                                                        owner_public_key,
                                                        manager_public_key,
                                                        record_id,
                                                        record_type,
                                                        record_data,
                                                        timestamp)
        await self._send_and_wait_for_commit(batch)
        transaction_id = batch.transactions[0].header_signature
        return transaction_id

    async def send_create_subjects(self, private_key,
                                   institution_public_key,
                                   class_id,
                                   list_subjects,
                                   timestamp):

        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))
        batch_signer = transaction_signer

        list_batches = transaction_creation.make_create_subjects(transaction_signer,
                                                                 batch_signer,
                                                                 institution_public_key,
                                                                 class_id,
                                                                 list_subjects,
                                                                 timestamp)
        list_transaction_id = self.submit_multi_batches(list_batches)
        return list_transaction_id

    async def send_create_certs(self, private_key,
                                certs,
                                timestamp):

        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))
        batch_signer = transaction_signer

        list_batches = transaction_creation.make_create_certs(transaction_signer,
                                                              batch_signer,
                                                              certs,
                                                              timestamp)

        list_transaction_id = self.submit_multi_batches(list_batches)
        return list_transaction_id

    async def send_create_subject(self, private_key,
                                  owner_public_key,
                                  manager_public_key,
                                  record_id,
                                  record_type,
                                  record_data,
                                  timestamp):

        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))
        batch_signer = transaction_signer

        batch = transaction_creation.make_create_record(transaction_signer,
                                                        batch_signer,
                                                        owner_public_key,
                                                        manager_public_key,
                                                        record_id,
                                                        record_type,
                                                        record_data,
                                                        timestamp)
        await self._send_and_wait_for_commit(batch)
        transaction_id = batch.transactions[0].header_signature
        return transaction_id

    async def send_create_cert(self, private_key,
                               owner_public_key,
                               record_id,
                               record_type,
                               record_data,
                               timestamp):

        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))
        batch_signer = transaction_signer
        manager_public_key = transaction_signer.get_public_key().as_hex()

        batch = transaction_creation.make_create_record(transaction_signer,
                                                        batch_signer,
                                                        owner_public_key,
                                                        manager_public_key,
                                                        record_id,
                                                        record_type,
                                                        record_data,
                                                        timestamp)
        await self._send_and_wait_for_commit(batch)
        transaction_id = batch.transactions[0].header_signature
        return transaction_id

    async def send_update_record(self, private_key,
                                 owner_public_key,
                                 manager_public_key,
                                 record_id,
                                 record_data,
                                 active,
                                 timestamp):

        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))
        batch_signer = transaction_signer

        batch = transaction_creation.make_update_record(transaction_signer,
                                                        batch_signer,
                                                        owner_public_key,
                                                        manager_public_key,
                                                        record_id,
                                                        record_data,
                                                        active,
                                                        timestamp)
        await self._send_and_wait_for_commit(batch)
        transaction_id = batch.transactions[0].header_signature
        return transaction_id

    async def send_update_actor_info(self, private_key,
                                     name,
                                     phone,
                                     email,
                                     address,
                                     timestamp):

        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))
        batch_signer = transaction_signer

        batch = transaction_creation.make_update_actor_info(transaction_signer,
                                                            batch_signer,
                                                            name,
                                                            phone,
                                                            email,
                                                            address,
                                                            timestamp)
        await self._send_and_wait_for_commit(batch)
        transaction_id = batch.transactions[0].header_signature
        return transaction_id

    async def send_test_time_create_transaction(self, num_transactions):
        ministry_private_key = Test.MINISTRY_PRIVATE_KEY

        # create institution
        institution_public_key, institution_private_key = self.get_new_key_pair()
        institution_profile = {'uid': str(uuid.uuid1())}
        await self.send_create_institution(private_key=institution_private_key, profile=institution_profile,
                                           timestamp=self.get_time())

        # accpept institution

        await self.send_create_vote(private_key=ministry_private_key, elector_public_key=institution_public_key,
                                    accepted=True, timestamp=self.get_time())

        # make signer
        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(institution_private_key))
        batch_signer = transaction_signer
        certs = []

        # create certs
        for i in range(num_transactions):
            globalregisno = str(uuid.uuid1())
            student_public_key, student_private_key = self.get_new_key_pair()
            certs.append({
                "globalregisno": globalregisno,
                "studentPublicKey": student_public_key,
                "cipher": Test.CIPHER
            })

        list_batches = transaction_creation.make_create_certs(transaction_signer=transaction_signer,
                                                              batch_signer=batch_signer,
                                                              certs=certs,
                                                              timestamp=self.get_time())
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        futures = []
        timestamp = self.get_time()
        commit_time = 0
        for batch in list_batches:
            futures.append(self._send_and_wait_for_commit(batch))
        try:
            start = time.time()
            loop.run_until_complete(asyncio.wait(futures))
            end = time.time()
            commit_time = end - start
        except Exception as e:
            LOGGER.warning(e)

        test_result = {
            "timestamp": timestamp,
            "num_transactions": num_transactions,
            "commit_time": commit_time
        }
        try:
            self.test_collection.insert_one(test_result)
        except Exception as e:
            LOGGER.warning("db err")
            LOGGER.warning(e)
        return commit_time

    def get_time(self):
        dts = datetime.datetime.utcnow()
        return round(time.mktime(dts.timetuple()) + dts.microsecond / 1e6)

    def submit_multi_batches(self, list_batches):
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        futures = []
        list_transaction_id = []
        for batch in list_batches:
            futures.append(self._send_and_wait_for_commit(batch))
            for transaction in batch.transactions:
                list_transaction_id.append(transaction.header_signature)
        try:
            loop.run_until_complete(asyncio.wait(futures))
            end = time.time()
        except Exception as e:
            LOGGER.warning(e)

        return list_transaction_id

    async def _send_and_wait_for_commit(self, batch):

        # Send transaction to validator
        submit_request = client_batch_submit_pb2.ClientBatchSubmitRequest(
            batches=[batch])
        await self._connection.send(
            validator_pb2.Message.CLIENT_BATCH_SUBMIT_REQUEST,
            submit_request.SerializeToString())

        # Send status request to validator
        batch_id = batch.header_signature
        status_request = client_batch_submit_pb2.ClientBatchStatusRequest(
            batch_ids=[batch_id], wait=True)
        validator_response = await self._connection.send(
            validator_pb2.Message.CLIENT_BATCH_STATUS_REQUEST,
            status_request.SerializeToString())

        # Parse response
        status_response = client_batch_submit_pb2.ClientBatchStatusResponse()
        status_response.ParseFromString(validator_response.content)
        status = status_response.batch_statuses[0].status
        if status == client_batch_submit_pb2.ClientBatchStatus.INVALID:
            error = status_response.batch_statuses[0].invalid_transactions[0]
            raise ApiBadRequest(error.message)
        elif status == client_batch_submit_pb2.ClientBatchStatus.PENDING:
            raise ApiInternalError('Transaction submitted but timed out')
        elif status == client_batch_submit_pb2.ClientBatchStatus.UNKNOWN:
            raise ApiInternalError('Something went wrong. Try again later')
