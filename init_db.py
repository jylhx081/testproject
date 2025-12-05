"""
MySQL 数据库初始化脚本
使用前请先在MySQL中创建数据库
"""
from app import app, db, User
from werkzeug.security import generate_password_hash


def init_database():
    """初始化数据库并创建默认管理员账号"""
    print("开始初始化数据库...")

    with app.app_context():
        # 删除所有表（谨慎使用）
        # db.drop_all()

        # 创建所有表
        db.create_all()
        print("✅ 数据库表创建成功")

        # 检查是否已存在管理员
        admin = User.query.filter_by(username='admin').first()

        if not admin:
            # 创建默认管理员账号
            admin = User(
                username='admin',
                password_hash=generate_password_hash(
                    'admin123'),  # 默认密码: admin123
                email='2934221302@qq.com',
                is_admin=True,
                is_active=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ 默认管理员账号创建成功")
            print("   用户名: admin")
            print("   密码: admin123")
            print("   ⚠️ 请登录后立即修改密码！")
        else:
            print("ℹ️ 管理员账号已存在")

    print("🎉 数据库初始化完成！")


if __name__ == '__main__':
    init_database()
