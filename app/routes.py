# app/routes.py
from flask import Blueprint, render_template, Response
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from .database import User
from flask import Blueprint, render_template, request, redirect, url_for, flash
from .database import db, ClassT, User, UserClass
from flask_login import login_user, logout_user, login_required, current_user
from .zunda_core import *


bp = Blueprint("main", __name__)

import re

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form.get("uname", "").strip()
        passwd = request.form.get("passwd", "").strip()

        # 半角英数字のみチェック（a〜z, A〜Z, 0〜9, アンダースコアOKなら _ を追加）
        if not re.match(r'^[0-9A-Za-z]+$', uname):
            flash("ユーザIDは半角英数字のみ利用できます", "danger")
            return render_template("register.html")

        if not uname or not passwd:
            flash("ユーザー名とパスワードは必須です", "danger")
            return render_template("register.html")

        if User.query.filter_by(uname=uname).first():
            flash("このユーザー名はすでに使われています", "danger")
            return render_template("register.html")

        user = User(uname=uname, passwd=passwd)  # 後でハッシュ化推奨
        db.session.add(user)
        db.session.commit()

        flash("ユーザ登録が完了しました。ログインしてください。", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html")


# ログイン
@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form.get("uname", "").strip()
        passwd = request.form.get("passwd", "")
        user = User.query.filter_by(uname=uname).first()
        if user and user.verify_password(passwd):
            login_user(user, remember=True)
            # ★ 初期PWならパスワード変更へ
            if user.passwd == "12345":
                flash("初期パスワードのため、変更してください。", "warning")
                return redirect(url_for("main.change_password"))
            return redirect(url_for("main.index"))
        flash("ユーザー名またはパスワードが違います。", "danger")
    return render_template("login.html")

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))

@bp.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        new_pw = request.form.get("new_password", "")
        new_pw2 = request.form.get("confirm_password", "")

        # バリデーション（必要に応じて強化）
        if not new_pw or not new_pw2:
            flash("入力が不足しています。", "danger")
            return render_template("change_password.html")
        if new_pw != new_pw2:
            flash("確認用パスワードが一致しません。", "danger")
            return render_template("change_password.html")
        if new_pw == "12345":
            flash("初期パスワードと同じにはできません。", "danger")
            return render_template("change_password.html")

        # 更新
        current_user.passwd = new_pw
        db.session.commit()

        # 再ログインを要求（安全策）
        logout_user()
        flash("パスワードを更新しました。新しいパスワードでログインしてください。", "success")
        return redirect(url_for("main.login"))

    return render_template("change_password.html")

