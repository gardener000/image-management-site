# models.py
# from app import db # 从 app.py 导入我们创建的 db 实例
from extensions import db
from datetime import datetime
from passlib.hash import pbkdf2_sha256 as sha256
from werkzeug.security import generate_password_hash, check_password_hash

# 图片和标签的多对多关联表
image_tags = db.Table('image_tags',
    db.Column('image_id', db.Integer, db.ForeignKey('images.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    images = db.relationship('Image', backref='owner', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = sha256.hash(password)

    def check_password(self, password):
        return sha256.verify(password, self.password_hash)

class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    storage_path = db.Column(db.String(512), unique=True, nullable=False)
    thumbnail_path = db.Column(db.String(512), unique=True, nullable=False)
    mime_type = db.Column(db.String(50))
    size = db.Column(db.Integer)
    resolution = db.Column(db.String(20))
    exif_data = db.Column(db.JSON)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    tags = db.relationship('Tag', secondary=image_tags, backref=db.backref('images', lazy='dynamic'))

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)