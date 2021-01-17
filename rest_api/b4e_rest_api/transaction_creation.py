# Copyright 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License"),
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

import hashlib

from sawtooth_rest_api.protobuf import batch_pb2
from sawtooth_rest_api.protobuf import transaction_pb2

from addressing.b4e_addressing import addresser
from config.config import Sawtooth_Config
from protobuf.b4e_protobuf import payload_pb2

import logging
import datetime
import time

LOGGER = logging.getLogger(__name__)


def slice_per(source, step):
    if len(source) < step:
        return [source]
    return [source[i::step] for i in range(step)]


def make_set_b4e_environment(signer, timestamp):
    environment_address = addresser.ENVIRONMENT_ADDRESS
    inputs = [environment_address]
    outputs = [environment_address]

    action = payload_pb2.SetB4EEnvironmentAction(timestamp=timestamp)

    payload = payload_pb2.B4EPayload(
        action=payload_pb2.B4EPayload.SET_B4E_ENVIRONMENT,
        set_b4e_environment=action,
        timestamp=timestamp
    )

    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=signer,
        batch_signer=signer)


def make_create_institution(transaction_signer,
                            batch_signer,
                            profile,
                            timestamp):
    actor_address = addresser.get_actor_address(transaction_signer.get_public_key().as_hex())
    voting_address = addresser.get_voting_address(transaction_signer.get_public_key().as_hex())

    inputs = [actor_address, voting_address]

    outputs = [actor_address, voting_address]

    info = payload_pb2.Info(data=str(profile))

    action = payload_pb2.CreateInstitutionAction(info=info, id=profile.get('uid'))

    payload = payload_pb2.B4EPayload(
        action=payload_pb2.B4EPayload.CREATE_INSTITUTION,
        create_institution=action,
        timestamp=timestamp)

    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=transaction_signer,
        batch_signer=batch_signer)


def make_create_teacher(transaction_signer,
                        batch_signer,
                        profile,
                        timestamp):
    institution_address = addresser.get_actor_address(transaction_signer.get_public_key().as_hex())
    teacher_address = addresser.get_actor_address(profile['publicKey'])

    inputs = [institution_address, teacher_address]

    outputs = [teacher_address]

    info = payload_pb2.Info(data=str(profile))

    action = payload_pb2.CreateTeacherAction(info=info, teacher_public_key=profile['publicKey'],
                                             id=profile['teacherId'])

    payload = payload_pb2.B4EPayload(
        action=payload_pb2.B4EPayload.CREATE_TEACHER,
        create_teacher=action,
        timestamp=timestamp)

    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=transaction_signer,
        batch_signer=batch_signer)


def make_create_teachers(transaction_signer,
                         batch_signer,
                         profiles,
                         timestamp):
    institution_address = addresser.get_actor_address(transaction_signer.get_public_key().as_hex())

    list_profiles = slice_per(profiles, Sawtooth_Config.MAX_BATCH_SIZE)
    list_batches = []
    for profiles in list_profiles:
        list_inputs = []
        list_outputs = []
        list_payload_bytes = []
        for profile in profiles:
            teacher_address = addresser.get_actor_address(profile['publicKey'])
            inputs = [institution_address, teacher_address]

            outputs = [teacher_address]
            info = payload_pb2.Info(data=str(profiles))
            action = payload_pb2.CreateTeacherAction(info=info, teacher_public_key=profile.get('publicKey'),
                                                     id=profile.get('teacherId'))

            payload = payload_pb2.B4EPayload(
                action=payload_pb2.B4EPayload.CREATE_TEACHER,
                create_teacher=action,
                timestamp=timestamp)
            payload_bytes = payload.SerializeToString()

            list_inputs.append(inputs)
            list_outputs.append(outputs)
            list_payload_bytes.append(payload_bytes)

        batch = _make_batch_multi_transactions(
            list_payload_bytes=list_payload_bytes,
            list_inputs=list_inputs,
            list_outputs=list_outputs,
            transaction_signer=transaction_signer,
            batch_signer=batch_signer)
        list_batches.append(batch)

    return list_batches


