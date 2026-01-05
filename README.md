# 图片管理网站 (Image Management Site)

## 项目简介
一个基于 Vue 3 + Flask 的图片管理网站，支持图片上传、自动标签、智能搜索等功能。

## 技术栈
- **前端**: Vue 3, Vite, Element Plus
- **后端**: Flask, Flask-SQLAlchemy, Flask-JWT-Extended
- **数据库**: MySQL 8.0
- **外部API**: 高德地图（GPS逆地理编码）、百度AI（图片内容识别）

## 功能特性
- 用户注册/登录（JWT认证）
- 图片上传与管理
- 自动提取EXIF信息（时间、GPS、分辨率）
- GPS自动转换为地点名称
- AI自动识别图片内容生成标签
- 标签搜索与筛选
- 智能自然语言搜索
- 图片轮播展示
- 深色主题界面

## 目录结构
```
image-management-site/
├── backend/                 # Flask 后端
│   ├── routes/             # API 路由
│   ├── models.py           # 数据模型
│   ├── config.py           # 配置文件
│   ├── app.py              # 应用入口
│   ├── Dockerfile          # Docker配置
│   └── requirements.txt    # Python依赖
├── frontend/               # Vue 前端
│   └── vue-project/
│       ├── src/
│       │   ├── views/      # 页面组件
│       │   ├── components/ # 通用组件
│       │   └── api/        # API客户端
│       ├── Dockerfile      # Docker配置
│       └── nginx.conf      # Nginx配置
├── database/               # 数据库脚本
│   └── init.sql           # 建库建表SQL
├── docker-compose.yml      # Docker编排
└── README.md
```

## 快速开始

### 1. 数据库配置
```bash
# 执行建库建表脚本
mysql -u root -p < database/init.sql
```

### 2. 后端启动
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 3. 前端启动
```bash
cd frontend/vue-project
npm install
npm run dev
```

### 4. 访问网站
- 前端: http://localhost:5173
- 后端API: http://localhost:5000

## Docker 部署
```bash
cp .env.example .env
docker-compose up -d --build
docker exec -it imagesite-backend flask db upgrade
```

## Git Log
使用以下命令查看完整的 Git 提交历史：
```bash
git log --oneline --graph --all
git log --pretty=format:"%h - %an, %ar : %s"
```

这里给出完整运行结果:

```bash
* a1f860b (HEAD -> main, origin/main) feat(backend):add Baidu API to analyse the uploaded images' content.
* 9f8f4b1 add GPS tag to homa page images.
* f2b83b5 feat(error fix):fix the overlap between the Element Plus imformation and the title * a1f860b (HEAD -> main, origin/main) feat(backend):add Baidu API to analyse the uploaded images' content.
* 9f8f4b1 add GPS tag to homa page images.
* f2b83b5 feat(error fix):fix the overlap between the Element Plus imformation and the title bar
* 8ba9bde feat(backend):add the AMAP api key to analyse the GPS of the uploaded images       
* 072bf62 feat(frontend):unified the style of the gallery and home page.
* 1c33abf feat(frontend):finished the style changing of home page.
* a1f860b (HEAD -> main, origin/main) feat(backend):add Baidu API to analyse the uploaded images' content.
* 9f8f4b1 add GPS tag to homa page images.
* f2b83b5 feat(error fix):fix the overlap between the Element Plus imformation and the title bar
* 8ba9bde feat(backend):add the AMAP api key to analyse the GPS of the uploaded images       
* 072bf62 feat(frontend):unified the style of the gallery and home page.
* 1c33abf feat(frontend):finished the style changing of home page.
* 4e35b2c feat(frontend):iprove the image carousel function and fix it into the face page    
* f724532 feat(frontend):initial the image carousel function
* 1188905 feat(frontend):fix the style issue on the mobile version of the website
* a1f860b (HEAD -> main, origin/main) feat(backend):add Baidu API to analyse the uploaded images' content.
* 9f8f4b1 add GPS tag to homa page images.
* f2b83b5 feat(error fix):fix the overlap between the Element Plus imformation and the title bar
* 8ba9bde feat(backend):add the AMAP api key to analyse the GPS of the uploaded images       
* 072bf62 feat(frontend):unified the style of the gallery and home page.
* 1c33abf feat(frontend):finished the style changing of home page.
* 4e35b2c feat(frontend):iprove the image carousel function and fix it into the face page    
* f724532 feat(frontend):initial the image carousel function
* 1188905 feat(frontend):fix the style issue on the mobile version of the website
* 939d0da feat(frontend):implement the function of color editing
* 5ab0f5c feat(frontend):implement the function of cropping images.
* 7fda595 feat: Implement the frontend components of tags
* 2281433 feat: Implement some backend APIs about tags
* a1f860b (HEAD -> main, origin/main) feat(backend):add Baidu API to analyse the uploaded images' content.
* 9f8f4b1 add GPS tag to homa page images.
* f2b83b5 feat(error fix):fix the overlap between the Element Plus imformation and the title bar
* 8ba9bde feat(backend):add the AMAP api key to analyse the GPS of the uploaded images       
* 072bf62 feat(frontend):unified the style of the gallery and home page.
* 1c33abf feat(frontend):finished the style changing of home page.
* 4e35b2c feat(frontend):iprove the image carousel function and fix it into the face page    
* f724532 feat(frontend):initial the image carousel function
* 1188905 feat(frontend):fix the style issue on the mobile version of the website
* 939d0da feat(frontend):implement the function of color editing
* 5ab0f5c feat(frontend):implement the function of cropping images.
* 7fda595 feat: Implement the frontend components of tags
* 2281433 feat: Implement some backend APIs about tags
* df1b559 feat: Implement the simplest frontend gallery and upload image page
* 1fd6930 feat: Implement the simplest frontend login page
* 724450c feat: Implement the simplest frontend register page
* f99ca88 feat(image): Implement protected image upload endpoint with EXIF parsing
* 4ed2177 feat(image): Implement protected image upload endpoint with thumbnail generation   
* 2af8182 feat(auth): Implement user login API with JWT
:...skipping...
* a1f860b (HEAD -> main, origin/main) feat(backend):add Baidu API to analyse the uploaded images' content.
* 9f8f4b1 add GPS tag to homa page images.
* f2b83b5 feat(error fix):fix the overlap between the Element Plus imformation and the title bar
* 8ba9bde feat(backend):add the AMAP api key to analyse the GPS of the uploaded images       
* 072bf62 feat(frontend):unified the style of the gallery and home page.
* 1c33abf feat(frontend):finished the style changing of home page.
* 4e35b2c feat(frontend):iprove the image carousel function and fix it into the face page    
* f724532 feat(frontend):initial the image carousel function
* 1188905 feat(frontend):fix the style issue on the mobile version of the website
* 939d0da feat(frontend):implement the function of color editing
* 5ab0f5c feat(frontend):implement the function of cropping images.
* 7fda595 feat: Implement the frontend components of tags
* 2281433 feat: Implement some backend APIs about tags
* df1b559 feat: Implement the simplest frontend gallery and upload image page
* 1fd6930 feat: Implement the simplest frontend login page
* 724450c feat: Implement the simplest frontend register page
* f99ca88 feat(image): Implement protected image upload endpoint with EXIF parsing
* 4ed2177 feat(image): Implement protected image upload endpoint with thumbnail generation   
* 2af8182 feat(auth): Implement user login API with JWT
* 11b5099 feat(auth): Implement user registration API endpoint with validation
* 6ab1606 feat: Setup frontend environment with Vue.js and install dependencies
```

## 作者
肖惠文

## 许可证
MIT License
