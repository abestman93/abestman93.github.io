import os
import requests
import json
import pandas as pd
from FinMind.data import DataLoader

def get_advice(stock_id, current_price, current_volume, hist_df):
    # 計算 30 日均價與均量
    avg_price = hist_df['close'].mean()
    avg_volume = hist_df['Volume'].mean()
    
    advice = f"目前價格 {current_price} 處於盤整區間。"
    color = "⚪️" 
    
    # 判斷邏輯：價漲量增 (價格 > 均價 2% 且 交易量 > 均量 1.5 倍)
    if current_price > avg_price * 1.02 and current_volume > avg_volume * 1.5:
        advice = "⚠️ 強勢爆量：價漲量增，建議關注進場點！"
        color = "🔴" 
    elif current_price < avg_price * 0.98 and current_volume > avg_volume * 1.5:
        advice = "🚨 弱勢爆量：價跌量增，請注意回檔風險！"
        color = "🟢" 
    
    return advice, color

def monitor():
    # --- 設定區 (已填入您的正確資訊) ---
    FINMIND_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYWJlc3RtYW45MyIsImVtYWlsIjoiYWJlc3RtYW45M0BnbWFpbC5jb20iLCJ0b2tlbl92ZXJzaW9uIjowfQ.765dsySj_ijbbkzhN8ZknCD4EpANAFCMLlMM71GFn0c".strip()
    TG_TOKEN = "8774997405:AAGUMlYMjgyEwePAq1sKL3sACxh-hwhjryc"
    CHAT_ID = "8753483383" 
    STOCK_ID = "2330" 
    
    api = DataLoader()
    # 登入 FinMind
    try:
        api.login_by_token(api_token=FINMIND_TOKEN)
    except Exception as e:
        print(f"FinMind 登入失敗：{e}")
        return

    # 1. 抓取歷史資料
    hist_df = api.taiwan_stock_daily(stock_id=STOCK_ID, start_date='2024-04-10')
    
    # 2. 抓取今日成交資訊 (免費版指令)
    try:
        tick_df = api.taiwan_stock_daily_info(stock_id=STOCK_ID)
        
        if not tick_df.empty:
            # 取得最新收盤價與當日成交量
            now_price = float(tick_df['close'].iloc[0])
            now_vol = float(tick_df['vol'].iloc[0])
            
            # 3. 取得分析建議
            advice, color = get_advice(STOCK_ID, now_price, now_vol, hist_df)
            
            # 4. 發送至 Telegram (完全免費，不限次數)
            send_telegram_advice(TG_TOKEN, CHAT_ID, STOCK_ID, now_price, advice, color)
            print(f"成功發送 Telegram 監控訊息，價格: {now_price}")
        else:
            print("今日目前無交易資料 (可能尚未開盤)")
            
    except Exception as e:
        print(f"執行出錯: {e}")

def send_telegram_advice(token, chat_id, stock_id, price, advice, color):
    # 分段拼湊路徑確保 API 正確性
    p1 = "https://api."
    p2 = "telegram.org/bot"
    p3 = token
    p4 = "/sendMessage"
    url = p1 + p2 + p3 + p4
    
    # 組合 Telegram 訊息文字
    message_text = f"{color} *股票 {stock_id} 分析結果*\n" \
                   f"━━━━━━━━━━━━━━━\n" \
                   f"💰 目前價格：{price}\n" \
                   f"💡 建議：{advice}"

    payload = {
        "chat_id": chat_id,
        "text": message_text,
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [[
                {
                    "text": "🚀 立即開啟投資先生 App", 
                    # 改用元大行動裝置專用的通用連結，點擊後 iPhone 會詢問是否開啟 App
                    "url": "https://www.yuanta.com.tw"
                }
            ]]
        }
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    monitor()
