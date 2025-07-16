import streamlit as st
import sqlite3
import os
from datetime import date
from PIL import Image

# ----------------------------
# 初期設定（画像保存・DB作成）
# ----------------------------
os.makedirs("images", exist_ok=True)
db_path = "records.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

# イベントテーブル
c.execute('''CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_date TEXT,
    venue TEXT,
    companion TEXT,
    spending INTEGER,
    items TEXT,
    tags TEXT,
    wait_time TEXT,
    notes TEXT
)''')

# 画像テーブル（キャプション削除済）
c.execute('''CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER,
    filename TEXT
)''')
conn.commit()

# ----------------------------
# 削除処理（POST時）
# ----------------------------
if "delete_id" in st.session_state:
    delete_id = st.session_state.delete_id
    # 画像削除
    c.execute("SELECT filename FROM images WHERE event_id = ?", (delete_id,))
    for (filename,) in c.fetchall():
        try:
            os.remove(os.path.join("images", filename))
        except FileNotFoundError:
            pass
    c.execute("DELETE FROM images WHERE event_id = ?", (delete_id,))
    c.execute("DELETE FROM events WHERE id = ?", (delete_id,))
    conn.commit()
    st.success(f"🗑️ 記録（ID:{delete_id}）を削除しました")
    del st.session_state.delete_id  # 削除フラグを消す

# ----------------------------
# イベント入力フォーム
# ----------------------------
st.title("🎪 オフラインイベント記録システム")

with st.form("event_form", clear_on_submit=True):
    st.subheader("📝 イベントの記録を入力")
    event_date = st.date_input("日付", value=date.today())
    venue = st.text_input("会場")
    companion = st.text_input("誰と行ったか")
    spending = st.number_input("支出額（円）", min_value=0, step=100)
    items = st.text_area("購入品")
    tags = st.text_input("タグ（例：#あんスタ #コミケ） ※半角スペースで複数可")
    wait_time = st.selectbox("待ち時間", ["なし", "〜15分", "15〜30分", "30分以上", "1時間以上"])
    notes = st.text_area("感想・メモ")

    uploaded_images = st.file_uploader("画像をアップロード（複数可）", accept_multiple_files=True, type=["png", "jpg", "jpeg"])

    submitted = st.form_submit_button("保存")
    if submitted:
        c.execute(
            "INSERT INTO events (event_date, venue, companion, spending, items, tags, wait_time, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (event_date.isoformat(), venue, companion, spending, items, tags, wait_time, notes)
        )
        event_id = c.lastrowid

        for img in uploaded_images:
            filename = f"{event_id}_{img.name}"
            filepath = os.path.join("images", filename)
            with open(filepath, "wb") as f:
                f.write(img.getbuffer())
            c.execute("INSERT INTO images (event_id, filename) VALUES (?, ?)", (event_id, filename))

        conn.commit()
        st.success("✅ 記録を保存しました！")

# ----------------------------
# タグによるフィルタリング
# ----------------------------
st.header("🔖 タグで分類して記録を見る")

# タグを全部取得してリスト化
c.execute("SELECT tags FROM events")
all_tags = []
for row in c.fetchall():
    if row[0]:
        tag_list = row[0].split()
        all_tags.extend(tag_list)

unique_tags = sorted(set(all_tags))

selected_tag = st.selectbox("表示したいタグを選んでください", ["すべて表示"] + unique_tags)

# ----------------------------
# 記録の表示（フィルター対応）
# ----------------------------
if selected_tag == "すべて表示":
    c.execute("SELECT * FROM events ORDER BY event_date DESC")
else:
    c.execute("SELECT * FROM events WHERE tags LIKE ? ORDER BY event_date DESC", (f"%{selected_tag}%",))

events = c.fetchall()

st.header("📚 記録一覧")

for event in events:
    eid, edate, venue, comp, spend, items, tags, wait, notes = event
    with st.expander(f"{edate}：{venue}（{tags}）"):
        st.markdown(f"""
        - 👥 同行者：{comp}  
        - 💸 支出：¥{spend}  
        - 🛍️ 購入品：{items}  
        - ⏱️ 待ち時間：{wait}  
        - 📝 感想：{notes}
        """)

        # 画像表示（スライド風）
        c.execute("SELECT filename FROM images WHERE event_id = ?", (eid,))
        imgs = c.fetchall()
        if imgs:
            st.markdown("📷 イベント写真")
            img_paths = [os.path.join("images", fname[0]) for fname in imgs]

            img_idx = st.slider("スライド", 0, len(img_paths) - 1, 0, key=f"slider_{eid}")
            image = Image.open(img_paths[img_idx])
            st.image(image, use_column_width=True)

        # 削除ボタン
        if st.button("🗑️ この記録を削除", key=f"delete_{eid}"):
            st.session_state.delete_id = eid
            st.rerun()
