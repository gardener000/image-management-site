# backend/routes/image.py
import os
import uuid
import requests
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

# --- GPS 坐标提取辅助函数 ---
def convert_to_degrees(value):
    """将 EXIF GPS 坐标值转换为十进制度数"""
    try:
        d = float(value.values[0].num) / float(value.values[0].den)
        m = float(value.values[1].num) / float(value.values[1].den)
        s = float(value.values[2].num) / float(value.values[2].den)
        return d + (m / 60.0) + (s / 3600.0)
    except:
        return None

def extract_gps_coordinates(tags):
    """从 EXIF 标签中提取 GPS 坐标"""
    lat = None
    lon = None
    
    if 'GPS GPSLatitude' in tags and 'GPS GPSLatitudeRef' in tags:
        lat = convert_to_degrees(tags['GPS GPSLatitude'])
        if lat and str(tags['GPS GPSLatitudeRef']) == 'S':
            lat = -lat
    
    if 'GPS GPSLongitude' in tags and 'GPS GPSLongitudeRef' in tags:
        lon = convert_to_degrees(tags['GPS GPSLongitude'])
        if lon and str(tags['GPS GPSLongitudeRef']) == 'W':
            lon = -lon
    
    if lat and lon:
        return (lat, lon)
    return None

def reverse_geocode_amap(lat, lon, api_key):
    """使用高德地图 API 进行逆地理编码，返回城市名"""
    if not api_key:
        return None
    
    try:
        # 高德API需要 经度,纬度 格式
        url = f"https://restapi.amap.com/v3/geocode/regeo?key={api_key}&location={lon},{lat}&extensions=base"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data.get('status') == '1' and data.get('regeocode'):
            address_component = data['regeocode'].get('addressComponent', {})
            province = address_component.get('province', '')
            city = address_component.get('city', '')
            
            # 直辖市的 city 可能是空列表
            if isinstance(city, list):
                city = ''
            if isinstance(province, list):
                province = ''
            
            # 返回省份或城市作为标签
            if city:
                return city
            elif province:
                return province
        return None
    except Exception as e:
        print(f"逆地理编码失败: {e}")
        return None

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

            # --- 新增：从EXIF中提取GPS地点 ---
            location_tag = None
            gps_coords = extract_gps_coordinates(tags)
            if gps_coords:
                lat, lon = gps_coords
                # 获取高德API Key（从环境变量或配置）
                amap_key = current_app.config.get('AMAP_API_KEY') or os.environ.get('AMAP_API_KEY')
                if amap_key:
                    location_tag = reverse_geocode_amap(lat, lon, amap_key)
                    if location_tag:
                        print(f"GPS坐标 ({lat}, {lon}) -> 地点: {location_tag}")
                else:
                    # 如果没有API Key，至少保存坐标信息到 exif_data
                    exif_data['GPS_Latitude'] = str(lat)
                    exif_data['GPS_Longitude'] = str(lon)
                    print(f"发现GPS坐标 ({lat}, {lon})，但未配置高德API Key，无法逆地理编码")

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
            auto_tags = []
            if date_time_tag:
                auto_tags.append(date_time_tag)
            if location_tag:
                auto_tags.append(location_tag)
            
            for tag_name in auto_tags:
                # 查找标签是否已存在
                tag_obj = Tag.query.filter_by(name=tag_name).first()
                
                # 如果标签不存在，则创建新标签
                if not tag_obj:
                    tag_obj = Tag(name=tag_name)
                    db.session.add(tag_obj)
                    db.session.flush()
                
                # 将图片和标签关联起来
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
@image_bp.route('/', methods=['GET'])
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
    
    # 4. 构造并返回结果 (动态获取主机地址)
    base_url = request.host_url + "uploads/"
    result = []
    for img in images:
        result.append({
            'id': img.id,
            'thumbnail_url': base_url + img.thumbnail_path.replace('\\', '/'),
            'original_url': base_url + img.storage_path.replace('\\', '/'),
            'filename': img.original_filename,
            'uploaded_at': img.uploaded_at.isoformat(),
            'tags': [{'id': tag.id, 'name': tag.name} for tag in img.tags]
        })
        
    return jsonify(result)

# --- 新增：获取单张图片详情的接口 ---
@image_bp.route('/<int:image_id>', methods=['GET'])
@jwt_required()
def get_image_details(image_id):
    current_user_id = int(get_jwt_identity())
    image = Image.query.filter_by(id=image_id, user_id=current_user_id).first_or_404()
    
    base_url = request.host_url + "uploads/"
    
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

