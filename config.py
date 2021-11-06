import base64
import os

MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = '3306'
MYSQL_USER = 'user_c'
MYSQL_PWD = base64.b64decode("MTIzNDU2").decode('utf-8')
MYSQL_DB = 'PROJECT_MODEL'


class Config:
    DEBUG = False
    TESTING = False

    @staticmethod
    def init_app(app):
        pass


class ProductionConfig(Config):  # 继承config基类
    # #产品中实际使用的config模块
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s/%s?charset=utf8mb4' % (
    MYSQL_USER, MYSQL_PWD, MYSQL_HOST, MYSQL_DB)
    #   SECRET_KEY = 'This is my key'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'main/media')
    UPLOADED_PHOTOS_DEST = os.path.join(os.path.dirname(__file__), 'main/media/images')

    FA_NETWORK_MODEL_PATH = "/home/czd-2019/Projects/MTL-face-attribute-classification/checkpoint_Jan08_structure_2_fixbugs_fixSAbugs_mid2_mid3_acc9220_epoch59/checkpoint_epoch59.pth"


class DevelopmentConfig(Config):
    ##开发人员使用的Config
    # DEBUG = True
    IS_FA_NET_USED = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s/%s?charset=utf8mb4' % (
    MYSQL_USER, MYSQL_PWD, MYSQL_HOST, MYSQL_DB)
    # SECRET_KEY = 'This is my key'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    FA_NETWORK_MODEL_PATH = "/home/czd-2019/Projects/MTL-face-attribute-classification/checkpoint_Jan08_structure_2_fixbugs_fixSAbugs_mid2_mid3_acc9220_epoch59/checkpoint_epoch59.pth"

class TestingConfig(Config):
    # 用于测试的config类
    TESTING = True


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
