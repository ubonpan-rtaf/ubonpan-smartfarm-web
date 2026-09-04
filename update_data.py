import os
import json
import requests
from requests.auth import HTTPBasicAuth

# 1. ตั้งค่าพิกัดศูนย์กลางและรัศมี (สะพานใหม่ / ดอนเมือง)
CENTER_LAT = 13.893106
CENTER_LON = 100.613921
RADAR_RANGE = 0.5

LAMIN = CENTER_LAT - RADAR_RANGE
LAMAX = CENTER_LAT + RADAR_RANGE
LOMIN = CENTER_LON - RADAR_RANGE
LOMAX = CENTER_LON + RADAR_RANGE

# ดึงรหัสผ่านจาก GitHub Secrets
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
OPENSKY_USER = os.getenv('OPENSKY_USER')
OPENSKY_PASS = os.getenv('OPENSKY_PASS')

def update_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?lat=13.912300&lon=100.620000&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        weather_json = {
            "temp": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "hum": data["main"]["humidity"],
            "wind": data["wind"]["speed"],
            "pressure": data["main"]["pressure"],
            "clouds": data["clouds"]["all"],
            "visibility": data.get("visibility", 10000),
            "desc": data["weather"][0]["main"].upper(),
            "id": data["weather"][0]["id"]
        }
        
        with open('weather.json', 'w') as f:
            json.dump(weather_json, f)
        print("Weather updated successfully.")
    except Exception as e:
        print(f"Error updating weather: {e}")

def update_flights():
    url = f"https://opensky-network.org/api/states/all?lamin={LAMIN}&lomin={LOMIN}&lamax={LAMAX}&lomax={LOMAX}"
    try:
        response = requests.get(url, auth=HTTPBasicAuth(OPENSKY_USER, OPENSKY_PASS), timeout=10)
        data = response.json()
        
        flights = []
        if data and 'states' in data and data['states'] is not None:
            for state in data['states']:
                lon, lat = state[5], state[6]
                if lon is None or lat is None:
                    continue
                    
                callsign = str(state[1]).strip() if state[1] else "N/A"
                if callsign == "": callsign = "N/A"
                
                flights.append({
                    "callsign": callsign,
                    "lon": lon,
                    "lat": lat,
                    "alt": state[7] or 0.0,
                    "speed": state[9] or 0.0
                })
        
        with open('flights.json', 'w') as f:
            json.dump(flights, f)
        print(f"Flights updated successfully. Found {len(flights)} planes.")
    except Exception as e:
        print(f"Error updating flights: {e}")

if __name__ == "__main__":
    update_weather()
    update_flights()
