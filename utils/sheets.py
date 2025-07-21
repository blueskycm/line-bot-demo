import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json

load_dotenv()
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

# 🌀 天氣圖示

def get_weather_icon(desc: str) -> str:
    mapping = [
        ("雷", "⛈️"),
        ("陣雨", "🌦️"),
        ("雨", "🌧️"),
        ("雪", "❄️"),
        ("晴", "☀️"),
        ("多雲", "🌤️"),
        ("陰", "☁️"),
    ]
    for keyword, emoji in mapping:
        if keyword in desc:
            return emoji
    return "🌈"

def get_uvi_level(uvi: str) -> str:
    try:
        value = float(uvi)
    except:
        return f"{uvi}（未知）"
    if value <= 2:
        return f"{uvi}（低量級🟢）"
    elif value <= 5:
        return f"{uvi}（中量級🟡）"
    elif value <= 7:
        return f"{uvi}（高量級🟠）"
    elif value <= 10:
        return f"{uvi}（過量級🔴）"
    else:
        return f"{uvi}（危險級🟣）"

def get_weekday(date_str: str):
    return ['星期一','星期二','星期三','星期四','星期五','星期六','星期日'][datetime.strptime(date_str, "%Y-%m-%d").weekday()]

# 📄 Google Sheets 讀取

def get_sheet(name: str):
    scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    creds_info = json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON"))
    creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).worksheet(name)

def get_cities_by_region(region: str):
    sheet = get_sheet("city_info")
    rows = sheet.get_all_values()
    return [row[0] for row in rows[1:] if row[2] == region]

def get_all_cities():
    sheet = get_sheet("city_info")
    rows = sheet.get_all_values()
    return list({row[0] for row in rows[1:]})

# ☀️ 今日天氣

def get_today_weather_for_city(city_name: str):
    sheet = get_sheet("weather_data")
    rows = sheet.get_all_values()
    today_str = datetime.today().strftime("%Y-%m-%d")
    latest_timestamp = sorted({row[11] for row in rows[1:] if row[1] == city_name})[-1]

    for row in rows[1:]:
        if row[1] == city_name and row[0] == today_str and row[11] == latest_timestamp:
            day_min, day_max, day_desc = row[2], row[3], row[4]
            night_min, night_max, night_desc = row[5], row[6], row[7]
            feel_min, feel_max = row[8], row[9]
            uvi = row[10]
            weekday = get_weekday(today_str)
            return f"""📍 {city_name} 今日天氣（{today_str} {weekday}）\n\n{get_weather_icon(day_desc)} 白天：{day_min}°C - {day_max}°C\n　　　　 {day_desc}\n{get_weather_icon(night_desc)} 晚上：{night_min}°C - {night_max}°C\n　　　　 {night_desc}\n🌀 體感：{feel_min}°C - {feel_max}°C\n🔆 紫外線指數：{get_uvi_level(uvi)}\n\n資料來源：交通部中央氣象署(https://www.cwa.gov.tw/V8/C/)"""

    return f"找不到 {city_name} 的今日天氣資料 😢"

# 🌤 明天天氣

def get_tomorrow_weather_for_city(city_name: str):
    sheet = get_sheet("weather_data")
    rows = sheet.get_all_values()
    tomorrow_str = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    latest_timestamp = sorted({row[11] for row in rows[1:] if row[1] == city_name})[-1]

    for row in rows[1:]:
        if row[1] == city_name and row[0] == tomorrow_str and row[11] == latest_timestamp:
            day_min, day_max, day_desc = row[2], row[3], row[4]
            night_min, night_max, night_desc = row[5], row[6], row[7]
            feel_min, feel_max = row[8], row[9]
            uvi = row[10]
            weekday = get_weekday(tomorrow_str)
            return f"""📍 {city_name} 明日天氣（{tomorrow_str} {weekday}）\n\n{get_weather_icon(day_desc)} 白天：{day_min}°C - {day_max}°C\n　　　　 {day_desc}\n{get_weather_icon(night_desc)} 晚上：{night_min}°C - {night_max}°C\n　　　　 {night_desc}\n🌀 體感：{feel_min}°C - {feel_max}°C\n🔆 紫外線指數：{get_uvi_level(uvi)}\n\n資料來源：交通部中央氣象署(https://www.cwa.gov.tw/V8/C/)"""

    return f"找不到 {city_name} 的明日天氣資料 😢"

# 📅 一週天氣

def get_week_weather_for_city(city_name: str):
    sheet = get_sheet("weather_data")
    rows = sheet.get_all_values()
    latest_timestamp = sorted({row[11] for row in rows[1:] if row[1] == city_name})[-1]

    result = f"📍 {city_name} 一週天氣預報\n\n"
    count = 0

    for row in rows[1:]:
        if row[1] == city_name and row[11] == latest_timestamp:
            date_str = row[0]
            day_min, day_max, day_desc = row[2], row[3], row[4]
            night_min, night_max, night_desc = row[5], row[6], row[7]
            feel_min, feel_max = row[8], row[9]
            uvi = row[10]
            weekday = get_weekday(date_str)

            result += f"{date_str}（{weekday}）\n"
            result += f"{get_weather_icon(day_desc)} 白天：{day_min}°C - {day_max}°C\n　　　　 {day_desc}\n"
            result += f"{get_weather_icon(night_desc)} 晚上：{night_min}°C - {night_max}°C\n　　　　 {night_desc}\n"
            result += f"🌀 體感：{feel_min}°C - {feel_max}°C\n"
            result += f"🔆 紫外線指數：{get_uvi_level(uvi)}\n\n"

            count += 1
            if count >= 7:
                break

    if count == 0:
        return f"找不到 {city_name} 的一週天氣資料 😢"

    result += "資料來源：交通部中央氣象署(https://www.cwa.gov.tw/V8/C/)"
    return result
