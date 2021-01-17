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

import argparse
import sys
import logging

from subscriber_b4e.b4e_subscriber.mongodb import Database
from subscriber_b4e.b4e_subscriber.subscriber import Subscriber
from subscriber_b4e.b4e_subscriber.event_handling import get_events_handler

from config.config import Sawtooth_Config, MongoDBConfig

KNOWN_COUNT = 15
LOGGER = logging.getLogger(__name__)


def parse_args(args):
    parser = argparse.ArgumentParser(add_help=False)

    subparsers = parser.add_subparsers(title='subcommands', dest='command')
    subparsers.required = True

    database_parser = argparse.ArgumentParser(add_help=False)
    database_parser.add_argument(
        '--db-name',
        help='The name of the database',
        default='b4e')
    database_parser.add_argument(
        '--db-host',
        help='The host of the database',
        default='localhost')
    database_parser.add_argument(
        '--db-port',
        help='The port of the database',
        default='27017')
    database_parser.add_argument(
        '--db-user',
        help='The authorized user of the database',
        default='')
    database_parser.add_argument(
        '--db-password',
        help="The authorized user's password for database access",
        default='')
    database_parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=0,
        help='Increase output sent to stderr')
    subparsers.add_parser(
        'init',
        parents=[database_parser])

    subscribe_parser = subparsers.add_parser(
        'subscribe',
        parents=[database_parser])
    subscribe_parser.add_argument(
        '-C', '--connect',
        help='The url of the validator to subscribe to',
        default='tcp://localhost:4004')

    subscribe_parser.add_argument(
        '-R', '--restapi',
        help='specify URL to connect to a running validator',
        default='http://localhost:8008')

    return parser.parse_args(args)


def init_logger(level):
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())
    if level == 1:
        logger.setLevel(logging.INFO)
    elif level > 1:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARN)


def do_subscribe():
    LOGGER.info('Starting subscriber_b4e...')
    try:
        database = Database()
        database.connect(host=MongoDBConfig.HOST, port=MongoDBConfig.PORT, user_name=MongoDBConfig.USER_NAME,
                         password=MongoDBConfig.PASSWORD)
        subscriber = Subscriber(Sawtooth_Config.VALIDATOR_TCP)
        subscriber.add_handler(get_events_handler(database))
        known_blocks = database.fetch_last_known_blocks(KNOWN_COUNT)
        known_ids = [block['block_id'] for block in known_blocks]
        subscriber.start(known_ids=known_ids)

    except KeyboardInterrupt:
        sys.exit(0)

    except Exception as err:  # pylint: disable=broad-except
        LOGGER.exception(err)
        sys.exit(1)

    finally:
        try:
            database.disconnect()
            subscriber.stop()
        except UnboundLocalError:
            pass

    LOGGER.info('Subscriber shut down successfully')


def do_init():
    LOGGER.info('Initializing subscriber_b4e...')
    try:

        database = Database()
        database.connect()
        print("creating indexes")
        database.create_collections()

    except Exception as err:  # pylint: disable=broad-except
        LOGGER.exception('Unable to initialize subscriber_b4e database: %s', err)

    finally:
        database.disconnect()


def main():
    opts = parse_args(sys.argv[1:])
    init_logger(opts.verbose)
    MongoDBConfig.USER_NAME = opts.db_user
    MongoDBConfig.PASSWORD = opts.db_password
    MongoDBConfig.HOST = opts.db_host
    MongoDBConfig.PORT = opts.db_port
    Sawtooth_Config.VALIDATOR_TCP = opts.connect
    Sawtooth_Config.REST_API = opts.restapi
    LOGGER.info("database host:" + MongoDBConfig.HOST)
    do_subscribe()


if __name__ == '__main__':
    # do_init()
    do_subscribe()
