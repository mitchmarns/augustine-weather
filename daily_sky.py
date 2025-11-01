import requests, datetime, os

# ------------- SETTINGS -------------
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
LAT, LON = 40.70, -77.60      
CITY_NAME = "Augustine"
# -----------------------------------

# --- Weather from Open-Meteo (free, no key) ---
resp = requests.get(
    f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}"
    "&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
    "precipitation,weather_code,wind_speed_10m&timezone=auto"
)
resp.raise_for_status()
w = resp.json()["current"]

temp_c = float(w["temperature_2m"])
feels_c = float(w["apparent_temperature"])
hum = int(w["relative_humidity_2m"])
wind_mps = float(w["wind_speed_10m"])
wind_mph = wind_mps * 2.237
code = int(w["weather_code"])

# --- Weather code → emoji + label (Open-Meteo codes) ---
def sky_from_code(c: int):
    if c == 0: return "☀️", "clear sky"
    if c in (1,): return "🌤️", "mostly clear"
    if c in (2,): return "⛅", "partly cloudy"
    if c in (3,): return "☁️", "overcast"
    if c in (45, 48): return "🌫️", "fog"
    if c in (51, 53, 55): return "🌦️", "drizzle"
    if c in (56, 57): return "🥶🌧️", "freezing drizzle"
    if c in (61, 63, 65): return "🌧️", "rain"
    if c in (66, 67): return "🥶🌧️", "freezing rain"
    if c in (71, 73, 75): return "🌨️", "snow"
    if c in (77,): return "🌨️", "snow grains"
    if c in (80, 81, 82): return "🌦️", "rain showers"
    if c in (85, 86): return "🌨️", "snow showers"
    if c in (95,): return "⛈️", "thunderstorm"
    if c in (96, 99): return "⛈️🧊", "thunderstorm w/ hail"
    return "🌤️", "conditions"

sky_emoji, sky_label = sky_from_code(code)

# --- Simple moon phase calc (Conway-style approx) ---
today = datetime.date.today()
yy, mm, dd = today.year, today.month, today.day
r = yy % 100
r %= 19
if r > 9: r -= 19
r = ((r * 11) % 30) + mm + dd
if mm < 3: r += 2
phase_index = (r + 2 - yy // 100 + yy // 400) % 30  # 0..29
illum = round(phase_index / 29.53 * 100)

phase_buckets = [
    "🌑 New Moon", "🌒 Waxing Crescent", "🌓 First Quarter",
    "🌔 Waxing Gibbous", "🌕 Full Moon", "🌖 Waning Gibbous",
    "🌗 Last Quarter", "🌘 Waning Crescent"
]
moon_name = phase_buckets[int(phase_index / 3.7)]  # rough 8-phase bucket

# --- Werewolf lore note (based on current phase) ---
lower = moon_name.lower()
notes = []

# global behaviors
if "waning crescent" in lower or "new moon" in lower or "waxing crescent" in lower:
    notes.append("Many avoid going out after sundown between **Third Quarter → First Quarter** (around the new moon).")

# specific states
if "full moon" in lower:
    notes.append("**Full moon tonight:** the shift is **unavoidable** and **painful** (born wolves endure it best).")
elif "waxing gibbous" in lower:
    notes.append("**Waxing gibbous:** most **ill-tempered**; lead-up to the full moon brings moodiness and restlessness.")
elif "waning gibbous" in lower:
    notes.append("**Waning gibbous:** most **physically & emotionally exhausted** after the full moon.")
elif "new moon" in lower:
    notes.append("**New moon:** calmest period. Only time new wolves can be created via an **alpha** bite; other bites leave a mark but don’t pass the curse.")

werewolf_note = "\n".join(notes) if notes else "Wolves feel the lunar pull; phases influence mood, stamina, and control."

# --- Build embed ---
desc = (
    f"{sky_emoji} **{sky_label.title()}**\n"
    f"**{temp_c:.0f}°C / {(temp_c*9/5+32):.0f}°F**, "
    f"feels {feels_c:.0f}°C / {(feels_c*9/5+32):.0f}°F\n"
    f"💨 {wind_mph:.0f} mph · 💧{hum}% humidity"
)

embed = {
    "title": f"{CITY_NAME} · Weather & Moon",
    "description": desc,
    "color": 0x393b8c,
    "fields": [
        {"name": "Moon", "value": f"{moon_name} ({illum}% lit)", "inline": True},
        {"name": "Werewolf", "value": werewolf_note, "inline": False}
    ],
    "timestamp": datetime.datetime.utcnow().isoformat()
}

payload = {"username": "Kismet · Sky Watch", "embeds": [embed]}
res = requests.post(WEBHOOK_URL, json=payload, timeout=20)
print("Status:", res.status_code, res.text[:200])
