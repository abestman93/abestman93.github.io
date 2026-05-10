import os
import requests
import json
import pandas as pd
from FinMind.data import DataLoader

def get_advice(stock_id, current_price, current_volume, hist_df):
    # 計算簡單指標：均價與均量
    avg_price = hist_df['close'].mean()
    avg_volume = hist_df['Volume'].mean()
    
    advice = "觀察中"
    color = "#808080" # 灰色
    
    # 判斷邏輯：例如量增價漲
    if current_price > avg_price * 1.02 and current_volume > avg_volume * 1.5:
        advice = "⚠️ 強勢爆量：價漲量增，建議關注進場點！"
        color = "#FF0000" # 紅色
    elif current_price < avg_price * 0.98 and current_volume > avg_volume * 1.5:
        advice = "🚨 弱勢爆量：價跌量增，請注意回檔風險！"
        color = "#008000" # 綠色
    
    return advice, color, avg_price, avg_volume

def monitor():
    # --- 設定區 ---
    FINMIND_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYWJlc3RtYW45MyIsImVtYWlsIjoiYWJlc3RtYW45M0BnbWFpbC5jb20iLCJ0b2tlbl92ZXJzaW9uIjowfQ.765dsySj_ijbbkzhN8ZknCD4EpANAFCMLlMM71GFn0c" 
    LINE_TOKEN = "32nl+/weNf3OwzeNFDPQOsAy41QGQ/amosEvOpjjHMQwhsd2HmF2nN1HLHca3TyCwDe2H3b+2qUTdnlb3IwMmML7FWa6qO/OXQDudILbPEnuUzX5Vxy8mLGbp+z4ri9t45/P9I+FKHo9E0v+KrsfVwdB04t89/1O/w1cDnyilFU="
    USER_ID = "Ucd008679a0984fb58643a92ee1f2232c"
    STOCK_ID = "2330" # 監控目標
    
    api = DataLoader()
    api.login_by_token(api_token=FINMIND_TOKEN)
    
    # 1. 抓取歷史資料 (過去 30 天) 作為依據
    hist_df = api.taiwan_stock_daily(stock_id=STOCK_ID, start_date='2024-04-10')
    
    # 2. 抓取即時快照 (來自證交所即時數據)
    tick_df = api.taiwan_stock_tick_snapshot(stock_id=STOCK_ID)
    
    if not tick_df.empty:
        now_price = tick_df['last_price'][0]
        now_vol = tick_df['total_volume'][0]
        
        # 3. 取得分析建議
        advice, color, avg_p, avg_v = get_advice(STOCK_ID, now_price, now_vol, hist_df)
        
        # 4. 發送 LINE Flex Message
        send_line_advice(LINE_TOKEN, USER_ID, STOCK_ID, now_price, advice, color)

def send_line_advice(token, user_id, stock_id, price, advice, color):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    
    payload = {
        "to": user_id,
        "messages": [{
            "type": "flex",
            "altText": f"股價分析建議: {stock_id}",
            "contents": {
                "type": "bubble",
                "body": {
                    "type": "box", "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": f"股票 {stock_id} 分析結果", "weight": "bold", "size": "lg"},
                        {"type": "separator", "margin": "md"},
                        {"type": "text", "text": f"即時價格：{price}", "margin": "md", "size": "md"},
                        {"type": "text", "text": advice, "weight": "bold", "color": color, "margin": "lg", "wrap": True}
                    ]
                },
                "footer": {
                    "type": "box", "layout": "vertical",
                    "contents": [{
                        "type": "button", "style": "primary",
                        "action": {"type": "uri", "label": "開啟元大投資先生", "uri": "https://yuanta.com.tw"}
                    }]
                }
            }
        }]
    }
    requests.post(url, headers=headers, data=json.dumps(payload))

if __name__ == "__main__":
    monitor()
