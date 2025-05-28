import streamlit as st

st.title("第7回 Streamlit 状態管理演習 - テンプレート")
st.caption("st.session_state を使って今日の気分を記録しましょう。")

st.markdown("---")
st.subheader("演習: 今日の気分記録アプリ")
st.write("**課題**: ボタンで気分を選択し、`st.session_state` で履歴を保持するアプリを作成する。")

# 気分の選択肢
moods = ["😊 良い", "😐 普通", "😔 悪い"]

# session_state に履歴を初期化
if "mood_history" not in st.session_state:
    st.session_state.mood_history = []

# 気分ボタンを表示
st.write("今日の気分を選んでください:")
for mood in moods:
    if st.button(mood):
        st.session_state.mood_history.append(mood)

# 履歴を表示
st.write("### 気分の履歴:")
st.write(st.session_state.mood_history)

st.markdown("---")
st.info("💡 気分ボタンを押すたびに履歴が蓄積され、アプリを再実行しても保持されることを確認してください。")
