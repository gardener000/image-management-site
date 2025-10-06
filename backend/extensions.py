# backend/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

# 创建扩展实例，但不在这里关联 app
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()