import os
import requests
import json
import pandas as pd
from FinMind.data import DataLoader

def get_advice(stock_id, current_price, current_volume, hist_df):
    avg_price = hist_df['close'].mean()
    avg_volume = hist_df['Volume'].mean()
    advice = f"目前價格 {current_price} 處於盤整區間。"
    color = "⚪️" 
    if current_price > avg_price * 1.02 and current_volume > avg_volume * 1.5:
        advice = "⚠️ 強勢爆量：價漲量增，建議關注進場點！"
        color = "🔴" 
    elif current_price < avg_price * 0.98 and current_volume > avg_volume * 1.5:
        advice = "🚨 弱勢爆量：價跌量增，請注意回檔風險！"
        color = "🟢" 
    return advice, color

def monitor():
    # --- 設定區 ---
    # 使用 .strip() 確保 Token 不會因為隱藏空格而失效
    FINMIND_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYWJlc3RtYW45MyIsImVtYWlsIjoiYWJlc3RtYW45M0BnbWFpbC5jb20iLCJ0b2tlbl92ZXJzaW9uIjowfQ.765dsySj_ijbbkzhN8ZknCD4EpANAFCMLlMM71GFn0c".strip()
    TG_TOKEN = "8774997405:AAGUMlYMjgyEwePAq1sKL3sACxh-hwhjryc"
    CHAT_ID = "8753483383" 
    STOCK_ID = "2330" 
    
    api = DataLoader()
    # 登入 FinMind
    try:
        api.login_by_token(api_token=FINMIND_TOKEN)
    except Exception as e:
        print(f"FinMind 登入失敗，請確認 Token 是否正確：{e}")
        return

    # 1. 抓取歷史資料
    hist_df = api.taiwan_stock_daily(stock_id=STOCK_ID, start_date='2024-04-10')
    
    # 2. 抓取今日成交資訊
    try:
        tick_df = api.taiwan_stock_daily_info(stock_id=STOCK_ID)
now_price = 1050.0
now_vol = 50000.0
send_telegram_advice(TG_TOKEN, CHAT_ID, STOCK_ID, now_price, advice="這是假日模擬測試成功！", color="🔵")
        if not tick_df.empty:
            now_price = float(tick_df['close'].iloc[0])
            now_vol = float(tick_df['vol'].iloc[0])
            advice, color = get_advice(STOCK_ID, now_price, now_vol, hist_df)
            send_telegram_advice(TG_TOKEN, CHAT_ID, STOCK_ID, now_price, advice, color)
            print(f"成功發送 Telegram 監控訊息")
        else:
            print("今日目前無交易資料")
    except Exception as e:
        print(f"執行出錯: {e}")

def send_telegram_advice(token, chat_id, stock_id, price, advice, color):
    # 分段拼湊網址避免錯誤
    url = "https://api." + "telegram.org/bot" + token + "/sendMessage"
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
                {"text": "🚀 開啟投資先生", "url": "https://yuanta.com.tw"}
            ]]
        }
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    monitor()
