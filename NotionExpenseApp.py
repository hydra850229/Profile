import streamlit as st
import requests
from datetime import date

# --- Config ---
NOTION_API_TOKEN = "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"
EXPENSE_DB_ID = "9152b63ce781493daf5a25802a561bbf"
CATEGORY_DB_ID = "2e4da94aa65e4a62a9be96510bf46f7f"

headers = {
    "Authorization": f"Bearer {NOTION_API_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# --- Functions ---
def fetch_category_map():
    url = f"https://api.notion.com/v1/databases/{CATEGORY_DB_ID}/query"
    res = requests.post(url, headers=headers)
    if res.status_code != 200:
        st.error(f"❌ 取得分類資料庫失敗：{res.status_code}")
        return {}

    data = res.json()["results"]
    category_map = {}
    for item in data:
        try:
            title = item["properties"]["類別"]["title"][0]["text"]["content"]
            page_id = item["id"]
            category_map[title] = page_id
        except:
            continue
    return category_map

def send_expense(name, amount, category_name, category_map):
    if category_name not in category_map:
        st.warning(f"⚠️ 找不到類別：{category_name}")
        return False

    payload = {
        "parent": {"database_id": EXPENSE_DB_ID},
        "properties": {
            "項目": {
                "title": [
                    {"text": {"content": name}}
                ]
            },
            "費用": {"number": amount},
            "類別": {
                "relation": [{"id": category_map[category_name]}]
            },
            "日期": {
                "date": {"start": date.today().isoformat()}
            }
        }
    }

    res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
    return res.status_code == 200

def batch_send_expense(batch_text, category_map):
    entries = batch_text.strip().splitlines()
    success_count = 0
    fail_count = 0
    for entry in entries:
        parts = entry.strip().split(",")
        if len(parts) != 3:
            fail_count += 1
            continue
        name, amt_str, cat = parts
        try:
            amt = float(amt_str)
            if send_expense(name.strip(), amt, cat.strip(), category_map):
                success_count += 1
            else:
                fail_count += 1
        except:
            fail_count += 1
    return success_count, fail_count

# --- UI ---
st.title("🧾 Notion 記帳小幫手")

category_map = fetch_category_map()

st.subheader("📋 批次記帳輸入")
st.markdown("輸入格式（每行一筆）：項目,金額,類別\n例如：\n早餐,80,飲食\n加油,100,交通")

if "batch_input" not in st.session_state:
    st.session_state.batch_input = ""

# 模板按鈕設定
TEMPLATES = [
    ("早餐,80,飲食", "🍽 早餐80"),
    ("加油,100,交通", "⛽ 加油100"),
    ("午餐,120,飲食", "🍱 午餐120")
]

col1, col2 = st.columns([3, 1])
with col1:
    st.session_state.batch_input = st.text_area("請貼上多筆記帳資料：", st.session_state.batch_input, height=150)
with col2:
    st.markdown("### 快捷模板")
    for value, label in TEMPLATES:
        if st.button(label):
            if st.session_state.batch_input.strip():
                st.session_state.batch_input += "\n" + value
            else:
                st.session_state.batch_input = value

if st.button("✅ 批次寫入 Notion"):
    if st.session_state.batch_input.strip():
        ok, fail = batch_send_expense(st.session_state.batch_input, category_map)
        st.success(f"✅ 成功 {ok} 筆，❌ 失敗 {fail} 筆")
    else:
        st.warning("請輸入至少一筆記帳資料")
