from flask import Flask, request, jsonify
import swisseph as swe
import datetime

app = Flask(__name__)

# लाहिरी अयनांश (Lahiri Ayanamsa) सेट करना
swe.set_sid_mode(swe.SIDM_LAHIRI)

def get_complete_chart(dob, tob, lat=28.6139, lon=77.2090):
    y, m, d = map(int, dob.split('-'))
    h, mn = map(int, tob.split(':'))
    
    # IST to UTC (-5:30)
    dt = datetime.datetime(y, m, d, h, mn) - datetime.timedelta(hours=5, minutes=30)
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0)
    
    # 1. लग्न (Ascendant) की गणना
    # 'P' for Placidus house system (Common in India)
    res_houses, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    lagna_degree = ascmc[0]
    lagna_rashi_no = int(lagna_degree / 30) + 1

    # 2. ग्रहों की लिस्ट
    planet_map = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS, "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_RAHU
    }

    planets_data = {}
    rashi_names = ["Mesh", "Vrishabh", "Mithun", "Kark", "Singh", "Kanya", "Tula", "Vrishchik", "Dhanu", "Makar", "Kumbh", "Meen"]

    for name, id in planet_map.items():
        res, ret = swe.calc_ut(jd, id, swe.FLG_SIDEREAL)
        deg = res[0]
        rashi_no = int(deg / 30) + 1
        # भाव (House) निकालना - लग्न के सापेक्ष
        house = ((rashi_no - lagna_rashi_no + 12) % 12) + 1
        planets_data[name] = {
            "rashi_no": rashi_no,
            "rashi_name": rashi_names[rashi_no-1],
            "degree": round(deg % 30, 2),
            "house": house
        }

    # 3. केतु (Ketu) हमेशा राहु के 180 डिग्री सामने होता है
    rahu_deg = planets_data["Rahu"]["degree"] + ((planets_data["Rahu"]["rashi_no"]-1) * 30)
    ketu_total_deg = (rahu_deg + 180) % 360
    ketu_rashi_no = int(ketu_total_deg / 30) + 1
    planets_data["Ketu"] = {
        "rashi_no": ketu_rashi_no,
        "rashi_name": rashi_names[ketu_rashi_no-1],
        "degree": round(ketu_total_deg % 30, 2),
        "house": ((ketu_rashi_no - lagna_rashi_no + 12) % 12) + 1
    }

    return {
        "lagna": lagna_rashi_no,
        "lagna_name": rashi_names[lagna_rashi_no-1],
        "moon_rashi": planets_data["Moon"]["rashi_name"],
        "planets": planets_data
    }

@app.route('/calculate')
def calculate():
    dob = request.args.get('dob')
    tob = request.args.get('tob')
    # डिफ़ॉल्ट दिल्ली का Lat/Lon, वर्डप्रेस से भेजेंगे तो वो लेगा
    lat = float(request.args.get('lat', 28.6139))
    lon = float(request.args.get('lon', 77.2090))
    
    try:
        data = get_complete_chart(dob, tob, lat, lon)
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run()
