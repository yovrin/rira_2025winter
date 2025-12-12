# app/__init__.py
from flask import Flask
from .database import init_db
import pathlib, os
from flask_login import LoginManager
from .database import db  # 既に init_db で初期化している想定


login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message = "ログインしてください。"

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "change-me"


    # Flask が管理する instance フォルダを必ず作成
    os.makedirs(app.instance_path, exist_ok=True)

    # DB は instance 配下に置く（絶対パス）
    db_path = pathlib.Path(app.instance_path) / "app.sqlite"

    # DB 初期化（絶対パスを文字列で渡す）
    init_db(app, str(db_path))
    login_manager.init_app(app)

    # ルート登録
    from .routes import init_routes
    init_routes(app)

    return app

@login_manager.user_loader
def load_user(user_id: str):
    from .database import User
    return db.session.get(User, int(user_id))