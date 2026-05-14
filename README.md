# ThinkPHP 风格 Web 服务

基于 ThinkPHP 目录结构构建的轻量级 Web 服务，使用 SQLite 数据库，支持多角色菜单权限管理。

## 目录结构

```
/workspace
├── app/                    # 应用目录
│   ├── common/            # 公共类库
│   │   ├── Application.php # 应用主类
│   │   ├── Route.php      # 路由类
│   │   └── Auth.php       # 认证授权类
│   ├── controller/        # 控制器目录
│   │   ├── Index.php      # 首页控制器
│   │   ├── Auth.php       # 认证控制器
│   │   ├── User.php       # 用户管理控制器
│   │   ├── Role.php       # 角色管理控制器
│   │   ├── Menu.php       # 菜单管理控制器
│   │   └── Article.php    # 文章管理控制器
│   ├── model/             # 模型目录
│   ├── view/              # 视图目录
│   └── middleware/        # 中间件目录
├── config/                # 配置目录
│   └── config.php         # 主配置文件
├── public/                # 公共目录
│   └── index.php          # 入口文件
├── runtime/               # 运行时目录
│   ├── cache/            # 缓存目录
│   ├── log/              # 日志目录
│   └── database.sqlite   # SQLite 数据库文件（自动创建）
├── route/                 # 路由目录
│   └── routes.php        # 路由配置文件
└── extend/               # 扩展类库目录
```

## 功能特性

1. **ThinkPHP 风格目录结构** - 遵循 ThinkPHP 的经典目录组织方式
2. **SQLite 数据库** - 无需额外配置数据库服务器，开箱即用
3. **多角色管理** - 内置三种角色：
   - 超级管理员 (admin) - 拥有所有权限
   - 普通管理员 (manager) - 拥有部分管理权限
   - 普通用户 (user) - 基础权限
4. **菜单权限控制** - 基于角色的菜单访问控制
5. **自动初始化** - 首次运行自动创建数据库表和默认数据

## 快速开始

### 启动 PHP 内置服务器

```bash
cd /workspace
php -S localhost:8080 -t public
```

### 访问应用

打开浏览器访问：http://localhost:8080

### 默认账户

| 用户名 | 密码 | 角色 | 权限说明 |
|--------|------|------|----------|
| admin | admin123 | 超级管理员 | 所有菜单和功能权限 |
| manager | admin123 | 普通管理员 | 系统管理相关权限 |
| user | admin123 | 普通用户 | 仅能访问首页，无法访问管理页面 |

## 权限说明

- **admin 角色**: 可以访问所有菜单和页面
- **manager 角色**: 可以访问系统管理、用户管理、角色管理、菜单管理
- **user 角色**: 只能访问首页，尝试访问其他管理页面会返回 403 Forbidden

## 技术实现

- **路由系统**: 简单的 MVC 路由分发
- **认证系统**: 基于 Session 的用户认证
- **权限控制**: 基于角色的访问控制 (RBAC)
- **数据库**: SQLite3 + PDO
- **自动加载**: PSR-4 风格的类自动加载

## 数据库表结构

- `tp_users` - 用户表
- `tp_roles` - 角色表
- `tp_menus` - 菜单表
- `tp_role_menus` - 角色菜单关联表

## 扩展开发

### 添加新控制器

在 `app/controller/` 目录下创建新的控制器类：

```php
<?php
namespace app\controller;

class NewController
{
    public function index()
    {
        return "Hello World";
    }
}
```

### 添加新路由

在 `app/common/Route.php` 的构造函数中注册新路由：

```php
$this->get(/new, New@index);
```

### 添加新菜单

直接在数据库中插入菜单记录，或通过代码管理。
