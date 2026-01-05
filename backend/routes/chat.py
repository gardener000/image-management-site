# backend/routes/chat.py
"""
智能搜索 API - 允许用户通过自然语言查询图片
"""
import re
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Image, Tag, db
from sqlalchemy import or_

chat_bp = Blueprint('chat', __name__)

def parse_search_intent(query):
    """
    解析用户的自然语言查询意图
    返回: {'type': 'tag'|'date'|'location'|'all', 'keywords': [...]}
    """
    query = query.lower().strip()
    
    # 时间相关关键词
    date_patterns = [
        r'(\d{4})年(\d{1,2})月',  # 2024年10月
        r'(\d{4})年',              # 2024年
        r'去年|今年|上个月|这个月',
        r'最近|最新'
    ]
    
    # 地点相关关键词
    location_keywords = ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '南京', 
                         '西安', '重庆', '天津', '苏州', '拍摄', '地点', '在哪', '宁波', '哪里']
    
    # 内容相关关键词
    content_keywords = ['风景', '人物', '动物', '食物', '建筑', '植物', '天空', '海洋',
                        '山', '树', '花', '猫', '狗', '鸟', '汽车', '美食', '夜景',
                        '日落', '日出', '城市', '自然', '旅行', '家人', '朋友']
    
    intent = {'type': 'all', 'keywords': [], 'original': query}
    
    # 检查时间模式
    for pattern in date_patterns:
        match = re.search(pattern, query)
        if match:
            intent['type'] = 'date'
            intent['keywords'].append(match.group())
            break
    
    # 检查地点关键词
    for loc in location_keywords:
        if loc in query:
            intent['type'] = 'location'
            intent['keywords'].append(loc)
    
    # 检查内容关键词
    for content in content_keywords:
        if content in query:
            if intent['type'] == 'all':
                intent['type'] = 'content'
            intent['keywords'].append(content)
    
    # 如果没有匹配到特定类型，提取所有可能的关键词
    if not intent['keywords']:
        # 简单分词
        words = re.findall(r'[\u4e00-\u9fa5]+|\w+', query)
        intent['keywords'] = [w for w in words if len(w) > 1]
    
    return intent

def search_images_by_intent(user_id, intent):
    """根据解析的意图搜索图片"""
    base_url = request.host_url + "uploads/"
    results = []
    
    # 基础查询
    query = Image.query.filter_by(user_id=user_id)
    
    if intent['keywords']:
        # 通过标签搜索
        for keyword in intent['keywords']:
            tag_matches = Tag.query.filter(Tag.name.like(f'%{keyword}%')).all()
            for tag in tag_matches:
                for img in tag.images:
                    if img.user_id == user_id and img.id not in [r['id'] for r in results]:
                        results.append({
                            'id': img.id,
                            'thumbnail_url': base_url + img.thumbnail_path.replace('\\', '/'),
                            'original_url': base_url + img.storage_path.replace('\\', '/'),
                            'filename': img.original_filename,
                            'tags': [{'id': t.id, 'name': t.name} for t in img.tags],
                            'match_reason': f'匹配标签: {tag.name}'
                        })
    
    # 如果没有通过标签找到，返回最近的图片
    if not results:
        images = query.order_by(Image.uploaded_at.desc()).limit(10).all()
        for img in images:
            results.append({
                'id': img.id,
                'thumbnail_url': base_url + img.thumbnail_path.replace('\\', '/'),
                'original_url': base_url + img.storage_path.replace('\\', '/'),
                'filename': img.original_filename,
                'tags': [{'id': t.id, 'name': t.name} for t in img.tags],
                'match_reason': '最近上传'
            })
    
    return results

def generate_response(intent, results):
    """生成自然语言回复"""
    count = len(results)
    
    if count == 0:
        return f"抱歉，没有找到与「{intent['original']}」相关的图片。试试其他关键词？"
    
    keywords_str = '、'.join(intent['keywords'][:3]) if intent['keywords'] else intent['original']
    
    if intent['type'] == 'date':
        return f"为您找到 {count} 张「{keywords_str}」的照片。"
    elif intent['type'] == 'location':
        return f"为您找到 {count} 张在「{keywords_str}」拍摄的照片。"
    elif intent['type'] == 'content':
        return f"为您找到 {count} 张包含「{keywords_str}」的照片。"
    else:
        return f"为您找到 {count} 张相关照片。"

@chat_bp.route('/search', methods=['POST'])
@jwt_required()
def smart_search():
    """
    智能搜索接口
    请求: {"query": "帮我找风景照片"}
    响应: {"message": "为您找到5张...", "images": [...]}
    """
    current_user_id = int(get_jwt_identity())
    
    data = request.get_json()
    if not data or not data.get('query'):
        return jsonify({'error': '请输入搜索内容'}), 400
    
    query = data['query']
    
    # 解析搜索意图
    intent = parse_search_intent(query)
    
    # 搜索图片
    results = search_images_by_intent(current_user_id, intent)
    
    # 生成回复
    message = generate_response(intent, results)
    
    return jsonify({
        'message': message,
        'images': results[:20],  # 最多返回20张
        'intent': intent
    })

@chat_bp.route('/suggestions', methods=['GET'])
@jwt_required()
def get_suggestions():
    """获取搜索建议"""
    current_user_id = int(get_jwt_identity())
    
    # 获取用户的所有标签
    images = Image.query.filter_by(user_id=current_user_id).all()
    tags = set()
    for img in images:
        for tag in img.tags:
            tags.add(tag.name)
    
    suggestions = [
        "帮我找风景照片",
        "显示最近上传的图片",
        "找有动物的照片",
        "显示建筑相关的图片"
    ]
    
    # 添加基于用户标签的建议
    for tag in list(tags)[:5]:
        suggestions.append(f"找「{tag}」相关的照片")
    
    return jsonify({'suggestions': suggestions})
