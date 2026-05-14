from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user

def role_required(*role_names):
    """装饰器：限制访问需要特定角色"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            if current_user.role.name not in role_names:
                flash('您没有权限访问此页面', 'error')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def menu_permission_required(menu_name):
    """装饰器：检查用户是否有特定菜单权限"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            # 超级管理员拥有所有权限
            if current_user.role.name == 'admin':
                return f(*args, **kwargs)
            
            # 检查用户角色是否有该菜单权限
            menu_names = [menu.name for menu in current_user.role.menus]
            if menu_name not in menu_names:
                flash('您没有权限访问此功能', 'error')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_user_menus():
    """获取当前用户可访问的菜单列表"""
    from app.model.models import Menu
    
    if not current_user.is_authenticated:
        return []
    
    # 超级管理员可以看到所有菜单
    if current_user.role.name == 'admin':
        menus = Menu.query.filter_by(parent_id=None, is_visible=True).order_by(Menu.sort_order).all()
    else:
        # 获取用户角色有权访问的顶级菜单
        menus = Menu.query.join(current_user.role.menus).filter(
            Menu.parent_id == None,
            Menu.is_visible == True
        ).order_by(Menu.sort_order).all()
    
    return menus


def can_access_menu(menu_name):
    """检查当前用户是否可以访问指定菜单"""
    if not current_user.is_authenticated:
        return False
    
    if current_user.role.name == 'admin':
        return True
    
    menu_names = [menu.name for menu in current_user.role.menus]
    return menu_name in menu_names
