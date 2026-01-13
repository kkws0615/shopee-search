import streamlit as st
import requests
import time
import pandas as pd

# 設定網頁標題與圖示
st.set_page_config(page_title="蝦皮省運費助手", page_icon="🛒", layout="centered")

# 自定義 CSS 讓介面更精美
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ee4d2d; color: white; }
    .seller-card { border: 1px solid #ddd; padding: 15px; border-radius: 10px; background: white; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛒 蝦皮共同賣家搜尋器")
st.subheader("一次買齊商品 A & B，節省運費與取貨時間！")

# 輸入區域
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        keyword_a = st.text_input("輸入第一個商品", placeholder="例如：iPhone 15 保護殼")
    with col2:
        keyword_b = st.text_input("輸入第二個商品", placeholder="例如：鋼化玻璃貼")

# 定義 API 請求函數
def fetch_shopee_data(keyword):
    # 使用模擬瀏覽器的 Header
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://shopee.tw/"
    }
    url = f"https://shopee.tw/api/v4/search/search_items?by=relevancy&keyword={keyword}&limit=60&newest=0&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        
        data = response.json()
        items = data.get('items', [])
        
        seller_dict = {}
        for item in items:
            b = item.get('item_basic')
            if b:
                shopid = b['shopid']
                seller_dict[shopid] = {
                    "itemid": b['itemid'],
                    "name": b['name'],
                    "price": b['price'] / 100000, # 蝦皮原始格式為 10^5
                    "image": f"https://down-tx-tw.img.susercontent.com/file/{b['image']}",
                    "rating": round(b['item_rating']['rating_star'], 1)
                }
        return seller_dict
    except:
        return None

# 按鈕觸發搜尋
if st.button("🔍 尋找共同賣家"):
    if not keyword_a or not keyword_b:
        st.error("⚠️ 請輸入兩個關鍵字！")
    else:
        with st.spinner("正在搜尋蝦皮數據，請稍候..."):
            # 獲取兩邊的資料
            dict_a = fetch_shopee_data(keyword_a)
            time.sleep(1.5) # 緩衝避免被封鎖
            dict_b = fetch_shopee_data(keyword_b)

            if dict_a is None or dict_b is None:
                st.error("❌ 請求過於頻繁或蝦皮阻擋，請稍後再試。")
            else:
                # 取交集
                common_shop_ids = set(dict_a.keys()) & set(dict_b.keys())

                if not common_shop_ids:
                    st.warning("☹️ 找不到同時賣這兩樣商品的賣家。建議縮短關鍵字再試一次。")
                else:
                    st.success(f"🎊 成功找到 {len(common_shop_ids)} 位共同賣家！")
                    
                    for shopid in common_shop_ids:
                        a = dict_a[shopid]
                        b = dict_b[shopid]
                        
                        # 顯示結果卡片
                        with st.container():
                            st.markdown(f"""
                            <div class="seller-card">
                                <h4>🏪 賣場 ID: {shopid}</h4>
                                <div style="display:flex; gap: 20px;">
                                    <div style="flex:1;">
                                        <p><b>商品 A:</b> {a['name'][:40]}...</p>
                                        <p style="color:#ee4d2d;">💰 ${a['price']}</p>
                                    </div>
                                    <div style="flex:1;">
                                        <p><b>商品 B:</b> {b['name'][:40]}...</p>
                                        <p style="color:#ee4d2d;">💰 ${b['price']}</p>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            st.link_button(f"👉 前往該賣場", f"https://shopee.tw/shop/{shopid}")
                            st.divider()

st.info("💡 提示：關鍵字越簡短（如：手機殼），越容易找到重疊的賣家。")
