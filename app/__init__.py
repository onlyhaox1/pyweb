from flask import Flask, request, g
from config.config import Config
from app.model.models import db, login_manager, User
from app.controller.auth import auth_bp
from app.controller.index import index_bp
from app.controller.user import user_bp
from app.controller.role import role_bp
from app.controller.menu import menu_bp
from app.middleware.permissions import get_user_menus
import os


def create_app(config_class=Config):
    app = Flask(__name__, 
                template_folder=os.path.join(os.getcwd(), 'app', 'view'),
                static_folder=os.path.join(os.getcwd(), 'public', 'static'))
    
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    
    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(index_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(menu_bp)
    
    # 用户加载回调
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # 上下文处理器：注入菜单到所有模板
    @app.context_processor
    def inject_menus():
        menus = []
        if hasattr(g, 'user') and g.user.is_authenticated:
            menus = get_user_menus()
        return dict(current_menus=menus)
    
    # 错误处理
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # 创建数据库表和初始化数据
    with app.app_context():
        db.create_all()
        init_database()
    
    return app


def init_database():
    """初始化数据库：创建默认角色、菜单和管理员账户"""
    from app.model.models import Role, Menu, RoleMenu, User
    
    # 检查是否已初始化
    if Role.query.first():
        return
    
    # 创建角色
    admin_role = Role(name='admin', description='超级管理员，拥有所有权限')
    manager_role = Role(name='manager', description='普通管理员，拥有系统管理权限')
    user_role = Role(name='user', description='普通用户，仅基础权限')
    
    db.session.add_all([admin_role, manager_role, user_role])
    db.session.commit()
    
    # 创建菜单
    menus = [
        Menu(name='dashboard', title='仪表盘', url='/dashboard', icon='fa-tachometer-alt', sort_order=1),
        Menu(name='profile', title='个人中心', url='/profile', icon='fa-user', sort_order=2),
    ]
    db.session.add_all(menus)
    db.session.commit()
    
    # 系统管理菜单（需要先提交获取 ID）
    system_menu = Menu(name='system', title='系统管理', url='#', icon='fa-cogs', sort_order=10)
    db.session.add(system_menu)
    db.session.commit()
    
    # 子菜单
    sub_menus = [
        Menu(name='user_management', title='用户管理', url='/user/', parent_id=system_menu.id, icon='fa-users', sort_order=1),
        Menu(name='role_management', title='角色管理', url='/role/', parent_id=system_menu.id, icon='fa-user-tag', sort_order=2),
        Menu(name='menu_management', title='菜单管理', url='/menu/', parent_id=system_menu.id, icon='fa-bars', sort_order=3),
    ]
    db.session.add_all(sub_menus)
    db.session.commit()
    
    # 为 admin 角色分配所有菜单
    all_menus = Menu.query.all()
    admin_role.menus = all_menus
    
    # 为 manager 角色分配部分菜单
    manager_menus = Menu.query.filter(
        Menu.name.in_(['dashboard', 'profile', 'system', 'user_management'])
    ).all()
    manager_role.menus = manager_menus
    
    # 为 user 角色分配基础菜单
    user_menus = Menu.query.filter(
        Menu.name.in_(['dashboard', 'profile'])
    ).all()
    user_role.menus = user_menus
    
    db.session.commit()
    
    # 创建默认管理员账户
    admin_user = User(username='admin', email='admin@example.com', role_id=admin_role.id)
    admin_user.set_password('admin123')
    
    manager_user = User(username='manager', email='manager@example.com', role_id=manager_role.id)
    manager_user.set_password('admin123')
    
    test_user = User(username='user', email='user@example.com', role_id=user_role.id)
    test_user.set_password('admin123')
    
    db.session.add_all([admin_user, manager_user, test_user])
    db.session.commit()
    
    print("数据库初始化完成！")
    print("默认账户:")
    print("  admin/admin123 (超级管理员)")
    print("  manager/admin123 (普通管理员)")
    print("  user/admin123 (普通用户)")


# 导入 render_template 用于错误处理
from flask import render_template
