import os
import requests
import json

def send_button_message():
    # 這裡直接填入你的資訊 (注意：Token 很長，必須用引號包起來)
    token = "32nl+/weNf3OwzeNFDPQOsAy41QGQ/amosEvOpjjHMQwhsd2HmF2nN1HLHca3TyCwDe2H3b+2qUTdnlb3IwMmML7FWa6qO/OXQDudILbPEnuUzX5Vxy8mLGbp+z4ri9t45/P9I+FKHo9E0v+KrsfVwdB04t89/1O/w1cDnyilFU="
    user_id = "Ucd008679a0984fb58643a92ee1f2232c"
    
    # 錯誤修正：LINE API 的正確傳送網址是這個
    url = "https://api.line.me/v2/bot/message/push"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # 定義按鈕訊息
    payload = {
        "to": user_id,
        "messages": [
            {
                "type": "flex",
                "altText": "GitHub 通知訊息",
                "contents": {
                  "type": "bubble",
                  "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                      {"type": "text", "text": "網站部署狀態", "weight": "bold", "size": "xl"},
                      {"type": "text", "text": "你的 GitHub Pages 專案已更新！", "margin": "md"}
                    ]
                  },
                  "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                      {
                        "type": "button",
                        "style": "primary",
                        "action": {
                          "type": "uri",
                          "label": "查看我的網頁",
                          "uri": "https://abestman93.github.io"
                        }
                      }
                    ]
                  }
                }
            }
        ]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        print("訊息傳送成功！")
    else:
        print(f"傳送失敗，狀態碼：{response.status_code}")
        print(f"錯誤原因：{response.text}")

if __name__ == "__main__":
    send_button_message()
