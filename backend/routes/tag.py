# backend/routes/tag.py
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from models import Tag

tag_bp = Blueprint('tag', __name__)

@tag_bp.route('', methods=['GET'])
@jwt_required()
def get_all_tags():
    tags = Tag.query.order_by(Tag.name).all()
    return jsonify([{'id': tag.id, 'name': tag.name} for tag in tags])