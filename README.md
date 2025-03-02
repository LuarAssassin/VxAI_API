# Django REST Framework 用户管理 API

这是一个基于Django REST Framework和JWT的用户管理API系统，提供了对自定义用户(CustomUser)的增删改查操作。

## 功能特点

- 基于邮箱的用户认证系统
- JWT令牌认证
- 自定义用户模型
- 完整的用户CRUD API
- 密码修改功能
- 用户头像上传
- 软删除功能
- 统一响应格式
- 自定义权限控制
- 日志记录
- 缓存支持
- 异常处理

## 技术栈

- Python 3.x
- Django 4.x
- Django REST Framework
- Simple JWT

## 项目结构

```
├── core/                  # 项目核心配置
├── users/                 # 用户应用
│   ├── migrations/        # 数据库迁移文件
│   ├── utils/             # 工具类
│   │   ├── cache.py       # 缓存工具
│   │   ├── exceptions.py  # 异常处理
│   │   ├── helpers.py     # 辅助函数
│   │   ├── logger.py      # 日志工具
│   │   ├── pagination.py  # 分页工具
│   │   ├── permissions.py # 权限工具
│   │   ├── response.py    # 响应工具
│   │   ├── serializers.py # 序列化器基类
│   │   └── views.py       # 视图基类
│   ├── admin.py           # 管理员配置
│   ├── models.py          # 数据模型
│   ├── serializers.py     # 序列化器
│   ├── urls.py            # URL配置
│   └── views.py           # 视图
├── logs/                  # 日志文件
├── media/                 # 媒体文件
├── manage.py              # Django管理脚本
└── requirements.txt       # 项目依赖
```

## 安装和运行

1. 克隆项目

```bash
git clone <repository-url>
cd <project-directory>
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

4. 创建超级用户

```bash
python manage.py createsuperuser
```

5. 运行开发服务器

```bash
python manage.py runserver
```

## API 端点

### 认证相关

- `POST /api/users/token/` - 获取JWT令牌
- `POST /api/users/token/refresh/` - 刷新JWT令牌

### 用户相关

- `POST /api/users/` - 用户注册
- `GET /api/users/` - 获取用户列表
- `GET /api/users/me/` - 获取当前用户信息
- `GET /api/users/{id}/` - 获取指定用户详情
- `PUT/PATCH /api/users/{id}/` - 更新用户信息
- `DELETE /api/users/{id}/` - 软删除用户
- `POST /api/users/{id}/restore/` - 恢复已删除的用户
- `DELETE /api/users/{id}/hard_delete/` - 硬删除用户
- `GET /api/users/deleted/` - 获取已删除的用户列表
- `PUT /api/users/change_password/` - 修改密码

## 使用示例

### 用户注册

```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"testuser","password":"securepassword123","password2":"securepassword123"}'
```

### 获取令牌

```bash
curl -X POST http://localhost:8000/api/users/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"securepassword123"}'
```

### 使用令牌访问API

```bash
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer <your-token>"
```

### 软删除用户

```bash
curl -X DELETE http://localhost:8000/api/users/1/ \
  -H "Authorization: Bearer <your-token>"
```

### 恢复已删除的用户

```bash
curl -X POST http://localhost:8000/api/users/1/restore/ \
  -H "Authorization: Bearer <your-token>"
```

## 自定义工具类

### 软删除基类

项目实现了软删除功能，通过以下方式：

1. `SoftDeleteModel` - 软删除模型基类，提供软删除功能
2. `SoftDeleteManager` - 软删除管理器，默认只返回未删除的对象
3. `SoftDeleteViewSet` - 软删除视图集，提供软删除和恢复功能

### 其他工具类

1. `BaseModel` - 基础模型，包含通用字段
2. `TimeStampedModel` - 时间戳模型，包含创建和更新时间
3. `BaseModelSerializer` - 基础模型序列化器
4. `DynamicFieldsModelSerializer` - 动态字段模型序列化器
5. `NestedModelSerializer` - 嵌套模型序列化器
6. `RecursiveSerializer` - 递归序列化器
7. `BaseViewSet` - 基础视图集
8. `CRUDViewSet` - 完整的CRUD视图集
9. `APIResponse` - 自定义API响应类
10. `RequestLogMiddleware` - 请求日志中间件

## 许可证

MIT 