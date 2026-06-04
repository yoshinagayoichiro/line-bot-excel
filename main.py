from fastapi import FastAPI, Request
import pandas as pd
import requests
import os

app = FastAPI()

CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")

# データ読み込み（起動時1回）
df = pd.read_excel("bot検討用.xlsx")

def reply(reply_token, text):
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}]
    }
    requests.post(url, headers=headers, json=body)

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/callback")
async def callback(request: Request):
    body = await request.json()

    for event in body.get("events", []):
        if event["type"] != "message":
            continue

        text = event["message"]["text"]

        try:
            number = int(text)
        except:
            reply_text = "組合員番号を数字で入力してください"
        else:
            result = df[df["組合員番号"] == number]

            if result.empty:
                reply_text = "該当データがありません"
            else:
                row = result.iloc[0]

                reply_text = (
                    f"利用総額は{row['利用総額']}円、
"
                    f"コース順位は{row['コース数']}人中{row['コース順位']}位、
"
                    f"全体順位は1240名中{row['全体順位']}位です"
                )

        reply(event["replyToken"], reply_text)

    return "OK"
