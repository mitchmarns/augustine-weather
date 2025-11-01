import requests, datetime, math, json, os

# ------------- SETTINGS -------------
WEBHOOK_URL = "https://discord.com/api/webhooks/XXX/YYY"
LAT, LON = 43.7, -79.4     # your location (Toronto example)
CITY_NAME = "Augustine Heights"
# -----------------------------------

# --- Weather from Open-Meteo (free, no key) ---
w = requests.get(
    f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}"
    "&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
    "precipitation,weather_code,wind_speed_10m&timezone=auto"
).json()["current"]
temp, feels, hum, wind = w["temperature_2m"], w["apparent_temperature"], w["relative_humidity_2m"], w["wind_speed_10m"]

# --- Simple moon phase calc (algorithm by John Conway) ---
today = datetime.date.today()
yy, mm, dd = today.year, today.month, today.day
r = yy % 100
r %= 19
if r>9: r -= 19
r = ((r * 11) % 30) + mm + dd
if mm<3: r += 2
phase = (r + 2 - yy//100 + yy//400) % 30
illum = round(phase / 29.53 * 100)
names = [
    "🌑 New Moon","🌒 Waxing Crescent","🌓 First Quarter",
    "🌔 Waxing Gibbous","🌕 Full Moon","🌖 Waning Gibbous",
    "🌗 Last Quarter","🌘 Waning Crescent"
]
moon_name = names[ int(phase/3.7) ]

# --- Make embed ---
embed = {
  "title": f"{CITY_NAME} · Weather & Moon",
  "description": f"**{temp:.0f}°C**, feels {feels:.0f}°C\n💨 {wind:.0f} m/s · 💧{hum}% humidity",
  "color": 0x393b8c,
  "fields": [
    {"name":"Moon","value":f"{moon_name} ({illum}% lit)", "inline":True}
  ],
  "timestamp": datetime.datetime.utcnow().isoformat()
}

payload = {"username":"Kismet · Sky Watch","embeds":[embed]}
r = requests.post(WEBHOOK_URL, json=payload)
print("Status:", r.status_code)
