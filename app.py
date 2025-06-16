import streamlit as st
import datetime
import pandas as pd
import re

st.title("ToDoリストアプリ")
st.caption("優先度・期限・カテゴリ管理付きのToDoリスト + メモ＆画像機能")

# ToDoリストとカテゴリの初期化
if "todo_list" not in st.session_state:
    st.session_state.todo_list = []

if "categories" not in st.session_state:
    st.session_state.categories = ["仕事", "学業", "趣味", "その他"]

categories = st.session_state.categories

# --- カテゴリ管理フォーム ---
st.subheader("🛠️ カテゴリ管理")
with st.form("category_form", clear_on_submit=True):
    new_category = st.text_input("新しいカテゴリを追加", placeholder="例: 家事")
    category_to_delete = st.selectbox("削除するカテゴリを選択", ["（選択なし）"] + categories)
    cat_submitted = st.form_submit_button("カテゴリを追加 / 削除")

    if cat_submitted:
        if new_category:
            if new_category in categories:
                st.warning("このカテゴリは既に存在します。")
            else:
                st.session_state.categories.append(new_category)
                st.success(f"カテゴリ「{new_category}」を追加しました")
        elif category_to_delete != "（選択なし）":
            if any(t["category"] == category_to_delete for t in st.session_state.todo_list):
                st.warning("このカテゴリを使っているタスクがあるため削除できません。")
            else:
                st.session_state.categories = [c for c in categories if c != category_to_delete]
                st.success(f"カテゴリ「{category_to_delete}」を削除しました")
        else:
            st.info("カテゴリの追加か削除を行ってください。")

# --- タスク追加フォーム ---
st.subheader("🆕 新しいタスクを追加")
with st.form("add_task_form", clear_on_submit=True):
    new_task = st.text_input("タスク内容", placeholder="例: レポートを書く")
    priority = st.selectbox("優先度", ["低", "中", "高"])
    deadline_date = st.date_input("期限（日付）", value=datetime.date.today())

    st.markdown("※ 時刻は `HH:MM` 形式（例: 14:30、24時間表記）で入力してください。")
    deadline_time_str = st.text_input("期限（時間）", placeholder="例: 14:30")
    time_pattern = r"^([01]?\d|2[0-3]):[0-5]\d$"

    category = st.selectbox("カテゴリ", categories)
    memo = st.text_area("📝 メモ（任意）", placeholder="補足事項などを記入できます")
    image = st.file_uploader("📷 画像を添付（任意）", type=["png", "jpg", "jpeg"])
    submitted = st.form_submit_button("タスクを追加")

    def is_valid_time(t):
        try:
            return re.match(time_pattern, t) is not None
        except Exception:
            return False

    if submitted:
        if not new_task:
            st.error("タスク内容を入力してください。")
        elif not is_valid_time(deadline_time_str):
            st.error("時刻の形式が正しくありません。例: 14:30（24時間表記）")
        else:
            deadline_time = datetime.datetime.strptime(deadline_time_str, "%H:%M").time()
            deadline = datetime.datetime.combine(deadline_date, deadline_time)

            new_entry = {
                "task": new_task,
                "done": False,
                "priority": priority,
                "deadline": deadline,
                "category": category,
                "memo": memo,
                "image": image
            }
            st.session_state.todo_list = st.session_state.todo_list + [new_entry]
            st.success(f"「{new_task}」を追加しました！")

# --- カテゴリで絞り込み ---
st.subheader("📂 カテゴリ別表示")
filter_category = st.selectbox("表示するカテゴリ", ["すべて"] + categories)

# フィルター処理
if filter_category == "すべて":
    filtered_tasks = st.session_state.todo_list
else:
    filtered_tasks = [t for t in st.session_state.todo_list if t["category"] == filter_category]

# --- ToDoリスト表示 ---
st.subheader("📝 タスクリスト")

if not filtered_tasks:
    st.info("このカテゴリにはタスクがありません。")
else:
    for i, item in enumerate(filtered_tasks):
        col1, col2, col3 = st.columns([5, 1, 1])
        with col1:
            label = f"{item['task']}（優先度: {item['priority']}、期限: {item['deadline'].strftime('%Y-%m-%d %H:%M')}）"
            checked = st.checkbox(label, value=item["done"], key=f"checkbox_{i}")
            if checked != item["done"]:
                # 元リストのインデックスを特定して更新
                idx = st.session_state.todo_list.index(item)
                todo_list_copy = st.session_state.todo_list.copy()
                todo_list_copy[idx]["done"] = checked
                st.session_state.todo_list = todo_list_copy

            if item.get("memo"):
                st.markdown(f"**📝 メモ:** {item['memo']}")

            if item.get("image") is not None:
                st.image(item["image"], width=200)

        with col2:
            if st.button("🗑️", key=f"delete_{i}"):
                todo_list_copy = [t for t in st.session_state.todo_list if t != item]
                st.session_state.todo_list = todo_list_copy
                st.success("タスクを削除しました")

        with col3:
            st.write(f"📁 {item['category']}")

# --- 一括操作 ---
if st.session_state.todo_list:
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ 全て完了にする"):
            todo_list_copy = st.session_state.todo_list.copy()
            for item in todo_list_copy:
                item["done"] = True
            st.session_state.todo_list = todo_list_copy
            st.success("全てのタスクを完了にしました！")
    with col2:
        if st.button("🧹 完了済みを削除"):
            st.session_state.todo_list = [t for t in st.session_state.todo_list if not t["done"]]
            st.success("完了済みタスクを削除しました")
