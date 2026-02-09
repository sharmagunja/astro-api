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
    dt_local = datetime.datetime(y, m, d, h, mn)
    dt_utc = dt_local - datetime.timedelta(hours=5, minutes=30)
    
    # --- 🛠️ ERROR FIX: float object cannot be interpreted as integer ---
    # यहाँ int() का प्रयोग किया गया है ताकि swe.julday एरर न दे
    jd = swe.julday(int(dt_utc.year), int(dt_utc.month), int(dt_utc.day), h + mn/60.0 - 5.5)
    
    # 1. लग्न (Ascendant) की गणना
    res_houses, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    lagna_degree = ascmc[0]
    lagna_rashi_no = int(lagna_degree / 30) + 1

    # 2. ग्रहों की गणना
    planet_map = {"Sun": 0, "Moon": 1, "Mercury": 2, "Venus": 3, "Mars": 4, "Jupiter": 5, "Saturn": 6, "Rahu": 10}
    planets_data = {}
    rashi_names = ["Mesh", "Vrishabh", "Mithun", "Kark", "Singh", "Kanya", "Tula", "Vrishchik", "Dhanu", "Makar", "Kumbh", "Meen"]

    for name, p_id in planet_map.items():
        res, ret = swe.calc_ut(jd, p_id, swe.FLG_SIDEREAL)
        deg = res[0]
        rashi_no = int(deg / 30) + 1
        house = ((rashi_no - lagna_rashi_no + 12) % 12) + 1
        planets_data[name] = {
            "rashi_no": rashi_no,
            "rashi_name": rashi_names[rashi_no-1],
            "degree": round(deg % 30, 2),
            "house": house,
            "abs_degree": deg 
        }

    # केतु की गणना
    rahu_abs_deg = planets_data["Rahu"]["abs_degree"]
    ketu_abs_deg = (rahu_abs_deg + 180) % 360
    ketu_rashi_no = int(ketu_abs_deg / 30) + 1
    planets_data["Ketu"] = {
        "rashi_no": ketu_rashi_no,
        "rashi_name": rashi_names[ketu_rashi_no-1],
        "degree": round(ketu_abs_deg % 30, 2),
        "house": ((ketu_rashi_no - lagna_rashi_no + 12) % 12) + 1
    }

    # --- विस्तृत पंचांग सिस्टम (Lists Unchanged) ---
    sun_deg = planets_data["Sun"]["abs_degree"]
    moon_deg = planets_data["Moon"]["abs_degree"]

    diff = (moon_deg - sun_deg + 360) % 360
    tithi_no = int(diff / 12) + 1
    tithi_names = ["Prathama", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima", 
                   "Prathama (K)", "Dwitiya (K)", "Tritiya (K)", "Chaturthi (K)", "Panchami (K)", "Shashthi (K)", "Saptami (K)", "Ashtami (K)", "Navami (K)", "Dashami (K)", "Ekadashi (K)", "Dwadashi (K)", "Trayodashi (K)", "Chaturdashi (K)", "Amavasya"]
    
    nak_names = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
    nakshatra_no = int(moon_deg / (360/27)) + 1

    yoga_deg = (sun_deg + moon_deg) % 360
    yoga_no = int(yoga_deg / (360/27)) + 1
    yoga_names = ["Vishkumbha", "Preeti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma", "Dhriti", "Shoola", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"]

    karana_names = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti", "Shakuni", "Chatushpada", "Nagava", "Kinstughna"]
    karana_no = int(diff / 6) + 1

    # --- 🆕 NO HARDCODING: Dynamic Muhurat Logic ---
    res_rise = swe.rise_trans(jd, 0, lon, lat, 0, swe.CALC_RISE)[1]
    res_set = swe.rise_trans(jd, 0, lon, lat, 0, swe.CALC_SET)[1]
    
    sunrise_dec = ((res_rise - jd) * 24) + (h + mn/60.0)
    sunset_dec = ((res_set - jd) * 24) + (h + mn/60.0)
    day_duration = sunset_dec - sunrise_dec

    weekday = dt_local.weekday()
    rahu_parts = {0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3, 6: 8}
    r_start_dec = sunrise_dec + (rahu_parts[weekday] - 1) * (day_duration / 8)

    def format_muhurat(dec_h):
        dec_h = dec_h % 24
        hr = int(dec_h)
        mi = int((dec_h % 1) * 60)
        suffix = 'AM' if hr < 12 else 'PM'
        display_h = hr if hr <= 12 else hr - 12
        if display_h == 0: display_h = 12
        return f"{display_h:02d}:{mi:02d} {suffix}"

    panchang_data = {
        "tithi": tithi_names[(tithi_no - 1) % 30],
        "nakshatra": nak_names[nakshatra_no - 1],
        "yoga": yoga_names[yoga_no - 1],
        "karana": karana_names[(karana_no - 1) % 11],
        "paksha": "Shukla Paksha" if tithi_no <= 15 else "Krishna Paksha",
        "day": dt_local.strftime('%A'),
        "rahukaal": f"{format_muhurat(r_start_dec)} - {format_muhurat(r_start_dec + (day_duration / 8))}",
        "abhijit": f"{format_muhurat(sunrise_dec + (day_duration/15)*7)} - {format_muhurat(sunrise_dec + (day_duration/15)*8)}",
        "sun_sign": rashi_names[int(sun_deg/30)],
        "moon_sign": rashi_names[int(moon_deg/30)],
        "sunrise": format_muhurat(sunrise_dec),
        "sunset": format_muhurat(sunset_dec)
    }

    return {
        "lagna": lagna_rashi_no,
        "lagna_name": rashi_names[lagna_rashi_no-1],
        "moon_rashi": planets_data["Moon"]["rashi_name"],
        "planets": planets_data,
        "panchang": panchang_data
    }

@app.route('/calculate')
def calculate():
    dob = request.args.get('dob')
    tob = request.args.get('tob', '12:00')
    lat = float(request.args.get('lat', 28.6139))
    lon = float(request.args.get('lon', 77.2090))
    try:
        data = get_complete_chart(dob, tob, lat, lon)
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/')
def home():
    return "Tapvaani Full Detailed Panchang API is Live!"

app = app
