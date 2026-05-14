import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'thinkphp-python-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.getcwd(), 'runtime', 'database.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 上传配置
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'public', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
