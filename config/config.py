import os


class Config:
    HOST = '0.0.0.0'
    PORT = 8082


class Sawtooth_Config:
    REST_API = 'http://localhost:8008'
    VALIDATOR_TCP = 'tcp://localhost:4004'
    MAX_BATCH_SIZE = 1000


class ElasticSearchConfig:
    HOST = 'localhost'
    PORT = 9200
    USER_INDEX = 'b4e_users'
    STUDENT_INDEX = 'b4e_students'
    INSTITUTION_INDEX = 'b4e_institutions'
    MINISTRY_INDEX = 'b4e_ministries'
    CERT_INDEX = 'b4e_certs'
    SUBJECT_INDEX = 'b4e_subjects'
    TEACHER_INDEX = 'b4e_teachers'
    SERVICE_TEACHER_INDEX = 'b4e_service_teachers'
    COURSE_INDEX = "b4e_courses"
    RECORD_INDEX = "b4e_records"
    BLOCK_INDEX = "b4e_blocks"
    MANAGER_INDEX = 'b4e_managers'
    LANDINGPAGE = 'b4e_landingpages'


class MongoDBConfig:
    DOCKER_HOST = "b4e_network"
    HOST = "localhost"
    PORT = 27017
    USER_NAME = ""
    PASSWORD = ""
    DATABASE = "EXPLORER"
    UNIVERSITY_PROFILE = "UniversityProfile"
    VOTE_REQUEST = "VoteRequest"
    USER_COLLECTION = 'b4e_users'
    ENVIRONMENT_COLLECTION = 'b4e_environments'
    CLASS_COLLECTION = 'b4e_classes'
    ACTOR_COLLECTION = 'b4e_actors'
    CERT_COLLECTION = 'b4e_certs'
    SUBJECT_COLLECTION = 'b4e_subjects'
    VOTING_COLLECTION = 'b4e_votings'
    VOTE_COLLECTION = 'b4e_votes'
    SERVICE_TEACHER_COLLECTION = 'b4e_service_teachers'
    COURSE_COLLECTION = "b4e_courses"
    RECORD_COLLECTION = "b4e_records"
    BLOCK_COLLECTION = "b4e_blocks"
    TRANSACTION_COLLECTION = "b4e_transactions"
    TRANSACTION_FAMILY_COLLECTION = "b4e_transaction_families"
    MANAGER_COLLECTION = 'b4e_managers'
    REGISTRATION_COLLECTION = 'b4e_registrations'


class Status:
    ACTIVE = 1
    REJECT = 0
    WAIT = 2
    DELETE = 3


class Key_default:
    TOKEN = "TOKEN_SHARE"
    PERMISSION = "token_permission_key"


class Role:
    MINISTRY = 1
    INSTITUTION = 2
    STUDENT = 3
    GUEST = 4
    TEACHER = 21
    MANAGER = 22


class EmailConfig:
    SMTP_SSL_HOST = 'smtp.gmail.com'  # smtp.mail.yahoo.com
    SMTP_SSL_PORT = 587
    USERNAME = 'vchain.bkc'
    PASSWORD = 'bkc@12345'
    SENDER = 'vchain.bkc@gmail.com'
    SMTP_SSL_PORT2 = 465
    B4E_EMAIL_VERIFY = 'b.cert.verify@gmail.com'
    B4E_EMAIL_VERIFY_PASSWORD = 'bcert01012020'


class JWT:
    JWT_SECRET_KEY = "B4E_app_authentication"


class Permission:
    YES = 1
    NO = 0


class LandingPage:
    QRCODEPATH = './static/qrcode/'
    BARCODEPATH = './static/barcode/'
    URL = '202.191.56.247:8000/landingpage'
    CLOSE_LIST = "close_list"


class Ipfs:
    HOST = "https://ipfs.infura.io"
    PORT = 5001


class Test:
    MINISTRY_PRIVATE_KEY = "6cebf871e936d15b6540dc714dcff176839f73359d30ae49ae8ec1d44bd276db"
    CIPHER = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    DATABASE = "test_db"
    TEST_COLLECTION = "test_collection"