def make_create_edu_officer(transaction_signer,
                            batch_signer,
                            profile,
                            timestamp):
    institution_address = addresser.get_actor_address(transaction_signer.get_public_key().as_hex())
    edu_officer_address = addresser.get_actor_address(profile.get('publicKey'))

    inputs = [institution_address, edu_officer_address]

    outputs = [edu_officer_address]

    info = payload_pb2.Info(data=str(profile))

    action = payload_pb2.CreateEduOfficerAction(info=info, edu_officer_public_key=profile.get('publicKey'),
                                                id=profile.get('bureauId'))

    payload = payload_pb2.B4EPayload(
        action=payload_pb2.B4EPayload.CREATE_EDU_OFFICER,
        create_edu_officer=action,
        timestamp=timestamp)

    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=transaction_signer,
        batch_signer=batch_signer)


def make_create_edu_officers(transaction_signer,
                             batch_signer,
                             profiles,
                             timestamp):
    institution_address = addresser.get_actor_address(transaction_signer.get_public_key().as_hex())

    list_profiles = slice_per(profiles, Sawtooth_Config.MAX_BATCH_SIZE)
    list_batches = []
    for profiles in list_profiles:
        list_inputs = []
        list_outputs = []
        list_payload_bytes = []
        for profile in profiles:
            edu_officer_address = addresser.get_actor_address(profile.get('publicKey'))

            inputs = [institution_address, edu_officer_address]

            outputs = [edu_officer_address]

            info = payload_pb2.Info(data=str(profile))

            action = payload_pb2.CreateEduOfficerAction(info=info, edu_officer_public_key=profile.get('publicKey'),
                                                        id=profile.get('bureauId'))

            payload = payload_pb2.B4EPayload(
                action=payload_pb2.B4EPayload.CREATE_EDU_OFFICER,
                create_edu_officer=action,
                timestamp=timestamp)
            payload_bytes = payload.SerializeToString()

            list_inputs.append(inputs)
            list_outputs.append(outputs)
            list_payload_bytes.append(payload_bytes)

        batch = _make_batch_multi_transactions(
            list_payload_bytes=list_payload_bytes,
            list_inputs=list_inputs,
            list_outputs=list_outputs,
            transaction_signer=transaction_signer,
            batch_signer=batch_signer)
        list_batches.append(batch)

    return list_batches


def make_create_vote(transaction_signer,
                     batch_signer,
                     issuer_public_key,
                     elector_public_key,
                     accepted,
                     timestamp):
    environment_address = addresser.ENVIRONMENT_ADDRESS
    voting_address = addresser.get_voting_address(elector_public_key)
    issuer_vote_address = addresser.get_actor_address(issuer_public_key)
    elector_address = addresser.get_actor_address(elector_public_key)

    inputs = [environment_address, voting_address, issuer_vote_address, elector_address]

    outputs = [voting_address, elector_address, environment_address]

    action = payload_pb2.CreateVoteAction(issuer_public_key=issuer_public_key, elector_public_key=elector_public_key,
                                          accepted=accepted)

    payload = payload_pb2.B4EPayload(
        action=payload_pb2.B4EPayload.CREATE_VOTE,
        create_vote=action,
        timestamp=timestamp)

    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=transaction_signer,
        batch_signer=batch_signer)


