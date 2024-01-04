from config.default import *

SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'pybo.db'))
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = b'A\x90\xf0\xfc}wR\xe8\xd2C\x93\xec\xf8\xc5\x8a\xa2'