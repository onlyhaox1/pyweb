#!/usr/bin/env python3
"""
ThinkPHP Python Web - 启动脚本
基于 Flask 构建的多角色权限管理系统

使用方法:
    python run.py
    
或者使用 Flask 命令:
    flask run --host=0.0.0.0 --port=8080
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 50)
    print("ThinkPHP Python Web Server")
    print("=" * 50)
    print("启动服务器...")
    print("访问地址：http://localhost:8080")
    print("")
    print("默认账户:")
    print("  admin/admin123   (超级管理员)")
    print("  manager/admin123 (普通管理员)")
    print("  user/admin123    (普通用户)")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=8080, debug=True)
