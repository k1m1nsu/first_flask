import os

BASE_DIR=os.path.dirname(__file__)


SQLALCHEMY_DATABASE_URI='sqlite:///{}'.format(os.path.join(BASE_DIR,'pybo.db'))

SQLALCHEMY_TRACK_MODIFICATIONS=False

# Flask_WTF 이라 불리는 플라스크 라이브러리 환경변수 설정
SECRET_KEY="dev"
