import os
import json
import requests
from requests.auth import HTTPBasicAuth

# ตั้งค่ากรอบเขตเริ่มต้น (ครอบคลุมกรุงเทพฯ และปริมณฑลแบบกว้าง)
CENTER_LAT = 13.893106
CENTER_LON = 100.613921
RADAR_RANGE = 1.5  # ขยายขอบเขตเริ่มต้นให้กว้างขึ้นเผื่อการย้ายพิกัด

LAMIN = CENTER_LAT - RADAR_RANGE
LAMAX = CENTER_LAT + RADAR_RANGE
LOMIN = CENTER_LON - RADAR_RANGE
LOMAX = CENTER_LON + RADAR_RANGE

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
                
                icao24 = state[0] or "N/A"
                origin_country = state[2] or "N/A"
                baro_altitude = state[7]
                on_ground = state[8]
                velocity = state[9] or 0.0
                heading = state[10] or 0.0
                vertical_rate = state[11] or 0.0
                squawk = state[14] or "N/A"
                
                flights.append({
                    "callsign": callsign,
                    "icao24": icao24,
                    "country": origin_country,
                    "lon": lon,
                    "lat": lat,
                    "alt": baro_altitude if baro_altitude is not None else 0.0,
                    "speed": velocity,
                    "heading": heading,
                    "vertical_rate": vertical_rate,
                    "on_ground": on_ground,
                    "squawk": squawk
                })
        
        with open('flights.json', 'w') as f:
            json.dump(flights, f)
        print(f"Flights updated successfully. Found {len(flights)} planes.")
    except Exception as e:
        print(f"Error updating flights: {e}")

if __name__ == "__main__":
    update_weather()
    update_flights()
