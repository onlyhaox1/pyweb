from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.model.models import db, User, Role, Menu
from app.middleware.permissions import role_required, menu_permission_required, get_user_menus

index_bp = Blueprint('index', __name__)


@index_bp.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('index.dashboard'))
    return render_template('index/home.html')


@index_bp.route('/dashboard')
@login_required
def dashboard():
    menus = get_user_menus()
    return render_template('index/dashboard.html', menus=menus)


@index_bp.route('/profile')
@login_required
def profile():
    menus = get_user_menus()
    return render_template('index/profile.html', menus=menus)