#初期画面
@bp.route("/")
@login_required
def index():
    user_id_str = str(current_user.id)
    # ① このユーザーの user_classes を一括取得
    uc_rows = UserClass.query.filter_by(user_id=user_id_str).all()
    # ② {科目名: is_acquired} の辞書にする（"1" or "0"）
    uc_map = {row.kamokumei: row.is_acquired for row in uc_rows}

    # 導入科目
    do_list = (ClassT.query.filter_by(k_kbn="導入科目").order_by(ClassT.id.asc()).all())

    #########基礎
    # 基盤リテラシー科目（情報）
    kiso_kiban_jo_1 = ClassT.query.filter_by(k_kbn="基礎科目", k_bunrui="基盤リテラシー科目", k_bunya="情報",nenji="1年次").order_by(ClassT.id.asc()).all()

    # 基盤リテラシー科目（数理）
    kiso_kiban_su_1 = ClassT.query.filter_by(k_kbn="基礎科目", k_bunrui="基盤リテラシー科目", k_bunya="数理",nenji="1年次").order_by(ClassT.id.asc()).all()

    # 多言語情報理解（多言語）
    kiso_tagengo_1 = ClassT.query.filter_by(k_kbn="基礎科目", k_bunrui="多言語情報理解科目", k_bunya="多言語情報理解",nenji="1年次").order_by(ClassT.id.asc()).all()

    # 世界理解（文化・芸術）
    kiso_sekai_bunka_1 = ClassT.query.filter_by(k_kbn="基礎科目", k_bunrui="世界理解科目", k_bunya="文化・思想",nenji="1年次").order_by(ClassT.id.asc()).all()

    # 世界理解（社会・ネットワーク）
    kiso_sekai_net_1 = ClassT.query.filter_by(k_kbn="基礎科目", k_bunrui="世界理解科目", k_bunya="社会・ネットワーク",nenji="1年次").order_by(ClassT.id.asc()).all()

    # 世界理解（社会・マーケット）
    kiso_sekai_keizai_1 = ClassT.query.filter_by(k_kbn="基礎科目", k_bunrui="世界理解科目", k_bunya="経済・マーケット",nenji="1年次").order_by(ClassT.id.asc()).all()

    #########展開1
    # 展開リテラシー科目（情報）
    tenkai_kiban_jo_1 = ClassT.query.filter_by(k_kbn="展開科目", k_bunrui="基盤リテラシー科目", k_bunya="情報", nenji="1年次").order_by(ClassT.id.asc()).all()

    # 展開リテラシー科目（数理）
    tenkai_kiban_su_1 = ClassT.query.filter_by(k_kbn="展開科目", k_bunrui="基盤リテラシー科目", k_bunya="数理", nenji="1年次").order_by(ClassT.id.asc()).all()

    # 多言語情報理解（多言語）
    tenkai_tagengo_1 = ClassT.query.filter_by(k_kbn="展開科目", k_bunrui="多言語情報理解科目", k_bunya="多言語情報理解",nenji="1年次").order_by(ClassT.id.asc()).all()

    # 世界理解（文化・芸術）
    tenkai_sekai_bunka_1 = ClassT.query.filter_by(k_kbn="展開科目", k_bunrui="世界理解科目", k_bunya="文化・思想",nenji="1年次").order_by(ClassT.id.asc()).all()

    # 世界理解（社会・ネットワーク）
    tenkai_sekai_net_1 = ClassT.query.filter_by(k_kbn="展開科目", k_bunrui="世界理解科目", k_bunya="社会・ネットワーク",nenji="1年次").order_by(ClassT.id.asc()).all()

    # # 世界理解（社会・マーケット）
    # tenkai_sekai_keizai_1 = ClassT.query.filter_by(k_kbn="展開科目", k_bunrui="世界理解科目", k_bunya="社会・ネットワーク",nenji="1年次").order_by(ClassT.id.asc()).all()

    # 世界理解（社会・マーケット）
    tenkai_shakai_keizai_1 = ClassT.query.filter_by(k_kbn="展開科目", k_bunrui="世界理解科目", k_bunya="経済・マーケット", nenji="1年次").order_by(ClassT.id.asc()).all()

    # 世界理解（デジタル産業）
    tenkai_shakai_deji_1 = ClassT.query.filter_by(k_kbn="展開科目", k_bunrui="世界理解科目", k_bunya="デジタル産業", nenji="1年次").order_by(ClassT.id.asc()).all()

    # 社会接続
    kiso_shakai_1 = ClassT.query.filter_by(k_kbn="展開科目", k_bunrui="社会接続科目", k_bunya="社会接続", nenji="1年次").order_by(ClassT.id.asc()).all()

   # 自由
    kiso_jiyu_1 = ClassT.query.filter_by(k_kbn="自由科目", k_bunrui="自由科目", k_bunya="自由科目", nenji="1年次").order_by(ClassT.id.asc()).all()


    #########展開2
    # 展開リテラシー科目（情報）
    tenkai_kiban_jo_2 = ClassT.query.filter_by(k_kbn="展開科目", k_bunrui="基盤リテラシー科目", k_bunya="情報", nenji="2年次").order_by(ClassT.id.asc()).all()

    # 展開リテラシー科目（数理）
    tenkai_kiban_su_2 = ClassT.query.filter_by(k_kbn="展開科目", k_bunrui="基盤リテラシー科目", k_bunya="数理", nenji="2年次").order_by(ClassT.id.asc()).all()

    # 多言語情報理解（多言語）
    tenkai_tagengo_2 = ClassT.query.filter_by(k_kbn="展開科目", k_bunrui="多言語情報理解科目", k_bunya="多言語情報理解",nenji="2年次").order_by(ClassT.id.asc()).all()

    # 世界理解（文化・芸術）
    tenkai_sekai_bunka_2 = ClassT.query.filter_by(k_kbn="展開科目", k_bunrui="世界理解科目", k_bunya="文化・思想",nenji="2年次").order_by(ClassT.id.asc()).all()

    # 世界理解（社会・ネットワーク）
    tenkai_sekai_net_2 = ClassT.query.filter_by(k_kbn="展開科目", k_bunrui="世界理解科目", k_bunya="社会・ネットワーク",nenji="2年次").order_by(ClassT.id.asc()).all()

    # 世界理解（社会・マーケット）
    tenkai_shakai_keizai_2 = ClassT.query.filter_by(k_kbn="展開科目", k_bunrui="世界理解科目", k_bunya="経済・マーケット", nenji="2年次").order_by(ClassT.id.asc()).all()

    # 世界理解（デジタル産業）
    tenkai_shakai_deji_2 = ClassT.query.filter_by(k_kbn="展開科目", k_bunrui="世界理解科目", k_bunya="デジタル産業", nenji="2年次").order_by(ClassT.id.asc()).all()

    # 社会接続
    kiso_shakai_2 = ClassT.query.filter_by(k_kbn="展開科目", k_bunrui="社会接続科目", k_bunya="社会接続", nenji="2年次").order_by(ClassT.id.asc()).all()

   # 自由
    kiso_jiyu_2 = ClassT.query.filter_by(k_kbn="自由科目", k_bunrui="自由科目", k_bunya="自由科目", nenji="2年次").order_by(ClassT.id.asc()).all()

   #########展開3
    # 展開リテラシー科目（情報）
    tenkai_kiban_jo_3 = ClassT.query.filter_by(k_kbn="展開科目", k_bunrui="基盤リテラシー科目", k_bunya="情報", nenji="3年次").order_by(ClassT.id.asc()).all()

    # 展開リテラシー科目（数理）
    tenkai_kiban_su_3 = ClassT.query.filter_by(k_kbn="展開科目", k_bunrui="基盤リテラシー科目", k_bunya="数理", nenji="3年次").order_by(ClassT.id.asc()).all()

    # # 多言語情報理解（多言語）
    # tenkai_tagengo_3 = ClassT.query.filter_by(k_kbn="展開科目", k_bunrui="多言語情報理解科目", k_bunya="多言語情報理解",nenji="3年次").order_by(ClassT.id.asc()).all()

    # 世界理解（文化・芸術）
    tenkai_sekai_bunka_3 = ClassT.query.filter_by(k_kbn="展開科目", k_bunrui="世界理解科目", k_bunya="文化・思想",nenji="3年次").order_by(ClassT.id.asc()).all()

    # 世界理解（社会・ネットワーク）
    tenkai_sekai_net_3 = ClassT.query.filter_by(k_kbn="展開科目", k_bunrui="世界理解科目", k_bunya="社会・ネットワーク",nenji="3年次").order_by(ClassT.id.asc()).all()

    # # 世界理解（社会・マーケット）
    # tenkai_shakai_keizai_3 = ClassT.query.filter_by(k_kbn="展開科目", k_bunrui="世界理解科目", k_bunya="経済・マーケット", nenji="3年次").order_by(ClassT.id.asc()).all()

    # 世界理解（デジタル産業）
    tenkai_shakai_deji_3 = ClassT.query.filter_by(k_kbn="展開科目", k_bunrui="世界理解科目", k_bunya="デジタル産業", nenji="3年次").order_by(ClassT.id.asc()).all()

    # 社会接続
    kiso_shakai_3 = ClassT.query.filter_by(k_kbn="展開科目", k_bunrui="社会接続科目", k_bunya="社会接続", nenji="3年次").order_by(ClassT.id.asc()).all()

   # 自由
    kiso_jiyu_3 = ClassT.query.filter_by(k_kbn="自由科目", k_bunrui="自由科目", k_bunya="自由科目", nenji="3年次").order_by(ClassT.id.asc()).all()

  #########考究
    # 考究(情報)
    kokyu_jo = ClassT.query.filter_by(k_kbn="展開科目（考究）", k_bunrui="基盤リテラシー科目", k_bunya="情報").order_by(ClassT.id.asc()).all()

    # 考究(数理)
    kokyu_su = ClassT.query.filter_by(k_kbn="展開科目（考究）", k_bunrui="基盤リテラシー科目", k_bunya="数理").order_by(ClassT.id.asc()).all()

    # 考究(文化・思想)
    kokyu_bunka = ClassT.query.filter_by(k_kbn="展開科目（考究）", k_bunrui="世界理解科目", k_bunya="文化・思想").order_by(ClassT.id.asc()).all()

    # 考究(社会・ネットワーク)
    kokyu_net = ClassT.query.filter_by(k_kbn="展開科目（考究）", k_bunrui="世界理解科目", k_bunya="社会・ネットワーク").order_by(ClassT.id.asc()).all()

    # 考究(経済・マーケート)
    kokyu_keizai = ClassT.query.filter_by(k_kbn="展開科目（考究）", k_bunrui="世界理解科目", k_bunya="経済・マーケット").order_by(ClassT.id.asc()).all()

    # 考究(デジタル産業)
    kokyu_deji = ClassT.query.filter_by(k_kbn="展開科目（考究）", k_bunrui="世界理解科目", k_bunya="デジタル産業").order_by(ClassT.id.asc()).all()

    # 考究(社会・ネットワーク)
    kokyu_shakai = ClassT.query.filter_by(k_kbn="展開科目（考究）", k_bunrui="社会接続科目", k_bunya="社会接続").order_by(ClassT.id.asc()).all()

   # 考究(社会・ネットワーク)
    pj = ClassT.query.filter_by(k_kbn="展開科目（考究）", k_bunrui="卒業プロジェクト科目", k_bunya="卒業プロジェクト").order_by(ClassT.id.asc()).all()

    ####check

    
    # from .check import run_all_checks, REQUIRED_KEYS
    # # 既存のクエリ結果を lists に束ねる
    # lists = {name: locals().get(name, []) for name in REQUIRED_KEYS}
    # # 判定
    # req_errors, summary = run_all_checks(uc_map, lists)
    # ####
    # from .check import run_all_checks, REQUIRED_KEYS
    # ── ここを追加 ─────────────────────────────
    from .check import run_all_checks
    show_check_modal = (request.args.get("check") == "1")
    req_errors = []
    total_credits = 0
    total_need = 120
    total_ok = False

    if show_check_modal:
        # check.py にまとめた処理を呼ぶ（戻りのキー名はあなたの実装に合わせて）
        result = run_all_checks(db.session, user_id_str, uc_map)
        req_errors = result["errors"]           # 不足の配列（コード、タイトル、detail、suggest、have/need など）
        total_credits = result["total_credits"] # 総取得単位
        total_need = result.get("total_need", 120)
        total_ok = (total_credits >= total_need)
    # ──────────────────────────────────────────


    return render_template("index.html",
                           do_list=do_list, kiso_kiban_jo_1=kiso_kiban_jo_1, kiso_kiban_su_1=kiso_kiban_su_1,
                           kiso_tagengo_1=kiso_tagengo_1, kiso_sekai_bunka_1=kiso_sekai_bunka_1, kiso_sekai_net_1=kiso_sekai_net_1,
                           kiso_sekai_keizai_1=kiso_sekai_keizai_1,
                           #########展開1
                           tenkai_kiban_jo_1=tenkai_kiban_jo_1,tenkai_kiban_su_1=tenkai_kiban_su_1,
                           tenkai_tagengo_1=tenkai_tagengo_1,tenkai_sekai_bunka_1=tenkai_sekai_bunka_1,
                           tenkai_sekai_net_1=tenkai_sekai_net_1,tenkai_shakai_keizai_1=tenkai_shakai_keizai_1,
                           tenkai_shakai_deji_1=tenkai_shakai_deji_1,
                           kiso_shakai_1=kiso_shakai_1,kiso_jiyu_1=kiso_jiyu_1,
                           #########展開2
                           tenkai_kiban_jo_2=tenkai_kiban_jo_2,tenkai_kiban_su_2=tenkai_kiban_su_2,
                           tenkai_tagengo_2=tenkai_tagengo_2,tenkai_sekai_bunka_2=tenkai_sekai_bunka_2,
                           tenkai_sekai_net_2=tenkai_sekai_net_2,tenkai_shakai_keizai_2=tenkai_shakai_keizai_2,
                           tenkai_shakai_deji_2=tenkai_shakai_deji_2,
                           kiso_shakai_2=kiso_shakai_2,kiso_jiyu_2=kiso_jiyu_2,
                           #########展開3
                           tenkai_kiban_jo_3=tenkai_kiban_jo_3,tenkai_kiban_su_3=tenkai_kiban_su_3,
                           #tenkai_tagengo_3=tenkai_tagengo_3,
                           tenkai_sekai_bunka_3=tenkai_sekai_bunka_3,
                           tenkai_sekai_net_3=tenkai_sekai_net_3,
                           #tenkai_shakai_keizai_3=tenkai_shakai_keizai_3,
                           tenkai_shakai_deji_3=tenkai_shakai_deji_3,
                           kiso_shakai_3=kiso_shakai_3,kiso_jiyu_3=kiso_jiyu_3,
                           #########考究
                           kokyu_jo=kokyu_jo,kokyu_su=kokyu_su,
                           kokyu_bunka=kokyu_bunka,kokyu_net=kokyu_net,kokyu_keizai=kokyu_keizai,
                           kokyu_deji=kokyu_deji,kokyu_shakai=kokyu_shakai,pj=pj,
                           ###check
                        # 追加で↓
                        show_check_modal=show_check_modal,
                        req_errors=req_errors,
                        total_credits=total_credits,
                        total_need=total_need,
                        total_ok=total_ok,
                        uc_map=uc_map
                           )

