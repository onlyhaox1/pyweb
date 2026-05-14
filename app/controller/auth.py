from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.model.models import db, User, Role, Menu

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('账户已被禁用', 'error')
                return render_template('auth/login.html')
            
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash(f'欢迎回来，{user.username}！', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index.dashboard'))
        else:
            flash('用户名或密码错误', 'error')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已退出登录', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'error')
            return render_template('auth/register.html')
        
        # 检查邮箱是否已存在
        if email and User.query.filter_by(email=email).first():
            flash('邮箱已被注册', 'error')
            return render_template('auth/register.html')
        
        # 获取默认用户角色
        default_role = Role.query.filter_by(name='user').first()
        if not default_role:
            flash('系统角色配置错误', 'error')
            return render_template('auth/register.html')
        
        # 创建新用户
        user = User(username=username, email=email, role_id=default_role.id)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('注册成功，请登录', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'注册失败：{str(e)}', 'error')
    
    return render_template('auth/register.html')
