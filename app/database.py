# app/database.py
import pathlib
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin      # ← 復活
import logging

log = logging.getLogger(__name__)

USER_GENERAL = '00'
USER_ADMIN = '99'
db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String, nullable=False)
    passwd = db.Column(db.String, nullable=False)
    utype = db.Column(db.String, nullable=False, default=USER_GENERAL)
    update_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __init__(self, uname, passwd, utype=USER_GENERAL):
        self.uname = uname
        self.passwd = passwd
        self.utype = utype
    # 追加↓↓
    def verify_password(self, raw: str) -> bool:
        return self.passwd == raw

class ClassT(db.Model):
    __tablename__ = 'class_t'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kamokumei = db.Column(db.String, nullable=False)  # 科目名
    tantou_k  = db.Column(db.String)                  # 担当教員
    tani      = db.Column(db.String)                  # 単位数
    k_kbn     = db.Column(db.String)                  # 科目区分
    k_bunrui  = db.Column(db.String)                  # 科目分類
    k_bunya   = db.Column(db.String)                  # 学問分野
    j_houhou  = db.Column(db.String)                  # 授業の方法
    k_zokusei = db.Column(db.String)                  # 科目属性
    nenji     = db.Column(db.String)                  # 履修想定年次
    kaikou_k  = db.Column(db.String)                  # 開講期
    k_number  = db.Column(db.String)                  # ナンバリング
    # is_acquired = db.Column(db.String, server_default="0") # 単位取得済み

class UserClass(db.Model):
    """
    ユーザーごとの科目状態を保持する中間テーブル
    """
    __tablename__ = 'user_classes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id  = db.Column(db.String, nullable=False)
    kamokumei = db.Column(db.String, nullable=False)
    is_acquired = db.Column(db.String, nullable=False, default="0")   # 互換のため維持したいならこれで

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    #ユニークキー
    __table_args__ = (
        db.UniqueConstraint('user_id', 'kamokumei', name='uq_user_kamokumei'),
    )

def init_db(app, db_path: str):
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True

    db.init_app(app)

    # DB ファイルが無くても、親ディレクトリは作成済み
    with app.app_context():
        db.create_all()   # ← 存在しないテーブルは作成される