def make_create_class(transaction_signer,
                      batch_signer,
                      teacher_public_key,
                      edu_officer_public_key,
                      class_id,
                      timestamp):
    institution_public_key = transaction_signer.get_public_key().as_hex()
    class_address = addresser.get_class_address(class_id, institution_public_key)
    teacher_address = addresser.get_actor_address(teacher_public_key)
    edu_officer_address = addresser.get_actor_address(edu_officer_public_key)
    institution_address = addresser.get_actor_address(institution_public_key)
    inputs = [class_address, teacher_address, edu_officer_address, institution_address]

    outputs = [class_address]

    action = payload_pb2.CreateClassAction(class_id=class_id,
                                           teacher_public_key=teacher_public_key,
                                           edu_officer_public_key=edu_officer_public_key,
                                           timestamp=timestamp)

    payload = payload_pb2.B4EPayload(
        action=payload_pb2.B4EPayload.CREATE_CLASS,
        create_class=action,
        timestamp=timestamp)

    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=transaction_signer,
        batch_signer=batch_signer)


def make_create_classes(transaction_signer,
                        batch_signer,
                        classes,
                        timestamp):
    institution_public_key = transaction_signer.get_public_key().as_hex()
    institution_address = addresser.get_actor_address(institution_public_key)

    list_classes = slice_per(classes, Sawtooth_Config.MAX_BATCH_SIZE)
    list_batches = []
    for classes in list_classes:
        list_inputs = []
        list_outputs = []
        list_payload_bytes = []
        for class_ in classes:
            class_address = addresser.get_class_address(class_.get('classId'), institution_public_key)
            teacher_address = addresser.get_actor_address(class_.get('teacherPublicKey'))
            edu_officer_address = addresser.get_actor_address(class_.get('bureauPublicKey'))

            inputs = [class_address, teacher_address, edu_officer_address, institution_address]

            outputs = [class_address]

            action = payload_pb2.CreateClassAction(class_id=class_.get('classId'),
                                                   teacher_public_key=class_.get('teacherPublicKey'),
                                                   edu_officer_public_key=class_.get('bureauPublicKey'),
                                                   timestamp=timestamp)

            payload = payload_pb2.B4EPayload(
                action=payload_pb2.B4EPayload.CREATE_CLASS,
                create_class=action,
                timestamp=timestamp)

            payload_bytes = payload.SerializeToString()

            list_inputs.append(inputs)
            list_outputs.append(outputs)
            list_payload_bytes.append(payload_bytes)

        batch = _make_batch_multi_transactions(
            list_payload_bytes=list_payload_bytes,
            list_inputs=list_inputs,
            list_outputs=list_outputs,
            transaction_signer=transaction_signer,
            batch_signer=batch_signer)
        list_batches.append(batch)

    return list_batches


def make_create_record(transaction_signer,
                       batch_signer,
                       owner_public_key,
                       manager_public_key,
                       record_id,
                       record_type,
                       record_data,
                       timestamp):
    issuer_public_key = transaction_signer.get_public_key().as_hex()
    manager_address = addresser.get_actor_address(manager_public_key)
    issuer_address = addresser.get_actor_address(issuer_public_key)
    record_address = addresser.get_record_address(record_id, owner_public_key, manager_public_key)
    class_address = addresser.get_class_address(record_id, manager_public_key)

    inputs = [manager_address, issuer_address, record_address, class_address]

    outputs = [record_address]

    if record_type == 'SUBJECT':
        record_type = payload_pb2.SUBJECT
    elif record_type == 'CERTIFICATE':
        record_type = payload_pb2.CERTIFICATE

    action = payload_pb2.CreateRecordAction(owner_public_key=owner_public_key,
                                            manager_public_key=manager_public_key,
                                            issuer_public_key=issuer_public_key,
                                            record_id=record_id,
                                            record_type=record_type,
                                            record_data=record_data)

    payload = payload_pb2.B4EPayload(
        action=payload_pb2.B4EPayload.CREATE_RECORD,
        create_record=action,
        timestamp=timestamp)

    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=transaction_signer,
        batch_signer=batch_signer)


