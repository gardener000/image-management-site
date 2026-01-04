# app.py
from flask import Flask
from flask import send_from_directory
from flask_cors import CORS
from config import Config
from extensions import db, migrate, jwt


def create_app(config_class=Config):
    # 创建并配置app
    app = Flask(__name__)
    app.config.from_object(config_class)

    @app.route('/uploads/<path:filename>')
    def serve_uploads(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    CORS(app, 
         resources={
             r"/api/*": {"origins": "*"},
             r"/uploads/*": {"origins": "*"}
             },
         allow_headers=["Authorization", "Content-Type"], 
         supports_credentials=True)

    # 将数据库实例与app关联
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app) # <-- 初始化 jwt

    # 在这里导入模型，确保它们被SQLAlchemy识别
    from models import User, Image, Tag

    from routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    from routes.image import image_bp
    app.register_blueprint(image_bp, url_prefix='/api/images')
    # --- 新增 ---
    from routes.tag import tag_bp
    app.register_blueprint(tag_bp, url_prefix='/api/tags')
    # 一个简单的测试路由
    @app.route('/')
    def index():
        return "Backend server is running!"

    return app

app = create_app()
# 这段代码使得我们可以直接运行 python app.py 来启动服务器
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0')