# --- 新增：删除图片的接口 ---
@image_bp.route('/<int:image_id>', methods=['DELETE'])
@jwt_required()
def delete_image(image_id):
    current_user_id = int(get_jwt_identity())
    image = Image.query.filter_by(id=image_id, user_id=current_user_id).first_or_404()
    
    # 构造文件的绝对路径
    upload_folder = current_app.config['UPLOAD_FOLDER']
    original_path = os.path.join(upload_folder, image.storage_path)
    thumbnail_path = os.path.join(upload_folder, image.thumbnail_path)
    
    try:
        # 1. 从数据库删除记录
        db.session.delete(image)
        
        # 2. 从文件系统删除文件
        if os.path.exists(original_path):
            os.remove(original_path)
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
            
        db.session.commit()
        
        return jsonify({'message': '图片已成功删除'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '删除失败', 'details': str(e)}), 500

# --- 编辑图片的接口（支持裁剪和色调调整） ---
@image_bp.route('/<int:image_id>/edit', methods=['POST'])
@jwt_required()
def edit_image(image_id):
    from PIL import ImageEnhance
    
    current_user_id = int(get_jwt_identity())
    image = Image.query.filter_by(id=image_id, user_id=current_user_id).first_or_404()
    
    data = request.get_json()
    if not data:
        return jsonify({'error': '缺少编辑参数'}), 400
    
    # 获取可选的编辑参数
    crop_params = data.get('crop')
    color_params = data.get('color_adjust')
    
    if not crop_params and not color_params:
        return jsonify({'error': '需要提供 crop 或 color_adjust 参数'}), 400

    upload_folder = current_app.config['UPLOAD_FOLDER']
    original_path = os.path.join(upload_folder, image.storage_path)
    
    try:
        with PILImage.open(original_path) as img:
            # 确保图像模式兼容 ImageEnhance
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            processed_img = img.copy()
            new_width, new_height = img.size
            
            # 1. 执行裁剪（如果有裁剪参数）
            if crop_params:
                x = int(crop_params.get('x'))
                y = int(crop_params.get('y'))
                width = int(crop_params.get('width'))
                height = int(crop_params.get('height'))
                processed_img = processed_img.crop((x, y, x + width, y + height))
                new_width, new_height = width, height
            
            # 2. 执行色调调整（如果有色调参数）
            if color_params:
                # 亮度调整: 前端传 -100 到 100，转换为 0 到 2 的增强因子
                brightness = color_params.get('brightness', 0)
                if brightness != 0:
                    factor = 1 + (brightness / 100)
                    enhancer = ImageEnhance.Brightness(processed_img)
                    processed_img = enhancer.enhance(factor)
                
                # 对比度调整: 前端传 -100 到 100，转换为 0 到 2 的增强因子
                contrast = color_params.get('contrast', 0)
                if contrast != 0:
                    factor = 1 + (contrast / 100)
                    enhancer = ImageEnhance.Contrast(processed_img)
                    processed_img = enhancer.enhance(factor)
                
                # 饱和度调整: 前端传 -100 到 100，转换为 0 到 2 的增强因子
                saturation = color_params.get('saturation', 0)
                if saturation != 0:
                    factor = 1 + (saturation / 100)
                    enhancer = ImageEnhance.Color(processed_img)
                    processed_img = enhancer.enhance(factor)
            
            # 3. 保存处理后的图片
            processed_img.save(original_path)
            
            # 4. 重新生成缩略图
            thumbnail_path = os.path.join(upload_folder, image.thumbnail_path)
            thumb_img = processed_img.copy()
            thumb_img.thumbnail((400, 400))
            thumb_img.save(thumbnail_path)
            
            # 5. 更新数据库中的图片信息
            image.resolution = f"{new_width}x{new_height}"
            image.size = os.path.getsize(original_path)
            
            db.session.commit()
            
            # 构造新的URL返回给前端
            base_url = request.host_url + "uploads/"
            return jsonify({
                'message': '图片编辑成功',
                'new_urls': {
                    'original_url': base_url + image.storage_path.replace('\\', '/') + f'?v={uuid.uuid4()}',
                    'thumbnail_url': base_url + image.thumbnail_path.replace('\\', '/') + f'?v={uuid.uuid4()}'
                }
            })
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '编辑失败', 'details': str(e)}), 500