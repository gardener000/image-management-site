# backend/routes/auth.py

import re
from flask import Blueprint, request, jsonify
from models import User, db  # 从 models.py 导入 User 模型和 db 实例

# 创建一个名为 'auth' 的蓝图
auth_bp = Blueprint('auth', __name__)

# 定义一个用于验证 email 格式的函数
def is_valid_email(email):
    # 一个简单的正则表达式用于验证email
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email) is not None
from flask_jwt_extended import create_access_token

@auth_bp.route('/register', methods=['POST'])
def register():
    # 1. 从请求中获取JSON数据
    data = request.get_json()
    if not data:
        return jsonify({"error": "无效的请求，需要JSON格式的数据"}), 400

    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    # 2. 验证输入数据的有效性
    if not all([username, password, email]):
        return jsonify({"error": "用户名、密码和邮箱都不能为空"}), 400

    if len(username) < 6:
        return jsonify({"error": "用户名长度不能少于6位"}), 400
    
    if len(password) < 6:
        return jsonify({"error": "密码长度不能少于6位"}), 400

    if not is_valid_email(email):
        return jsonify({"error": "无效的邮箱格式"}), 400

    # 3. 检查用户名和邮箱是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "该用户名已被注册"}), 409 # 409 Conflict

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "该邮箱已被注册"}), 409

    # 4. 创建新用户并保存到数据库
    try:
        new_user = User(username=username, email=email)
        new_user.set_password(password) # 使用我们模型里的方法来加密密码
        
        db.session.add(new_user)
        db.session.commit()

        # 5. 返回成功响应
        return jsonify({"message": "用户注册成功"}), 201 # 201 Created
    except Exception as e:
        db.session.rollback() # 如果发生错误，回滚数据库操作
        return jsonify({"error": "服务器内部错误", "details": str(e)}), 500
    
@auth_bp.route('/login', methods=['POST'])
def login():
    # 1. 从请求中获取JSON数据
    data = request.get_json()
    if not data:
        return jsonify({"error": "无效的请求，需要JSON格式的数据"}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "用户名和密码不能为空"}), 400

    # 2. 在数据库中查找用户
    user = User.query.filter_by(username=username).first()

    # 3. 验证用户是否存在以及密码是否正确
    #    使用 User 模型中的 check_password 方法
    if user is None or not user.check_password(password):
        return jsonify({"error": "用户名或密码错误"}), 401 # 401 Unauthorized

    # 4. 如果验证成功，为用户创建一个 access token
    #    我们使用 user.id 作为 token 的身份标识
    access_token = create_access_token(identity=str(user.id)) #修改：将 user.id 强制转换为字符串
    
    # 5. 返回 token
    return jsonify(access_token=access_token)
