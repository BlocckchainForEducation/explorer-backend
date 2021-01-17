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

from addressing.b4e_addressing import addresser

from protobuf.b4e_protobuf import actor_pb2
from protobuf.b4e_protobuf import record_pb2
from protobuf.b4e_protobuf import b4e_environment_pb2
from protobuf.b4e_protobuf import class_pb2
from protobuf.b4e_protobuf import voting_pb2

import logging

LOGGER = logging.getLogger(__name__)


class B4EState(object):
    def __init__(self, context, timeout=10):
        self._context = context
        self._timeout = timeout

    def get_b4e_environment(self):
        try:
            address = addresser.ENVIRONMENT_ADDRESS
            state_entries = self._context.get_state(
                addresses=[address], timeout=self._timeout)
            if state_entries:
                container = b4e_environment_pb2.B4EEnvironmentContainer()
                container.ParseFromString(state_entries[0].data)
                for environment in container.entries:
                    return environment
            return None
        except Exception as e:
            print("Err :", e)
            return None

    def set_b4e_environment(self, transaction_id):
        """Creates a new agent in state

        Args:
        """
        environment = b4e_environment_pb2.B4EEnvironment(institution_number=0, transaction_id=transaction_id)
        environment_address = addresser.ENVIRONMENT_ADDRESS
        container = b4e_environment_pb2.B4EEnvironmentContainer()
        state_entries = self._context.get_state(
            addresses=[environment_address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)

        container.entries.extend([environment])
        data = container.SerializeToString()

        updated_state = {}
        updated_state[environment_address] = data
        response_address = self._context.set_state(updated_state, timeout=self._timeout)

    def add_one_b4e_environment(self, transaction_id):

        address = addresser.ENVIRONMENT_ADDRESS
        container = b4e_environment_pb2.B4EEnvironmentContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)
            for env in container.entries:
                env.institution_number += 1
                env.transaction_id = transaction_id

        data = container.SerializeToString()
        updated_state = {}
        updated_state[address] = data
        self._context.set_state(updated_state, timeout=self._timeout)

    def get_actor(self, public_key):

        try:
            address = addresser.get_actor_address(public_key)
            state_entries = self._context.get_state(
                addresses=[address], timeout=self._timeout)
            if state_entries:
                container = actor_pb2.ActorContainer()
                container.ParseFromString(state_entries[0].data)
                for actor in container.entries:
                    if actor.actor_public_key == public_key:
                        return actor

            return None
        except Exception as e:
            print("Err :", e)
            return None

    def set_actor(self, actor, public_key):
        """Creates a new agent in state

        Args:
        """

        actor_address = addresser.get_actor_address(public_key)
        container = actor_pb2.ActorContainer()
        state_entries = self._context.get_state(
            addresses=[actor_address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)

        container.entries.extend([actor])
        data = container.SerializeToString()

        updated_state = {}
        updated_state[actor_address] = data
        response_address = self._context.set_state(updated_state, timeout=self._timeout)

    def set_active_actor(self, public_key):

        address = addresser.get_actor_address(public_key)
        container = actor_pb2.ActorContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)
            for actor in container.entries:
                if actor.actor_public_key == public_key:
                    actor.status = actor_pb2.ACTIVE

        data = container.SerializeToString()
        updated_state = {}
        updated_state[address] = data
        self._context.set_state(updated_state, timeout=self._timeout)

    def set_reject_actor(self, public_key):

        address = addresser.get_actor_address(public_key)
        container = actor_pb2.ActorContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)
            for actor in container.entries:
                if actor.actor_public_key == public_key:
                    actor.status = actor_pb2.REJECT

        data = container.SerializeToString()
        updated_state = {}
        updated_state[address] = data
        self._context.set_state(updated_state, timeout=self._timeout)

    def get_voting(self, public_key):
        try:
            address = addresser.get_voting_address(public_key)
            state_entries = self._context.get_state(
                addresses=[address], timeout=self._timeout)
            if state_entries:
                container = voting_pb2.VotingContainer()
                container.ParseFromString(state_entries[0].data)
                for voting in container.entries:
                    if voting.elector_public_key == public_key:
                        return voting

            return None
        except Exception as e:
            print("Err :", e)
            return None

    def set_voting(self, voting, public_key):

        voting_address = addresser.get_voting_address(public_key)
        container = voting_pb2.VotingContainer()
        state_entries = self._context.get_state(
            addresses=[voting_address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)

        container.entries.extend([voting])
        data = container.SerializeToString()

        updated_state = {}
        updated_state[voting_address] = data
        response_address = self._context.set_state(updated_state, timeout=self._timeout)

    def update_voting(self, public_key, vote_result, vote, timestamp):

        address = addresser.get_voting_address(public_key)
        container = voting_pb2.VotingContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)
            for voting in container.entries:
                if voting.elector_public_key == public_key:
                    voting.vote.extend([vote])
                    voting.close_vote_timestamp = timestamp
                    voting.vote_result = vote_result

        data = container.SerializeToString()
        updated_state = {}
        updated_state[address] = data
        self._context.set_state(updated_state, timeout=self._timeout)

    def get_class(self, class_id, institution_public_key):

        try:
            address = addresser.get_class_address(class_id, institution_public_key)
            state_entries = self._context.get_state(
                addresses=[address], timeout=self._timeout)
            if state_entries:
                container = class_pb2.ClassContainer()
                container.ParseFromString(state_entries[0].data)
                for class_ in container.entries:
                    if class_.class_id == class_id:
                        return class_

            return None
        except Exception as e:
            print("Err :", e)
            return None

    def set_class(self, class_id, class_):

        class_address = addresser.get_class_address(class_id, class_.institution_public_key)
        container = class_pb2.ClassContainer()

        state_entries = self._context.get_state(
            addresses=[class_address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)

        container.entries.extend([class_])
        data = container.SerializeToString()

        updated_state = {}
        updated_state[class_address] = data
        response_address = self._context.set_state(updated_state, timeout=self._timeout)

    def get_record(self, record_id, owner_public_key, manager_public_key):
        try:
            address = addresser.get_record_address(record_id, owner_public_key, manager_public_key)
            state_entries = self._context.get_state(
                addresses=[address], timeout=self._timeout)
            if state_entries:
                container = record_pb2.RecordContainer()
                container.ParseFromString(state_entries[0].data)
                for record in container.entries:
                    if record.record_id == record_id:
                        return record

            return None
        except Exception as e:
            print("Err :", e)
            return None

    def set_record(self, record_id, record):

        address = addresser.get_record_address(record_id, record.owner_public_key, record.manager_public_key)

        container = record_pb2.RecordContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)

        container.entries.extend([record])
        data = container.SerializeToString()

        updated_state = {}
        updated_state[address] = data
        self._context.set_state(updated_state, timeout=self._timeout)

    def update_record(self, record_id, owner_public_key, manager_public_key, record_data, active, timestamp,
                      transaction_id):

        new_data = record_pb2.Record.RecordData(
            record_data=record_data,
            active=active,
            timestamp=timestamp,
            transaction_id=transaction_id
        )

        address = addresser.get_record_address(record_id, owner_public_key, manager_public_key)
        container = record_pb2.RecordContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)
            for record in container.entries:
                if record.record_id == record_id:
                    record.record_data.extend([new_data])

        data = container.SerializeToString()
        updated_state = {}
        updated_state[address] = data
        self._context.set_state(updated_state, timeout=self._timeout)

    def update_actor_info(self, actor_public_key, info):
        address = addresser.get_actor_address(actor_public_key)
        container = actor_pb2.ActorContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)
            for actor in container.entries:
                if actor.actor_public_key == actor_public_key:
                    actor.info.extend([info])

        data = container.SerializeToString()
        updated_state = {}
        updated_state[address] = data
        self._context.set_state(updated_state, timeout=self._timeout)
