from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.model.models import db, User, Role, Menu
from app.middleware.permissions import role_required, menu_permission_required, get_user_menus

menu_bp = Blueprint('menu', __name__, url_prefix='/menu')


@menu_bp.route('/')
@login_required
@role_required('admin')
def index():
    menus = get_user_menus()
    all_menus = Menu.query.order_by(Menu.parent_id, Menu.sort_order).all()
    return render_template('menu/index.html', menus=menus, all_menus=all_menus)


@menu_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('admin')
@menu_permission_required('menu_management')
def create():
    menus = get_user_menus()
    
    if request.method == 'POST':
        name = request.form.get('name')
        title = request.form.get('title')
        url = request.form.get('url')
        parent_id = request.form.get('parent_id')
        icon = request.form.get('icon', 'fa-circle')
        sort_order = int(request.form.get('sort_order', 0))
        
        if Menu.query.filter_by(name=name).first():
            flash('菜单标识已存在', 'error')
            return render_template('menu/create.html', menus=menus)
        
        menu = Menu(
            name=name,
            title=title,
            url=url,
            parent_id=int(parent_id) if parent_id else None,
            icon=icon,
            sort_order=sort_order
        )
        
        try:
            db.session.add(menu)
            db.session.commit()
            flash('菜单创建成功', 'success')
            return redirect(url_for('menu.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败：{str(e)}', 'error')
    
    parent_menus = Menu.query.filter_by(parent_id=None).order_by(Menu.sort_order).all()
    return render_template('menu/create.html', menus=menus, parent_menus=parent_menus)


@menu_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
@menu_permission_required('menu_management')
def edit(id):
    menus = get_user_menus()
    menu = Menu.query.get_or_404(id)
    
    if request.method == 'POST':
        menu.title = request.form.get('title')
        menu.url = request.form.get('url')
        menu.icon = request.form.get('icon', 'fa-circle')
        menu.sort_order = int(request.form.get('sort_order', 0))
        menu.is_visible = bool(request.form.get('is_visible'))
        
        parent_id = request.form.get('parent_id')
        menu.parent_id = int(parent_id) if parent_id and int(parent_id) != menu.id else None
        
        try:
            db.session.commit()
            flash('菜单更新成功', 'success')
            return redirect(url_for('menu.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'error')
    
    parent_menus = Menu.query.filter_by(parent_id=None).order_by(Menu.sort_order).all()
    return render_template('menu/edit.html', menus=menus, menu=menu, parent_menus=parent_menus)


@menu_bp.route('/delete/<int:id>')
@login_required
@role_required('admin')
@menu_permission_required('menu_management')
def delete(id):
    menu = Menu.query.get_or_404(id)
    
    # 检查是否有子菜单
    if menu.children:
        flash('该菜单下有子菜单，无法删除', 'error')
        return redirect(url_for('menu.index'))
    
    try:
        db.session.delete(menu)
        db.session.commit()
        flash('菜单删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{str(e)}', 'error')
    
    return redirect(url_for('menu.index'))