def make_create_subjects(transaction_signer,
                         batch_signer,
                         institution_public_key,
                         class_id,
                         list_subjects,
                         timestamp):
    issuer_public_key = transaction_signer.get_public_key().as_hex()
    manager_address = addresser.get_actor_address(institution_public_key)
    issuer_address = addresser.get_actor_address(issuer_public_key)
    class_address = addresser.get_class_address(class_id, institution_public_key)

    list_subjects = slice_per(list_subjects, Sawtooth_Config.MAX_BATCH_SIZE)
    list_batches = []
    for subjects in list_subjects:
        list_inputs = []
        list_outputs = []
        list_payload_bytes = []
        for subject in subjects:
            subject_address = addresser.get_record_address(class_id, subject.get('studentPublicKey'),
                                                           institution_public_key)
            inputs = [manager_address, issuer_address, subject_address, class_address]

            outputs = [subject_address]

            record_type = payload_pb2.SUBJECT

            action = payload_pb2.CreateRecordAction(owner_public_key=subject.get('studentPublicKey'),
                                                    manager_public_key=institution_public_key,
                                                    issuer_public_key=issuer_public_key,
                                                    record_id=class_id,
                                                    record_type=record_type,
                                                    record_data=subject.get('cipher'))

            payload = payload_pb2.B4EPayload(
                action=payload_pb2.B4EPayload.CREATE_RECORD,
                create_record=action,
                timestamp=timestamp)

            payload_bytes = payload.SerializeToString()

            list_inputs.append(inputs)
            list_outputs.append(outputs)
            list_payload_bytes.append(payload_bytes)

        batch = _make_batch_multi_transactions(
            list_payload_bytes=list_payload_bytes,
            list_inputs=list_inputs,
            list_outputs=list_outputs,
            transaction_signer=transaction_signer,
            batch_signer=batch_signer)
        list_batches.append(batch)

    return list_batches


def make_create_certs(transaction_signer,
                      batch_signer,
                      certs,
                      timestamp):
    issuer_public_key = transaction_signer.get_public_key().as_hex()
    institution_public_key = issuer_public_key
    manager_address = addresser.get_actor_address(institution_public_key)
    issuer_address = addresser.get_actor_address(issuer_public_key)

    list_certs = slice_per(certs, Sawtooth_Config.MAX_BATCH_SIZE)
    list_batches = []
    for certs in list_certs:
        list_inputs = []
        list_outputs = []
        list_payload_bytes = []
        for cert in certs:
            cert_id = cert.get('globalregisno')
            cert_address = addresser.get_record_address(cert_id, cert.get('studentPublicKey'),
                                                        institution_public_key)
            inputs = [manager_address, issuer_address, cert_address]

            outputs = [cert_address]
            record_type = payload_pb2.CERTIFICATE

            action = payload_pb2.CreateRecordAction(owner_public_key=cert.get('studentPublicKey'),
                                                    manager_public_key=institution_public_key,
                                                    issuer_public_key=issuer_public_key,
                                                    record_id=cert_id,
                                                    record_type=record_type,
                                                    record_data=cert.get('cipher'))

            payload = payload_pb2.B4EPayload(
                action=payload_pb2.B4EPayload.CREATE_RECORD,
                create_record=action,
                timestamp=timestamp)

            payload_bytes = payload.SerializeToString()

            list_inputs.append(inputs)
            list_outputs.append(outputs)
            list_payload_bytes.append(payload_bytes)

        batch = _make_batch_multi_transactions(
            list_payload_bytes=list_payload_bytes,
            list_inputs=list_inputs,
            list_outputs=list_outputs,
            transaction_signer=transaction_signer,
            batch_signer=batch_signer)
        list_batches.append(batch)

    return list_batches


