from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.model.models import db, User, Role, Menu
from app.middleware.permissions import role_required, menu_permission_required, get_user_menus

role_bp = Blueprint('role', __name__, url_prefix='/role')


@role_bp.route('/')
@login_required
@role_required('admin')
def index():
    menus = get_user_menus()
    roles = Role.query.all()
    all_menus = Menu.query.order_by(Menu.sort_order).all()
    return render_template('role/index.html', menus=menus, roles=roles, all_menus=all_menus)


@role_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('admin')
@menu_permission_required('role_management')
def create():
    menus = get_user_menus()
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        menu_ids = request.form.getlist('menus[]')
        
        if Role.query.filter_by(name=name).first():
            flash('角色名称已存在', 'error')
            return render_template('role/create.html', menus=menus)
        
        role = Role(name=name, description=description)
        
        # 关联菜单权限
        if menu_ids:
            role.menus = Menu.query.filter(Menu.id.in_(menu_ids)).all()
        
        try:
            db.session.add(role)
            db.session.commit()
            flash('角色创建成功', 'success')
            return redirect(url_for('role.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败：{str(e)}', 'error')
    
    all_menus = Menu.query.filter_by(parent_id=None).order_by(Menu.sort_order).all()
    return render_template('role/create.html', menus=menus, all_menus=all_menus)


@role_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
@menu_permission_required('role_management')
def edit(id):
    menus = get_user_menus()
    role = Role.query.get_or_404(id)
    
    if request.method == 'POST':
        role.description = request.form.get('description')
        menu_ids = request.form.getlist('menus[]')
        
        # 更新菜单权限
        role.menus = Menu.query.filter(Menu.id.in_(menu_ids)).all() if menu_ids else []
        
        try:
            db.session.commit()
            flash('角色更新成功', 'success')
            return redirect(url_for('role.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'error')
    
    all_menus = Menu.query.order_by(Menu.sort_order).all()
    return render_template('role/edit.html', menus=menus, role=role, all_menus=all_menus)


@role_bp.route('/delete/<int:id>')
@login_required
@role_required('admin')
@menu_permission_required('role_management')
def delete(id):
    role = Role.query.get_or_404(id)
    
    # 检查是否有用户使用该角色
    if role.users.count() > 0:
        flash('该角色下有用户，无法删除', 'error')
        return redirect(url_for('role.index'))
    
    try:
        db.session.delete(role)
        db.session.commit()
        flash('角色删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{str(e)}', 'error')
    
    return redirect(url_for('role.index'))
