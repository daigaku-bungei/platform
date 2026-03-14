from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # 設定
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-12345')
    db_url = os.environ.get('DATABASE_URL', 'sqlite://')
    if db_url and db_url.startswith("postgres://") and not db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    with app.app_context():
        # ★すべてのモデルをインポート（順序重要）
        from app.models.user import User
        from app.models.novel import Novel
        from app.models.comment import Comment
        from app.models.like import Like

        # 機能（Blueprint）の読み込み
        from app.routes.main import main_bp
        from app.routes.auth import auth_bp
        from app.routes.novels import novels_bp
        from app.routes.users import users_bp
        from app.routes.comments import comments_bp

        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(novels_bp, url_prefix='/novels')
        app.register_blueprint(users_bp, url_prefix='/users')
        app.register_blueprint(comments_bp, url_prefix='/comments')

        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    return app