def make_update_record(transaction_signer,
                       batch_signer,
                       owner_public_key,
                       manager_public_key,
                       record_id,
                       record_data,
                       active,
                       timestamp):
    manager_address = addresser.get_actor_address(transaction_signer.get_public_key().as_hex())
    record_address = addresser.get_record_address(record_id, owner_public_key, manager_public_key, )

    inputs = [manager_address, record_address]

    outputs = [record_address]

    action = payload_pb2.UpdateRecordAction(record_id=record_id,
                                            record_data=record_data,
                                            owner_public_key=owner_public_key,
                                            manager_public_key=manager_public_key,
                                            active=active)

    payload = payload_pb2.B4EPayload(
        action=payload_pb2.B4EPayload.UPDATE_RECORD,
        update_record=action,
        timestamp=timestamp)

    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=transaction_signer,
        batch_signer=batch_signer)


def make_update_actor_info(transaction_signer,
                           batch_signer,
                           name,
                           phone,
                           email,
                           address,
                           timestamp):
    actor_address = addresser.get_actor_address(transaction_signer.get_public_key().as_hex())

    inputs = [actor_address]

    outputs = [actor_address]

    info = payload_pb2.Info(name=name, phone=phone, email=email, address=address)
    action = payload_pb2.UpdateActorInfoAction(info=info)

    payload = payload_pb2.B4EPayload(
        action=payload_pb2.B4EPayload.UPDATE_ACTOR_INFO,
        update_actor_info=action,
        timestamp=timestamp)

    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=transaction_signer,
        batch_signer=batch_signer)


def _make_batch(payload_bytes,
                inputs,
                outputs,
                transaction_signer,
                batch_signer):
    transaction_header = transaction_pb2.TransactionHeader(
        family_name=addresser.FAMILY_NAME,
        family_version=addresser.FAMILY_VERSION,
        inputs=inputs,
        outputs=outputs,
        signer_public_key=transaction_signer.get_public_key().as_hex(),
        batcher_public_key=batch_signer.get_public_key().as_hex(),
        dependencies=[],
        payload_sha512=hashlib.sha512(payload_bytes).hexdigest())
    transaction_header_bytes = transaction_header.SerializeToString()

    transaction = transaction_pb2.Transaction(
        header=transaction_header_bytes,
        header_signature=transaction_signer.sign(transaction_header_bytes),
        payload=payload_bytes)

    batch_header = batch_pb2.BatchHeader(
        signer_public_key=batch_signer.get_public_key().as_hex(),
        transaction_ids=[transaction.header_signature])
    batch_header_bytes = batch_header.SerializeToString()

    batch = batch_pb2.Batch(
        header=batch_header_bytes,
        header_signature=batch_signer.sign(batch_header_bytes),
        transactions=[transaction])

    return batch


def _make_batch_multi_transactions(list_payload_bytes,
                                   list_inputs,
                                   list_outputs,
                                   transaction_signer,
                                   batch_signer):
    list_transactions = []
    list_transaction_ids = []
    for i in range(len(list_inputs)):
        transaction_header = transaction_pb2.TransactionHeader(
            family_name=addresser.FAMILY_NAME,
            family_version=addresser.FAMILY_VERSION,
            inputs=list_inputs[i],
            outputs=list_outputs[i],
            signer_public_key=transaction_signer.get_public_key().as_hex(),
            batcher_public_key=batch_signer.get_public_key().as_hex(),
            dependencies=[],
            payload_sha512=hashlib.sha512(list_payload_bytes[i]).hexdigest())

        transaction_header_bytes = transaction_header.SerializeToString()

        transaction = transaction_pb2.Transaction(
            header=transaction_header_bytes,
            header_signature=transaction_signer.sign(transaction_header_bytes),
            payload=list_payload_bytes[i])
        list_transactions.append(transaction)
        list_transaction_ids.append(transaction.header_signature)

    batch_header = batch_pb2.BatchHeader(
        signer_public_key=batch_signer.get_public_key().as_hex(),
        transaction_ids=list_transaction_ids)
    batch_header_bytes = batch_header.SerializeToString()

    batch = batch_pb2.Batch(
        header=batch_header_bytes,
        header_signature=batch_signer.sign(batch_header_bytes),
        transactions=list_transactions)

    return batch
