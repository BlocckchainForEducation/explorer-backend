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

from sawtooth_sdk.processor.exceptions import InvalidTransaction

from protobuf.b4e_protobuf import payload_pb2


class B4EPayload(object):

    def __init__(self, payload):
        self._transaction = payload_pb2.B4EPayload()
        self._transaction.ParseFromString(payload)

    @property
    def action(self):
        return self._transaction.action

    @property
    def data(self):
        if self._transaction.HasField('create_institution') and \
                self._transaction.action == \
                payload_pb2.B4EPayload.CREATE_INSTITUTION:
            return self._transaction.create_institution
        if self._transaction.HasField('create_teacher') and \
                self._transaction.action == \
                payload_pb2.B4EPayload.CREATE_TEACHER:
            return self._transaction.create_teacher
        if self._transaction.HasField('create_edu_officer') and \
                self._transaction.action == \
                payload_pb2.B4EPayload.CREATE_EDU_OFFICER:
            return self._transaction.create_edu_officer
        if self._transaction.HasField('create_vote') and \
                self._transaction.action == \
                payload_pb2.B4EPayload.CREATE_VOTE:
            return self._transaction.create_vote
        if self._transaction.HasField('create_class') and \
                self._transaction.action == \
                payload_pb2.B4EPayload.CREATE_CLASS:
            return self._transaction.create_class
        if self._transaction.HasField('create_record') and \
                self._transaction.action == \
                payload_pb2.B4EPayload.CREATE_RECORD:
            return self._transaction.create_record
        if self._transaction.HasField('update_record') and \
                self._transaction.action == \
                payload_pb2.B4EPayload.UPDATE_RECORD:
            return self._transaction.update_record
        if self._transaction.HasField('update_actor_info') and \
                self._transaction.action == \
                payload_pb2.B4EPayload.UPDATE_ACTOR_INFO:
            return self._transaction.update_actor_info
        if self._transaction.HasField('set_b4e_environment') and \
                self._transaction.action == \
                payload_pb2.B4EPayload.SET_B4E_ENVIRONMENT:
            return self._transaction.set_b4e_environment

        raise InvalidTransaction('Action does not match payload data')

    @property
    def timestamp(self):
        return self._transaction.timestamp
