import os
from flask import Flask, request, abort
from dotenv import load_dotenv

from linebot import LineBotApi, WebhookHandler
from linebot.models import *
from linebot.exceptions import InvalidSignatureError

from utils.sheets import (
    get_cities_by_region,
    get_today_weather_for_city,
    get_tomorrow_weather_for_city,
    get_week_weather_for_city
)

# 載入 .env 檔案
load_dotenv()

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

user_state = {}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text.strip()

    if text == "天氣查詢":
        user_state[user_id] = {"stage": "region"}
        reply_regions(event)
    elif user_id in user_state:
        stage = user_state[user_id]["stage"]

        if stage == "region":
            user_state[user_id]["region"] = text
            user_state[user_id]["stage"] = "city"
            reply_cities(event, text)
        elif stage == "city":
            user_state[user_id]["city"] = text
            user_state[user_id]["stage"] = "time"
            reply_time_options(event, text)
        elif stage == "time":
            city = user_state[user_id]["city"]
            if text == "今天":
                reply_text(event, get_today_weather_for_city(city))
            elif text == "明天":
                reply_text(event, get_tomorrow_weather_for_city(city))
            elif text == "一週天氣":
                reply_text(event, get_week_weather_for_city(city))
            else:
                reply_text(event, "請輸入 今天 / 明天 / 一週天氣")
            user_state.pop(user_id, None)
        else:
            reply_text(event, "請從『天氣查詢』開始")
    else:
        reply_text(event, "請輸入『天氣查詢』開始")

def reply_regions(event):
    quick_reply = QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="北部", text="北部")),
        QuickReplyButton(action=MessageAction(label="中部", text="中部")),
        QuickReplyButton(action=MessageAction(label="南部", text="南部")),
        QuickReplyButton(action=MessageAction(label="東部", text="東部")),
        QuickReplyButton(action=MessageAction(label="外島", text="外島")),
    ])
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="請選擇地區：", quick_reply=quick_reply)
    )

def reply_cities(event, region):
    cities = get_cities_by_region(region)
    items = [QuickReplyButton(action=MessageAction(label=city, text=city)) for city in cities[:13]]
    quick_reply = QuickReply(items=items)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"請選擇縣市（{region}）：", quick_reply=quick_reply)
    )

def reply_time_options(event, city):
    quick_reply = QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="今天", text="今天")),
        QuickReplyButton(action=MessageAction(label="明天", text="明天")),
        QuickReplyButton(action=MessageAction(label="一週天氣", text="一週天氣")),
    ])
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"請選擇查詢時間（{city}）：", quick_reply=quick_reply)
    )

def reply_text(event, text):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=text)
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
