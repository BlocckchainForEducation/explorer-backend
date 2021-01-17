# import hashlib
# from datetime import datetime
# from sawtooth_sdk.protobuf import transaction_pb2, batch_pb2
#
# from addressing.b4e_addressing import addresser
# from protobuf.b4e_protobuf import payload_pb2
# from sawtooth_signing import create_context
# from sawtooth_signing import CryptoFactory
# from sawtooth_signing import secp256k1
# import time
# from sawtooth_sdk.protobuf.batch_pb2 import BatchList
# import requests
#
#
# def make_set_b4e_environment(signer, timestamp):
#     environment_address = addresser.ENVIRONMENT_ADDRESS
#     inputs = [environment_address]
#     outputs = [environment_address]
#
#     action = payload_pb2.SetB4EEnvironmentAction(timestamp=timestamp)
#
#     payload = payload_pb2.B4EPayload(
#         action=payload_pb2.B4EPayload.SET_B4E_ENVIRONMENT,
#         set_b4e_environment=action,
#         timestamp=timestamp
#     )
#
#     payload_bytes = payload.SerializeToString()
#     return _make_batch(
#         payload_bytes=payload_bytes,
#         inputs=inputs,
#         outputs=outputs,
#         transaction_signer=signer,
#         batch_signer=signer)
#
#
# def _make_batch(payload_bytes,
#                 inputs,
#                 outputs,
#                 transaction_signer,
#                 batch_signer):
#     transaction_header = transaction_pb2.TransactionHeader(
#         family_name=addresser.FAMILY_NAME,
#         family_version=addresser.FAMILY_VERSION,
#         inputs=inputs,
#         outputs=outputs,
#         signer_public_key=transaction_signer.get_public_key().as_hex(),
#         batcher_public_key=batch_signer.get_public_key().as_hex(),
#         dependencies=[],
#         payload_sha512=hashlib.sha512(payload_bytes).hexdigest())
#     transaction_header_bytes = transaction_header.SerializeToString()
#
#     transaction = transaction_pb2.Transaction(
#         header=transaction_header_bytes,
#         header_signature=transaction_signer.sign(transaction_header_bytes),
#         payload=payload_bytes)
#
#     batch_header = batch_pb2.BatchHeader(
#         signer_public_key=batch_signer.get_public_key().as_hex(),
#         transaction_ids=[transaction.header_signature])
#     batch_header_bytes = batch_header.SerializeToString()
#
#     batch = batch_pb2.Batch(
#         header=batch_header_bytes,
#         header_signature=batch_signer.sign(batch_header_bytes),
#         transactions=[transaction])
#
#     return batch
#
#
# def submit(batch):
#     batch_list_bytes = BatchList(batches=[batch]).SerializeToString()
#
#     try:
#         headers = {'Content-Type': 'application/octet-stream'}
#         res0 = requests.post(url='http://localhost:8008/batches', data=batch_list_bytes, headers=headers).json()
#         link = res0['link']
#         res = requests.get(link).json()
#         id = res['data'][0]['id']
#         timer = 0
#         timeout = 10
#         while (requests.get(link).json()['data'][0]['status'] != "COMMITTED"):
#             time.sleep(0.3)
#             timer += 1
#             if timer > timeout:
#                 return {"msg": "Transaction isn't committed"}
#
#         res2 = requests.get('http://0.0.0.0:8008/batches/' + id).json()
#         transaction_id = res2['data']['header']["transaction_ids"][0]
#         return {"transaction_id": transaction_id}
#     except Exception as e:
#         print(e)
#         return {"msg : ", e}
#
#
# def create_env(signer):
#     timestamp = int(datetime.utcnow().timestamp())
#     batch = make_set_b4e_environment(signer, timestamp)
#     return submit(batch)
#
#
# def create_signer(private_key):
#     context = create_context('secp256k1')
#     return CryptoFactory(context).new_signer(secp256k1.Secp256k1PrivateKey.from_hex(private_key))
#
#
# stu_public_key = "025a5477d1f0ad3780f2aa5224371dc779b38719581ae623dc665168d8e1b6ca60"
# stu_private_key = "4d8de40eba071a892c6edefa990c125a02501d230c58353aeac06e04553e8b30"
# stu_signer = create_signer(stu_private_key)
