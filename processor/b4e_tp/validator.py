import datetime
import time

from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction

SYNC_TOLERANCE = 60 * 5


def is_active(object):
    return max(object.infos, key=lambda obj: obj.timestamp).active


def validate_timestamp(timestamp):
    """Validates that the client submitted timestamp for a transaction is not
    greater than current time, within a tolerance defined by SYNC_TOLERANCE

    NOTE: Timestamp validation can be challenging since the machines that are
    submitting and validating transactions may have different system times
    """
    dts = datetime.datetime.utcnow()
    current_time = round(time.mktime(dts.timetuple()) + dts.microsecond / 1e6)
    if (timestamp - current_time) > SYNC_TOLERANCE:
        raise InvalidTransaction(
            'Timestamp must be less than local time.'
            ' Expected {0} in ({1}-{2}, {1}+{2})'.format(
                timestamp, current_time, SYNC_TOLERANCE))


def validate_record(record):
    latest_state = max(record.infos, key=lambda obj: obj.timestamp)
    return latest_state


def validate_issuer(state, issuer_public_key):
    pass


def latest_manager_public_key_record(record):
    return max(record.managers, key=lambda obj: obj.timestamp).manager_public_key


def _validate_manager(signer_public_key, record):
    pass
