from sawtooth_sdk.processor.exceptions import InvalidTransaction
from protobuf.b4e_protobuf import actor_pb2
from protobuf.b4e_protobuf import record_pb2
from protobuf.b4e_protobuf import payload_pb2
from protobuf.b4e_protobuf import voting_pb2
from protobuf.b4e_protobuf import b4e_environment_pb2
from protobuf.b4e_protobuf import class_pb2

import datetime
import time

import logging

LOGGER = logging.getLogger(__name__)

# ministry key pair for dev
# ministry_public_key = "037dd31d79a82b44a3a24314bcdb8ea472dd7da3e07a2c96ff9fce4588b7e6464f"
# ministry_private_key = "6cebf871e936d15b6540dc714dcff176839f73359d30ae49ae8ec1d44bd276db"
list_ministry_public_key = []
with open("list_ministry_public_key") as fp:
    for line in fp:
        list_ministry_public_key.append(line.strip())

VOTE_RATE = 0.5


def set_b4e_environment(state, public_key, transaction_id, payload):
    if not state.get_b4e_environment():
        state.set_b4e_environment(transaction_id)

    else:
        raise InvalidTransaction("Environment just set once time!")


def _check_is_valid_actor(actor):
    if not actor:
        raise InvalidTransaction("Actor doesn't exist")
    if actor.status != actor_pb2.ACTIVE:
        raise InvalidTransaction("Actor is not active")


def _create_actor(state, transaction_id, public_key, manager_public_key, status, payload, role):
    if state.get_actor(public_key):
        raise InvalidTransaction("Actor existed!")
    actor_public_key = public_key
    actor_id = payload.data.id
    info = actor_pb2.Actor.Info(data=payload.data.info.data,
                                transaction_id=transaction_id,
                                timestamp=payload.timestamp)

    actor = actor_pb2.Actor(actor_public_key=actor_public_key,
                            manager_public_key=manager_public_key,
                            status=status,
                            info=[info],
                            id=actor_id,
                            role=role,
                            transaction_id=transaction_id,
                            timestamp=payload.timestamp)

    state.set_actor(actor, public_key)


def create_institution(state, public_key, transaction_id, payload):
    _create_actor(state, transaction_id, public_key, public_key, actor_pb2.WAITING, payload,
                  actor_pb2.Actor.INSTITUTION)

    voting = voting_pb2.Voting(elector_public_key=public_key,
                               data=payload.data.info.data,
                               timestamp=payload.timestamp,
                               close_vote_timestamp=0,
                               voteType=voting_pb2.Voting.ACTIVE,
                               vote_result=voting_pb2.Voting.UNKNOWN,
                               vote=[],
                               transaction_id=transaction_id)

    state.set_voting(voting, public_key)


def create_teacher(state, public_key, transaction_id, payload):
    institution = state.get_actor(public_key)
    _check_is_valid_actor(institution)

    if institution.role != actor_pb2.Actor.INSTITUTION:
        raise InvalidTransaction("Invalid signer!")

    _create_actor(state, transaction_id, payload.data.teacher_public_key, public_key, actor_pb2.ACTIVE, payload,
                  actor_pb2.Actor.TEACHER)


def create_edu_officer(state, public_key, transaction_id, payload):
    institution = state.get_actor(public_key)
    _check_is_valid_actor(institution)
    if institution.role != actor_pb2.Actor.INSTITUTION:
        raise InvalidTransaction("Invalid signer!")

    _create_actor(state, transaction_id, payload.data.edu_officer_public_key, public_key, actor_pb2.ACTIVE, payload,
                  actor_pb2.Actor.EDU_OFFICER)


def vote(state, public_key, transaction_id, payload):
    close_vote_timestamp = 0
    voting = state.get_voting(payload.data.elector_public_key)
    if not voting:
        raise InvalidTransaction("Voting doesn't exist")
    if voting.close_vote_timestamp > 0:
        raise InvalidTransaction("Voting has been closed")
    if public_key == voting.elector_public_key:
        raise InvalidTransaction("You can't vote for yourself")

    for vote in voting.vote:
        if vote.issuer_public_key == public_key:
            raise InvalidTransaction("Issuer has voted!")

    actor_vote = voting_pb2.Voting.Vote(issuer_public_key=public_key, accepted=payload.data.accepted,
                                        timestamp=payload.timestamp, transaction_id=transaction_id)
    if public_key in list_ministry_public_key:

        if payload.data.accepted:
            close_vote_timestamp = payload.timestamp
            vote_result = voting_pb2.Voting.WIN
            state.add_one_b4e_environment(transaction_id=transaction_id)

            state.set_active_actor(payload.data.elector_public_key)
        else:
            vote_result = voting_pb2.Voting.UNKNOWN

        state.update_voting(payload.data.elector_public_key, vote_result,
                            actor_vote, timestamp=close_vote_timestamp)

        return

    actor = state.get_actor(public_key)
    _check_is_valid_actor(actor)
    if actor.role != actor_pb2.Actor.INSTITUTION:
        raise InvalidTransaction("Actor must be INSTITUTION")

    env = state.get_b4e_environment()
    election = voting.vote
    accept = 0
    reject = 0
    total = env.institution_number + 1
    # count accept and reject voted
    for voted in election:
        if voted.accepted:
            accept += 1
        else:
            reject += 1
    # add voted
    if payload.data.accepted:
        accept += 1
    else:
        reject += 1

    # check for close vote
    if accept / total > VOTE_RATE:
        vote_result = voting_pb2.Voting.WIN
        state.update_voting(payload.data.elector_public_key, vote_result,
                            actor_vote, timestamp=payload.timestamp)
        state.set_active_actor(payload.data.elector_public_key)
        return

    if reject / total > VOTE_RATE:
        vote_result = voting_pb2.Voting.LOSE
        state.update_voting(payload.data.elector_public_key, vote_result,
                            actor_vote, timestamp=payload.timestamp)
        state.set_reject_actor(payload.data.elector_public_key)
        return
    #
    vote_result = voting_pb2.Voting.UNKNOWN
    state.update_voting(payload.data.elector_public_key, vote_result,
                        actor_vote, timestamp=close_vote_timestamp)


