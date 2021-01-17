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

import enum
import hashlib

FAMILY_NAME = 'b4e'
FAMILY_VERSION = '3.0'
NAMESPACE = hashlib.sha512(FAMILY_NAME.encode('utf-8')).hexdigest()[:6]
ACTOR_PREFIX = '00'
VOTING_PREFIX = '01'
CLASS_PREFIX = '10'
RECORD_PREFIX = '11'

ENVIRONMENT_ADDRESS = NAMESPACE + str(10 ** 64)[1:]


@enum.unique
class AddressSpace(enum.IntEnum):
    ACTOR = 0
    VOTING = 1
    CLASS = 2
    RECORD = 4
    ENVIRONMENT = 5
    OTHER_FAMILY = 100


def get_environment_address():
    return ENVIRONMENT_ADDRESS


def get_actor_address(public_key):
    return NAMESPACE + ACTOR_PREFIX + hashlib.sha512(
        public_key.encode('utf-8')).hexdigest()[:62]


def get_voting_address(public_key):
    return NAMESPACE + VOTING_PREFIX + hashlib.sha512(
        public_key.encode('utf-8')).hexdigest()[:62]


def get_class_address(class_id, institution_public_key):
    institution_prefix = institution_public_key[-10:]
    return NAMESPACE + CLASS_PREFIX + institution_prefix + hashlib.sha512(
        class_id.encode('utf-8')).hexdigest()[:52]


def get_record_address(record_id, owner_public_key, manager_public_key):
    owner_prefix = owner_public_key[-10:]
    manager_prefix = manager_public_key[-5:]
    return NAMESPACE + RECORD_PREFIX + owner_prefix + manager_prefix \
           + hashlib.sha512(record_id.encode('utf-8')).hexdigest()[:47]


def get_address_type(address):
    if address[:len(NAMESPACE)] != NAMESPACE:
        return AddressSpace.OTHER_FAMILY
    if address == ENVIRONMENT_ADDRESS:
        return AddressSpace.ENVIRONMENT
    infix = address[6:8]

    if infix == '00':
        return AddressSpace.ACTOR
    if infix == '01':
        return AddressSpace.VOTING
    if infix == '10':
        return AddressSpace.CLASS
    if infix == '11':
        return AddressSpace.RECORD

    return AddressSpace.OTHER_FAMILY


def is_owner(record_address, owner_public_key):
    infix = record_address[6:8]
    if infix != '11':
        return False
    if record_address[8:18] == owner_public_key[-10:]:
        return True
    return False


def is_manager(record_address, manager_public_key):
    infix = record_address[6:8]
    if infix != '11':
        return False
    if record_address[18:23] == manager_public_key[-5:]:
        return True
    return False
