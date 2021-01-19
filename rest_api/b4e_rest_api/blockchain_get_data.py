import base64
import json
import logging

import requests

from protobuf.b4e_protobuf import payload_pb2

from config.config import Sawtooth_Config
from addressing.b4e_addressing import addresser
from addressing.b4e_addressing.addresser import AddressSpace
from protobuf.b4e_protobuf.actor_pb2 import ActorContainer
from protobuf.b4e_protobuf.b4e_environment_pb2 import B4EEnvironmentContainer
from protobuf.b4e_protobuf.voting_pb2 import VotingContainer
from protobuf.b4e_protobuf.class_pb2 import ClassContainer
from protobuf.b4e_protobuf.record_pb2 import RecordContainer
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import MessageToDict

CONTAINERS = {
    AddressSpace.ACTOR: ActorContainer,
    AddressSpace.RECORD: RecordContainer,
    AddressSpace.CLASS: ClassContainer,
    AddressSpace.VOTING: VotingContainer,
    AddressSpace.ENVIRONMENT: B4EEnvironmentContainer
}

LOGGER = logging.getLogger(__name__)


def enum_value_to_name(val):
    desc = payload_pb2.B4EPayload.Action.DESCRIPTOR
    for (k, v) in desc.values_by_name.items():
        if v.number == val:
            return k
    return None


def get_transactions_from_rest(limit):
    if (limit):
        limit_url = "?limit=" + str(limit)
    else:
        limit_url = ""
    url = Sawtooth_Config.REST_API + "/transactions" + limit_url
    response = requests.get(url)
    if response.status_code == 200:
        try:
            transaction_dict = json.loads(response.content)
            return transaction_dict

        except Exception as e:
            print("err:", e)
            LOGGER.warning(e)
            return None


def get_blocks_from_rest(limit):
    if (limit):
        limit_url = "?limit=" + str(limit)
    else:
        limit_url = ""
    url = Sawtooth_Config.REST_API + "/blocks" + limit_url
    response = requests.get(url)
    if response.status_code == 200:
        try:
            blocks = json.loads(response.content)
            return blocks

        except Exception as e:
            print("err:", e)
            LOGGER.warning(e)
            return None


def get_block_from_rest(block_id):
    url = Sawtooth_Config.REST_API + "/blocks/" + str(block_id)
    response = requests.get(url)
    if response.status_code == 200:
        try:
            blocks = json.loads(response.content)
            return blocks

        except Exception as e:
            print("err:", e)
            LOGGER.warning(e)
            return None


def get_peers():
    url = Sawtooth_Config.REST_API + "/peers"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            peers = json.loads(response.content)
            return peers

        except Exception as e:
            print("err:", e)
            LOGGER.warning(e)
            return None


def get_data_from_transaction(transaction_id):
    url = Sawtooth_Config.REST_API + "/transactions/" + str(transaction_id)
    response = requests.get(url)
    if response.status_code == 200:
        try:
            transaction_dict = json.loads(response.content)
            payload_string = transaction_dict['data']['payload']
            data_model = payload_pb2.B4EPayload()
            data_model.ParseFromString(base64.b64decode(payload_string))
            return MessageToDict(data_model)

        except Exception as e:
            print("err:", e)
            LOGGER.warning(e)
            return None


def get_record_transaction(transaction_id):
    url = Sawtooth_Config.REST_API + "/transactions/" + str(transaction_id)

    response = requests.get(url)
    if response.status_code == 200:
        try:
            transaction_dict = json.loads(response.content)
            payload_string = transaction_dict['data']['payload']
            data_model = payload_pb2.B4EPayload()
            data_model.ParseFromString(base64.b64decode(payload_string))
            data = dict(MessageToDict(data_model))

            if data.get('createRecord'):
                res = {
                    'ok': True,
                    'cipher': data['createRecord']['recordData'],
                    'timestamp': data['timestamp']
                }
            elif data.get('updateRecord'):
                res = {
                    'ok': True,
                    'cipher': data['updateRecord']['recordData'],
                    'timestamp': data['timestamp']
                }
            else:
                res = {
                    'ok': False,
                    'msg': 'Transaction record not found'
                }
            return res

        except Exception as e:
            print("err:", e)
            LOGGER.warning(e)
            return {'ok': False}
    return {'ok': False, 'msg': 'Transaction  not found'}


def get_payload_from_block(block_id, address):
    url = Sawtooth_Config.REST_API + "/blocks/" + str(block_id)
    response = requests.get(url)
    if response.status_code == 200:
        try:
            block = json.loads(response.content)
            batches = block['data']['batches']
            for batch in batches:

                for transaction in batch['transactions']:
                    tran = json.loads(json.dumps(transaction))
                    print(tran['header']['outputs'])
                    if address in transaction['header']['outputs']:
                        return transaction['payload']

            return None

        except Exception as e:
            print("err:", e)
            return {'msg': "err"}


def get_data_payload(payload_string):
    try:
        data_model = payload_pb2.B4EPayload()
        data_model.ParseFromString(base64.b64decode(payload_string))

        return data_model

    except Exception as e:
        print("err:", e)
        return payload_string


def get_state(sawtooth_address):
    url = Sawtooth_Config.REST_API + "/state/" + str(sawtooth_address)
    response = requests.get(url)
    if response.status_code == 200:
        try:
            state_dict = json.loads(response.content)
            payload_string = state_dict['data']
            data = deserialize_data(sawtooth_address, base64.b64decode(payload_string))[0]

            return data

        except Exception as e:
            print("err:", e)
            return {'msg': "err"}


def deserialize_data(address, data):
    """Deserializes state data by type based on the address structure and
    returns it as a dictionary with the associated data type

    Args:
        address (str): The state address of the container
        data (str): String containing the serialized state data
    """
    data_type = addresser.get_address_type(address)

    if data_type == addresser.AddressSpace.OTHER_FAMILY:
        return []
    try:
        container = CONTAINERS[data_type]
    except KeyError:
        raise TypeError('Unknown data type: {}'.format(data_type))

    entries = _parse_proto(container, data).entries
    return [_convert_proto_to_dict(pb) for pb in entries]


def _parse_proto(proto_class, data):
    deserialized = proto_class()
    deserialized.ParseFromString(data)
    return deserialized


def _convert_proto_to_dict(proto):
    result = {}

    for field in proto.DESCRIPTOR.fields:
        key = field.name
        value = getattr(proto, key)

        if field.type == field.TYPE_MESSAGE:
            if field.label == field.LABEL_REPEATED:
                result[key] = [_convert_proto_to_dict(p) for p in value]
            else:
                result[key] = _convert_proto_to_dict(value)

        elif field.type == field.TYPE_ENUM:
            number = int(value)
            name = field.enum_type.values_by_number.get(number).name
            result[key] = name

        else:
            result[key] = value

    return result
