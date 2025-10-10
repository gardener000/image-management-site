# config.py
import os
from dotenv import load_dotenv

# 定位 .env 文件的路径
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # 构建数据库URI
    # 格式: mysql+mysqlconnector://user:password@host:port/database_name
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://"
        f"{os.environ.get('DB_USER')}:"
        f"{os.environ.get('DB_PASSWORD')}@"
        f"{os.environ.get('DB_HOST')}:"
        f"{os.environ.get('DB_PORT')}/"
        f"{os.environ.get('DB_NAME')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # --- 新增 ---
    # 设置为 True 会在终端打印出所有执行的 SQL 语句
    SQLALCHEMY_ECHO = True 
    # ---
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'iloveb$sanddo&ngqi8anyu'

    # 定义图片上传的根目录
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')