from fastapi import FastAPI, Request, Response
import pandas as pd
import requests
import os

app = FastAPI()

# LINEチャネルアクセストークン（Renderの環境変数）
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")

# CSV読み込み（起動時1回）
df = pd.read_csv(
    "bot検討用.csv",
    encoding="utf-8-sig"
)


def reply(reply_token, text):
    url = "https://api.line.me/v2/bot/message/reply"

    headers = {
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    body = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": text
            }
        ]
    }

    requests.post(
        url,
        headers=headers,
        json=body
    )


@app.get("/")
@app.head("/")
def root():
    return Response(
        content='{"status":"ok"}',
        media_type="application/json"
    )


@app.post("/callback")
async def callback(request: Request):
    body = await request.json()

    for event in body.get("events", []):

        if event.get("type") != "message":
            continue

        text = event["message"]["text"]

        try:
            number = int(text)

            result = df[df["組合員番号"] == number]

            if result.empty:
                reply_text = "該当データがありません"

            else:
                row = result.iloc[0]

                reply_text = (
                    f"利用総額は{int(row['利用総額']):,}円、\n"
                    f"コース順位は{int(row['コース数'])}人中{int(row['コース順位'])}位、\n"
                    f"全体順位は1240名中{int(row['全体順位'])}位です"
                )

        except ValueError:
            reply_text = "組合員番号を数字で入力してください"

        except Exception as e:
            reply_text = f"エラーが発生しました: {str(e)}"

        reply(event["replyToken"], reply_text)

    return {"status": "ok"}
