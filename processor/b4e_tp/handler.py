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


from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction

from addressing.b4e_addressing import addresser

from protobuf.b4e_protobuf import payload_pb2

from processor.b4e_tp.payload import B4EPayload
from processor.b4e_tp.state import B4EState

from processor.b4e_tp import handler_action
from processor.b4e_tp import validator

import logging

SYNC_TOLERANCE = 60 * 5
LOGGER = logging.getLogger(__name__)


class B4EHandler(TransactionHandler):

    @property
    def family_name(self):
        return addresser.FAMILY_NAME

    @property
    def family_versions(self):
        return [addresser.FAMILY_VERSION]

    @property
    def namespaces(self):
        return [addresser.NAMESPACE]

    def apply(self, transaction, context):
        header = transaction.header
        payload = B4EPayload(transaction.payload)
        state = B4EState(context)

        validator.validate_timestamp(payload.timestamp)

        if payload.action == payload_pb2.B4EPayload.CREATE_INSTITUTION:
            handler_action.create_institution(
                state=state,
                public_key=header.signer_public_key,
                transaction_id=transaction.signature,
                payload=payload)
        elif payload.action == payload_pb2.B4EPayload.CREATE_TEACHER:
            handler_action.create_teacher(
                state=state,
                public_key=header.signer_public_key,
                transaction_id=transaction.signature,
                payload=payload)
        elif payload.action == payload_pb2.B4EPayload.CREATE_EDU_OFFICER:
            handler_action.create_edu_officer(
                state=state,
                public_key=header.signer_public_key,
                transaction_id=transaction.signature,
                payload=payload)
        elif payload.action == payload_pb2.B4EPayload.CREATE_VOTE:
            handler_action.vote(
                state=state,
                public_key=header.signer_public_key,
                transaction_id=transaction.signature,
                payload=payload)
        elif payload.action == payload_pb2.B4EPayload.CREATE_RECORD:
            handler_action.create_record(
                state=state,
                public_key=header.signer_public_key,
                transaction_id=transaction.signature,
                payload=payload)
        elif payload.action == payload_pb2.B4EPayload.UPDATE_RECORD:
            handler_action.update_record(
                state=state,
                public_key=header.signer_public_key,
                transaction_id=transaction.signature,
                payload=payload)
        elif payload.action == payload_pb2.B4EPayload.CREATE_CLASS:
            handler_action.create_class(
                state=state,
                public_key=header.signer_public_key,
                transaction_id=transaction.signature,
                payload=payload)
        elif payload.action == payload_pb2.B4EPayload.UPDATE_ACTOR_INFO:
            handler_action.update_actor_info(
                state=state,
                public_key=header.signer_public_key,
                transaction_id=transaction.signature,
                payload=payload)
        elif payload.action == payload_pb2.B4EPayload.SET_B4E_ENVIRONMENT:
            handler_action.set_b4e_environment(
                state=state,
                public_key=header.signer_public_key,
                transaction_id=transaction.signature,
                payload=payload)
        else:
            raise InvalidTransaction('Unhandled action')