@bp.route("/healthz")
def healthz():
    return "ok", 200

def init_routes(app):
    app.register_blueprint(bp)



#
def get_user_class(user_id_str: str, clazz: ClassT):
    return UserClass.query.filter_by(user_id=user_id_str, kamokumei=clazz.kamokumei).first()

#更新画面
@bp.route("/update", methods=["GET", "POST"])
@login_required
def update():
    user_id_str = str(current_user.id)  # user_classes.user_id が String のため

    if request.method == "POST":
        action = request.form.get("action")

        if action == "to_right":
            # 左で選んだ科目を「取得済み」にする = user_classes に行を作る（無ければ）
            ids = request.form.getlist("left_ids")
            for cid in ids:
                clazz = db.session.get(ClassT, int(cid))
                if not clazz:
                    continue
                uc = get_user_class(user_id_str, clazz)
                if not uc:
                    uc = UserClass(user_id=user_id_str, kamokumei=clazz.kamokumei)
                    db.session.add(uc)
                # is_acquired は使わないが、残すなら "1" を入れておく
                uc.is_acquired = "1"
            db.session.commit()

        elif action == "to_left":
            # 右で選んだ科目を「未取得」に戻す = user_classes の行を削除
            ids = request.form.getlist("right_ids")
            for cid in ids:
                clazz = db.session.get(ClassT, int(cid))
                if not clazz:
                    continue
                uc = get_user_class(user_id_str, clazz)
                if uc:
                    db.session.delete(uc)
            db.session.commit()

        return redirect(url_for("main.update"))

    # GET: 左＝未取得（user_classes に行が無い科目のみ）
    left_items = (
        db.session.query(ClassT)
        .outerjoin(
            UserClass,
            (UserClass.kamokumei == ClassT.kamokumei) &
            (UserClass.user_id == user_id_str)
        )
        .filter(UserClass.id.is_(None))     # ← 行が無いものだけ
        .order_by(ClassT.id.asc())
        .all()
    )

    # 右＝取得済（user_classes に行があるもの）
    right_items = (
        db.session.query(ClassT)
        .join(
            UserClass,
            (UserClass.kamokumei == ClassT.kamokumei) &
            (UserClass.user_id == user_id_str)
        )
        .order_by(ClassT.id.asc())
        .all()
    )

    return render_template("update.html", left_items=left_items, right_items=right_items)


#
@bp.route("/check", methods=["GET"], endpoint="check_requirements")
@login_required
def check_requirements():
    # index に ?check=1 を付けてリダイレクト（同じ画面でモーダル表示）
    return redirect(url_for("main.index", check=1))

#####################
# CAの紹介
@bp.route("/ca_intro", methods=["GET"])
@login_required
def ca_intro():
    text = request.args.get("text")
    wav_bytes = generate_wav_bytes(text)
    return Response(wav_bytes, mimetype="audio/wav")