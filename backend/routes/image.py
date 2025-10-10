# backend/routes/image.py
import os
import uuid
import exifread
from PIL import Image as PILImage # 使用别名避免与 models.Image 冲突
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models import Image, db,Tag,image_tags
from sqlalchemy import and_

# 创建一个名为 'image' 的蓝图
image_bp = Blueprint('image', __name__)

# 定义允许上传的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@image_bp.route('/upload', methods=['POST'])
@jwt_required() # <--- 这是一个“保护器”，确保只有携带有效JWT的请求才能访问此路由
def upload_image():
    # 1. 从JWT中获取当前登录用户的ID
    current_user_id = int(get_jwt_identity())

    # 2. 检查请求中是否包含文件
    if 'file' not in request.files:
        return jsonify({"error": "请求中未包含文件部分"}), 400
    
    file = request.files['file']

    # 3. 检查文件名是否有效
    if file.filename == '':
        return jsonify({"error": "未选择文件"}), 400

    if file and allowed_file(file.filename):
        # 4. 生成一个安全且唯一的文件名，防止文件名冲突和安全问题
        #    使用UUID来保证唯一性
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = str(uuid.uuid4()) + '.' + ext
        
        # 5. 创建用户专属的文件夹路径，例如：uploads/user_1/
        user_upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f'user_{current_user_id}')
        os.makedirs(user_upload_path, exist_ok=True) # 如果文件夹不存在，则创建它

        # 6. 保存原始图片
        original_path = os.path.join(user_upload_path, unique_filename)
        file.save(original_path)

        # 7. --- 图像处理和信息提取 ---
        try:
            # 提取EXIF信息
            with open(original_path, 'rb') as f:
                tags = exifread.process_file(f,details=False)
            
            exif_data = {key: str(val) for key, val in tags.items() if key not in ('JPEGThumbnail', 'TIFFThumbnail')}
            
            # --- 新增：从EXIF中提取拍摄日期 ---
            date_time_tag = None
            if 'EXIF DateTimeOriginal' in tags:
                # 格式通常是 '2024:10:27 15:30:00'
                date_str = str(tags['EXIF DateTimeOriginal'])
                # 尝试解析年份和月份
                try:
                    year = date_str.split(':')[0]
                    month = date_str.split(':')[1]
                    if year.isdigit() and month.isdigit():
                        date_time_tag = f"{year}年{month}月"
                except IndexError:
                    # 日期格式不规范，忽略
                    pass

            # 使用Pillow库处理图片
            with PILImage.open(original_path) as img:
                # 获取分辨率
                resolution = f"{img.width}x{img.height}"
                
                # 生成缩略图
                thumbnail_filename = 'thumb_' + unique_filename
                thumbnail_path = os.path.join(user_upload_path, thumbnail_filename)
                
                # 保持宽高比生成缩略图，最大尺寸为400x400
                img.thumbnail((400, 400))
                img.save(thumbnail_path)

            # 8. 将图片信息存入数据库
            new_image = Image(
                user_id=current_user_id,
                original_filename=secure_filename(file.filename),
                storage_path=os.path.relpath(original_path, current_app.config['UPLOAD_FOLDER']), # 存储相对路径
                thumbnail_path=os.path.relpath(thumbnail_path, current_app.config['UPLOAD_FOLDER']),
                mime_type=file.mimetype,
                size=os.path.getsize(original_path),
                resolution=resolution,
                exif_data=exif_data
            )
            db.session.add(new_image)
            db.session.flush()
            
            # --- 新增：处理自动生成的标签 ---
            if date_time_tag:
                # 查找标签是否已存在
                tag_obj = Tag.query.filter_by(name=date_time_tag).first()
                
                # 如果标签不存在，则创建新标签
                if not tag_obj:
                    tag_obj = Tag(name=date_time_tag)
                    db.session.add(tag_obj)
                    # 再次 flush，让新标签也获得 id
                    db.session.flush()
                
                # 将图片和标签关联起来
                # 我们在 Image 模型中定义了 tags 关系，可以直接 append
                new_image.tags.append(tag_obj)
            # 提交整个事务（图片信息和标签关联）
            db.session.commit()
            return jsonify({"message": "图片上传成功", "imageId": new_image.id}), 201

        except Exception as e:
            db.session.rollback()
            # 如果处理过程中出错，需要清理已上传的文件
            if os.path.exists(original_path):
                os.remove(original_path)
            if 'thumbnail_path' in locals() and os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
            
            return jsonify({"error": "图片处理失败", "details": str(e)}), 500

    else:
        return jsonify({"error": "不允许的文件类型"}), 400
