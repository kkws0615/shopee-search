import streamlit as st
import requests
import time
import random

# 設定網頁標題
st.set_page_config(page_title="蝦皮共同賣家搜尋", page_icon="🛒")

st.title("🛒 蝦皮共同賣家搜尋器")
st.write("輸入商品 A 與 B，找出同時賣這兩樣東西的店家。")

# --- 進階防爬蟲函數 ---
def get_shopee_items(keyword):
    # 1. 模擬更像真人的 Headers
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1"
    ]
    
    headers = {
        "User-Agent": random.choice(user_agents),
        "Referer": "https://shopee.tw/",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "x-api-source": "pc",
        "x-shopee-language": "zh-Hant",
    }

    # 2. 加上隨機延遲，不要瞬間發出兩次請求
    time.sleep(random.uniform(2.0, 4.0))

    url = f"https://shopee.tw/api/v4/search/search_items?by=relevancy&keyword={keyword}&limit=60&newest=0&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2"
    
    try:
        # 使用 Session 來保持連線狀態
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=10)
        
        if response.status_code == 403:
            return "blocked"
        
        data = response.json()
        items = data.get('items', [])
        
        sellers = {}
        for item in items:
            b = item.get('item_basic')
            if b:
                sellers[b['shopid']] = {
                    "price": b['price'] / 100000,
                    "name": b['name']
                }
        return sellers
    except:
        return None

# --- UI 介面 ---
col1, col2 = st.columns(2)
with col1:
    input_a = st.text_input("商品 A", placeholder="例如：iPhone殼")
with col2:
    input_b = st.text_input("商品 B", placeholder="例如：玻璃貼")

if st.button("開始搜尋"):
    if input_a and input_b:
        with st.spinner("正在安全搜尋中，請稍候約 5-10 秒..."):
            # 搜尋商品 A
            res_a = get_shopee_items(input_a)
            
            if res_a == "blocked":
                st.error("❌ 被蝦皮偵測到機器人行為 (403)，請過 5 分鐘後再試。")
            elif res_a:
                # 搜尋商品 B
                res_b = get_shopee_items(input_b)
                
                if res_b == "blocked":
                    st.error("❌ 搜尋商品 B 時被擋，請稍後。")
                elif res_b:
                    # 取交集
                    common = set(res_a.keys()) & set(res_b.keys())
                    
                    if common:
                        st.success(f"找到 {len(common)} 個共同賣家！")
                        for sid in common:
                            st.markdown(f"**🏪 賣家 ID: {sid}**")
                            st.write(f"👉 {input_a}: ${res_a[sid]['price']}")
                            st.write(f"👉 {input_b}: ${res_b[sid]['price']}")
                            st.link_button("進入賣場", f"https://shopee.tw/shop/{sid}")
                            st.divider()
                    else:
                        st.warning("沒找到共同賣家。")
            else:
                st.error("搜尋失敗，可能關鍵字有誤或網路不穩。")
    else:
        st.info("請輸入關鍵字")
