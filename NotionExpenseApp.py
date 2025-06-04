import streamlit as st
import requests
from datetime import datetime
import pytz

# --- Config ---
NOTION_API_TOKEN = "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"
EXPENSE_DB_ID = "9152b63ce781493daf5a25802a561bbf"
CATEGORY_DB_ID = "2e4da94aa65e4a62a9be96510bf46f7f"

headers = {
    "Authorization": f"Bearer {NOTION_API_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# --- State ---
if "input_area" not in st.session_state:
    st.session_state.input_area = ""
if "clear_input" not in st.session_state:
    st.session_state.clear_input = False

# Handle clear action before text_area is rendered
if st.session_state.clear_input:
    st.session_state.input_area = ""
    st.session_state.clear_input = False
    st.rerun()

# --- Get today's date in Taiwan time ---
tz = pytz.timezone("Asia/Taipei")
today_str = datetime.now(tz).date().isoformat()

# --- Fetch category map ---
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

# --- Send to Notion ---
def send_expense(name, amount, category_name, category_map):
    if category_name not in category_map:
        st.warning(f"⚠️ 找不到類別：{category_name}")
        return False

    payload = {
        "parent": {"database_id": EXPENSE_DB_ID},
        "properties": {
            "項目": {"title": [{"text": {"content": name}}]},
            "費用": {"number": float(amount)},
            "類別": {"relation": [{"id": category_map[category_name]}]},
            "日期": {"date": {"start": today_str}}
        }
    }

    res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
    return res.status_code == 200

# --- UI ---
st.title("📥 批次記帳小幫手")
st.markdown("輸入格式：每行一筆資料，如：\n早餐,80,飲食")
st.text_area("請貼上多筆記帳資料：", value=st.session_state.input_area, height=150, key="input_area")

# 分類 map
category_map = fetch_category_map()

# 動作按鈕區域
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("✅ 寫入 Notion"):
        entries = st.session_state.input_area.strip().splitlines()
        success, fail = 0, 0
        for line in entries:
            try:
                name, amount, category = [x.strip() for x in line.split(",")]
                if send_expense(name, amount, category, category_map):
                    success += 1
                else:
                    fail += 1
            except Exception as e:
                print("❌ 格式錯誤：", line)
                fail += 1
        st.success(f"✅ 成功 {success} 筆，❌ 失敗 {fail} 筆")

with col2:
    if st.button("🧹 清除重填"):
        st.session_state.clear_input = True
        st.rerun()