@image_bp.route('', methods=['GET'])
@jwt_required()
def get_user_images():
    current_user_id = int(get_jwt_identity())
    tag_name = request.args.get('tag', None)
    
    # 1. 初始化基础查询
    query = Image.query.filter_by(user_id=current_user_id)
    
    # 2. 如果 URL 参数中存在 tag, 则在基础查询上追加过滤条件
    if tag_name:
        query = query.filter(Image.tags.any(Tag.name == tag_name))
        
    # 3. 在【最终形成的 query 对象】上应用排序，并执行查询
    #    --- 这是关键的修正点 ---
    images = query.order_by(Image.uploaded_at.desc()).all()
    
    # 4. 构造并返回结果 (这部分代码是正确的)
    base_url = "http://localhost:5000/uploads/"
    result = []
    for img in images:
        result.append({
            'id': img.id,
            'thumbnail_url': base_url + img.thumbnail_path.replace('\\', '/'),
            'original_url': base_url + img.storage_path.replace('\\', '/'),
            'filename': img.original_filename,
            'uploaded_at': img.uploaded_at.isoformat()
        })
        
    return jsonify(result)

# --- 新增：获取单张图片详情的接口 ---
@image_bp.route('/<int:image_id>', methods=['GET'])
@jwt_required()
def get_image_details(image_id):
    current_user_id = int(get_jwt_identity())
    image = Image.query.filter_by(id=image_id, user_id=current_user_id).first_or_404()
    
    base_url = "http://localhost:5000/uploads/"
    
    return jsonify({
        'id': image.id,
        'original_url': base_url + image.storage_path.replace('\\', '/'),
        'filename': image.original_filename,
        'uploaded_at': image.uploaded_at.isoformat(),
        'resolution': image.resolution,
        'size': image.size,
        'exif_data': image.exif_data,
        'tags': [{'id': tag.id, 'name': tag.name} for tag in image.tags]
    })

# --- 新增：为图片添加标签的接口 ---
@image_bp.route('/<int:image_id>/tags', methods=['POST'])
@jwt_required()
def add_tag_to_image(image_id):
    current_user_id = int(get_jwt_identity())
    image = Image.query.filter_by(id=image_id, user_id=current_user_id).first_or_404()
    
    data = request.get_json()
    tag_name = data.get('name')
    if not tag_name:
        return jsonify({'error': '标签名不能为空'}), 400
        
    # 查找或创建标签
    tag = Tag.query.filter_by(name=tag_name).first()
    if not tag:
        tag = Tag(name=tag_name)
        db.session.add(tag)
    
    # 检查图片是否已经有关联此标签
    if tag not in image.tags:
        image.tags.append(tag)
        db.session.commit()
    
    return jsonify({'id': tag.id, 'name': tag.name}), 201

# --- 新增：移除图片标签的接口 ---
@image_bp.route('/<int:image_id>/tags/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def remove_tag_from_image(image_id, tag_id):
    current_user_id = int(get_jwt_identity())
    image = Image.query.filter_by(id=image_id, user_id=current_user_id).first_or_404()
    tag = Tag.query.get_or_404(tag_id)
    
    if tag in image.tags:
        image.tags.remove(tag)
        db.session.commit()
        
    return jsonify({'message': '标签已移除'}), 200