def create_class(state, public_key, transaction_id, payload):
    institution = state.get_actor(public_key)
    _check_is_valid_actor(institution)

    if institution.role != actor_pb2.Actor.INSTITUTION:
        raise InvalidTransaction("Just institution can create class")

    if state.get_class(payload.data.class_id, public_key):
        raise InvalidTransaction("Class existed!")

    class_ = class_pb2.Class(teacher_public_key=payload.data.teacher_public_key,
                             edu_officer_public_key=payload.data.edu_officer_public_key,
                             institution_public_key=public_key,
                             timestamp=payload.timestamp,
                             class_id=payload.data.class_id,
                             transaction_id=transaction_id)

    state.set_class(payload.data.class_id, class_)


def _get_record_type(i):
    switcher = {
        payload_pb2.CERTIFICATE: record_pb2.Record.CERTIFICATE,
        payload_pb2.SUBJECT: record_pb2.Record.SUBJECT
    }
    return switcher.get(i)


def create_record(state, public_key, transaction_id, payload):
    actor = state.get_actor(public_key)
    _check_is_valid_actor(actor)
    record_id = payload.data.record_id
    owner_public_key = payload.data.owner_public_key
    manager_public_key = payload.data.manager_public_key

    if state.get_record(record_id, owner_public_key, manager_public_key):
        raise InvalidTransaction("Record has been existed")

    if payload.data.record_type == payload_pb2.CERTIFICATE and actor.role != actor_pb2.Actor.INSTITUTION:
        raise InvalidTransaction("Just Institution can't create certificate")

    if actor.role == actor_pb2.Actor.TEACHER or actor.role == actor_pb2.Actor.EDU_OFFICER:
        class_ = state.get_class(payload.data.record_id, manager_public_key)
        if not class_:
            raise InvalidTransaction("Class doesn't exist!")

        if public_key != class_.teacher_public_key and public_key != class_.edu_officer_public_key:
            raise InvalidTransaction("Invalid issuer for this class")

    record_type = _get_record_type(payload.data.record_type)

    record_data = record_pb2.Record.RecordData(record_data=payload.data.record_data,
                                               active=True,
                                               timestamp=payload.timestamp,
                                               transaction_id=transaction_id)
    record = record_pb2.Record(owner_public_key=payload.data.owner_public_key,
                               manager_public_key=payload.data.manager_public_key,
                               issuer_public_key=payload.data.issuer_public_key,
                               record_id=payload.data.record_id,
                               record_type=record_type,
                               record_data=[record_data],
                               timestamp=payload.timestamp,
                               transaction_id=transaction_id)

    state.set_record(payload.data.record_id, record)


def update_record(state, public_key, transaction_id, payload):
    actor = state.get_actor(public_key)
    _check_is_valid_actor(actor)
    record_id = payload.data.record_id
    owner_public_key = payload.data.owner_public_key
    manager_public_key = payload.data.manager_public_key
    record = state.get_record(record_id, owner_public_key, manager_public_key)
    if not record:
        raise InvalidTransaction("Record doesn't exist")

    class_ = state.get_class(payload.data.record_id, manager_public_key)
    has_permission = False
    if class_:
        if class_.edu_officer_public_key == public_key:
            has_permission = True

    if public_key != record.manager_public_key or has_permission:
        raise InvalidTransaction("Invalid permission")

    state.update_record(record_id, owner_public_key, manager_public_key, payload.data.record_data, payload.data.active,
                        payload.timestamp, transaction_id)


def update_actor_info(state, public_key, transaction_id, payload):
    actor = state.get_actor(public_key)
    _check_is_valid_actor(actor)

    if actor.actor_public_key != public_key:
        raise InvalidTransaction("Illegal")

    info = actor_pb2.Actor.Info(name=payload.data.info.name,
                                phone=payload.data.info.phone,
                                email=payload.data.info.email,
                                address=payload.data.info.address,
                                timestamp=payload.timestamp,
                                transaction_id=transaction_id)

    state.update_actor_info(public_key, info)


def get_time():
    dts = datetime.datetime.utcnow()
    return round(time.mktime(dts.timetuple()) + dts.microsecond / 1e6)


def add_years(d, years):
    try:
        # Return same day of the current year
        return d.replace(year=d.year + years)
    except ValueError:
        # If not same day, it will return other, i.e.  February 29 to March 1 etc.
        return d + (datetime.date(d.year + years, 1, 1) - datetime.date(d.year, 1, 1))


def timestamp_to_datetime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)


def to_time_stamp(date_time):
    return datetime.datetime.timestamp(date_time)
