from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.model.models import db, User, Role, Menu
from app.middleware.permissions import role_required, menu_permission_required, get_user_menus

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/')
@login_required
@role_required('admin', 'manager')
def index():
    menus = get_user_menus()
    users = User.query.all()
    roles = Role.query.all()
    return render_template('user/index.html', menus=menus, users=users, roles=roles)


@user_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'manager')
@menu_permission_required('user_management')
def create():
    menus = get_user_menus()
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        role_id = request.form.get('role_id')
        
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'error')
            return render_template('user/create.html', menus=menus)
        
        user = User(username=username, email=email, role_id=int(role_id))
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('用户创建成功', 'success')
            return redirect(url_for('user.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败：{str(e)}', 'error')
    
    roles = Role.query.all()
    return render_template('user/create.html', menus=menus, roles=roles)


@user_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'manager')
@menu_permission_required('user_management')
def edit(id):
    menus = get_user_menus()
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        user.email = request.form.get('email')
        user.role_id = int(request.form.get('role_id'))
        user.is_active = bool(request.form.get('is_active'))
        
        password = request.form.get('password')
        if password:
            user.set_password(password)
        
        try:
            db.session.commit()
            flash('用户更新成功', 'success')
            return redirect(url_for('user.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'error')
    
    roles = Role.query.all()
    return render_template('user/edit.html', menus=menus, user=user, roles=roles)


@user_bp.route('/delete/<int:id>')
@login_required
@role_required('admin')
@menu_permission_required('user_management')
def delete(id):
    user = User.query.get_or_404(id)
    
    if user.id == current_user.id:
        flash('不能删除自己', 'error')
        return redirect(url_for('user.index'))
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash('用户删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{str(e)}', 'error')
    
    return redirect(url_for('user.index'))
