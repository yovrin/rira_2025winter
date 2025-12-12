from app import create_app
import logging


app = create_app()

# ★ ここから追加：SQL を必ず標準出力に出す
logging.basicConfig(level=logging.INFO)
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)  # SQL文
logging.getLogger("sqlalchemy.pool").setLevel(logging.INFO)    # 接続取得など（任意）
# ★ ここまで追加
    
# ロガーのカスタマイズ
handler = logging.FileHandler('./flask_app.log')  # ファイルに出力
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

if __name__ == '__main__':
    app.logger.info("flask起動スタート")

    # app.run(debug=True)
    app.run(host="0.0.0.0", port=5000, debug=False)

