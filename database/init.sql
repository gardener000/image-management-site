-- ============================================
-- 图片管理网站 - 数据库初始化脚本
-- 数据库: MySQL 8.0+
-- ============================================

-- 1. 创建数据库
CREATE DATABASE IF NOT EXISTS image_db 
  DEFAULT CHARACTER SET utf8mb4 
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE image_db;

-- 2. 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. 创建标签表
CREATE TABLE IF NOT EXISTS tags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. 创建图片表
CREATE TABLE IF NOT EXISTS images (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    storage_path VARCHAR(500) NOT NULL,
    thumbnail_path VARCHAR(500),
    mime_type VARCHAR(50),
    size INT,
    resolution VARCHAR(20),
    exif_data JSON,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_uploaded_at (uploaded_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. 创建图片-标签关联表（多对多）
CREATE TABLE IF NOT EXISTS image_tags (
    image_id INT NOT NULL,
    tag_id INT NOT NULL,
    PRIMARY KEY (image_id, tag_id),
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. 创建 Flask-Migrate 版本表（如果需要）
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    PRIMARY KEY (version_num)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 可选：插入测试数据
-- ============================================

-- 插入测试用户 (密码: 123456)
-- 注意：此密码哈希由 werkzeug 生成，实际使用时通过注册功能创建用户
-- INSERT INTO users (username, email, password_hash) VALUES 
-- ('testuser', 'test@example.com', 'scrypt:32768:8:1$...');

-- ============================================
-- 数据库表说明
-- ============================================
-- users: 存储用户信息，密码使用 scrypt 哈希加密
-- tags: 存储标签（自动生成：日期、地点、AI识别内容）
-- images: 存储图片元数据和 EXIF 信息
-- image_tags: 图片与标签的多对多关联
