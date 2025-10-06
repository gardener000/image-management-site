# app.py
from flask import Flask
from config import Config
from extensions import db, migrate


def create_app(config_class=Config):
    # 创建并配置app
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 将数据库实例与app关联
    db.init_app(app)
    migrate.init_app(app, db)

    # 在这里导入模型，确保它们被SQLAlchemy识别
    from models import User, Image, Tag

    # 导入并注册蓝图
    # 从 routes.auth 模块导入 auth_bp 蓝图
    from routes.auth import auth_bp
    # 注册蓝图，并为其添加URL前缀 /api/auth
    # 这样 auth.py 里的 /register 路由就会变成 /api/auth/register
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # 一个简单的测试路由
    @app.route('/')
    def index():
        return "Backend server is running!"

    return app

# 我们需要一个 app 实例来运行，所以要调用 create_app
app = create_app()
# 这段代码使得我们可以直接运行 python app.py 来启动服务器
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)