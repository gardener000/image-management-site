# 图片管理网站 - Docker 部署指南

## 快速启动

### 1. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件修改密码等配置（可选）
```

### 2. 启动所有服务
```bash
docker-compose up -d --build
```

### 3. 初始化数据库
首次运行需要创建数据库表：
```bash
docker exec -it imagesite-backend flask db upgrade
```

### 4. 访问网站
- 前端：http://localhost
- 后端API：http://localhost:5000

## 服务说明

| 服务 | 端口 | 说明 |
|------|------|------|
| frontend | 80 | Vue 前端 (nginx) |
| backend | 5000 | Flask 后端 API |
| db | 3307 | MySQL 数据库 |

## 常用命令

```bash
# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重建并启动
docker-compose up -d --build

# 进入后端容器
docker exec -it imagesite-backend bash

# 查看数据库
docker exec -it imagesite-db mysql -u imageuser -p
```

## 数据持久化

- `mysql_data`: MySQL 数据
- `uploads_data`: 上传的图片文件

## 生产环境建议

1. 修改 `.env` 中的所有密码
2. 配置 HTTPS (在 nginx.conf 中添加 SSL)
3. 定期备份 MySQL 数据和上传文件
