from flask import Flask, request, jsonify
import swisseph as swe
import datetime

app = Flask(__name__)

# लाहिरी अयनांश सेट करना
swe.set_sid_mode(swe.SIDM_LAHIRI)

def get_complete_chart(dob, tob, lat=28.6139, lon=77.2090):
    y, m, d = map(int, dob.split('-'))
    h, mn = map(int, tob.split(':'))
    
    # IST to UTC (-5:30)
    dt = datetime.datetime(y, m, d, h, mn) - datetime.timedelta(hours=5, minutes=30)
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0)
    
    # 1. लग्न (Ascendant) की गणना
    res_houses, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    lagna_degree = ascmc[0]
    lagna_rashi_no = int(lagna_degree / 30) + 1

    # 2. पूरे 9 ग्रहों की लिस्ट (Correct IDs)
    # 0=Sun, 1=Moon, 2=Mercury, 3=Venus, 4=Mars, 5=Jupiter, 6=Saturn, 10=Rahu
    # केतु को हम 180 डिग्री के गणित से ही निकालेंगे क्योंकि वो सबसे सटीक होता है
    planet_map = {
        "Sun": 0, 
        "Moon": 1, 
        "Mercury": 2, 
        "Venus": 3, 
        "Mars": 4, 
        "Jupiter": 5, 
        "Saturn": 6, 
        "Rahu": 10
    }

    planets_data = {}
    rashi_names = ["Mesh", "Vrishabh", "Mithun", "Kark", "Singh", "Kanya", "Tula", "Vrishchik", "Dhanu", "Makar", "Kumbh", "Meen"]

    # पहले 8 ग्रहों की गणना
    for name, p_id in planet_map.items():
        res, ret = swe.calc_ut(jd, p_id, swe.FLG_SIDEREAL)
        deg = res[0]
        rashi_no = int(deg / 30) + 1
        house = ((rashi_no - lagna_rashi_no + 12) % 12) + 1
        planets_data[name] = {
            "rashi_no": rashi_no,
            "rashi_name": rashi_names[rashi_no-1],
            "degree": round(deg % 30, 2),
            "house": house
        }

    # 3. नौवां ग्रह: केतु (Ketu) - राहु के ठीक सामने
    rahu_abs_deg = (planets_data["Rahu"]["rashi_no"] - 1) * 30 + planets_data["Rahu"]["degree"]
    ketu_abs_deg = (rahu_abs_deg + 180) % 360
    ketu_rashi_no = int(ketu_abs_deg / 30) + 1
    planets_data["Ketu"] = {
        "rashi_no": ketu_rashi_no,
        "rashi_name": rashi_names[ketu_rashi_no-1],
        "degree": round(ketu_abs_deg % 30, 2),
        "house": ((ketu_rashi_no - lagna_rashi_no + 12) % 12) + 1
    }

    return {
        "lagna": lagna_rashi_no,
        "lagna_name": rashi_names[lagna_rashi_no-1],
        "moon_rashi": planets_data["Moon"]["rashi_name"],
        "planets": planets_data # अब इसमें पूरे 9 ग्रह हैं!
    }

@app.route('/calculate')
def calculate():
    dob = request.args.get('dob')
    tob = request.args.get('tob')
    lat = float(request.args.get('lat', 28.6139))
    lon = float(request.args.get('lon', 77.2090))
    try:
        data = get_complete_chart(dob, tob, lat, lon)
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/')
def home():
    return "Tapvaani 9-Planet Astro API is Live!"

app = app
