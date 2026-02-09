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

    # 2. ग्रहों की गणना (पुराना लॉजिक बरकरार)
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

    # --- 🆕 विस्तृत पंचांग सिस्टम (Full Detailed Section) ---
    sun_deg = planets_data["Sun"]["abs_degree"]
    moon_deg = planets_data["Moon"]["abs_degree"]

    # 1. तिथि (Tithi)
    diff = (moon_deg - sun_deg + 360) % 360
    tithi_no = int(diff / 12) + 1
    tithi_names = ["Prathama", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima", 
                   "Prathama (K)", "Dwitiya (K)", "Tritiya (K)", "Chaturthi (K)", "Panchami (K)", "Shashthi (K)", "Saptami (K)", "Ashtami (K)", "Navami (K)", "Dashami (K)", "Ekadashi (K)", "Dwadashi (K)", "Trayodashi (K)", "Chaturdashi (K)", "Amavasya"]
    
    # 2. नक्षत्र (Nakshatra)
    nak_names = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
    nakshatra_no = int(moon_deg / (360/27)) + 1

    # 3. योग (Yoga)
    yoga_deg = (sun_deg + moon_deg) % 360
    yoga_no = int(yoga_deg / (360/27)) + 1
    yoga_names = ["Vishkumbha", "Preeti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma", "Dhriti", "Shoola", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"]

    # 4. करण (Karana)
    karana_no = int(diff / 6) + 1
    karana_names = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti", "Shakuni", "Chatushpada", "Nagava", "Kinstughna"]

    # पंचांग डेटा में ये दो लाइनें जोड़ें (बाकी कोड वैसा ही रहने दें)
    panchang_data = {
        "tithi": tithi_names[(tithi_no - 1) % 30],
        "nakshatra": nak_names[nakshatra_no - 1],
        "yoga": yoga_names[(yoga_no - 1) % 27],
        "karana": karana_names[(karana_no - 1) % 11],
        "paksha": "Shukla Paksha" if tithi_no <= 15 else "Krishna Paksha",
        "day": dt_local.strftime('%A'),
        # --- ये दो लाइनें पक्का जोड़ें ---
        "rahukaal": f"{format_muhurat(r_start_dec)} - {format_muhurat(r_start_dec + (day_duration / 8))}",
        "abhijit": f"{format_muhurat(sunrise_dec + (day_duration/15)*7)} - {format_muhurat(sunrise_dec + (day_duration/15)*8)}",
        # ---------------------------
        "sunrise": format_muhurat(sunrise_dec),
        "sunset": format_muhurat(sunset_dec),
        "sun_sign": rashi_names[int(sun_deg/30)],
        "moon_sign": rashi_names[int(moon_deg/30)]
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
    return "Tapvaani Full Detailed Panchang API is Live!"

app = app
