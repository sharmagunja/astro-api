from flask import Flask, request, jsonify
import swisseph as swe
import datetime

app = Flask(__name__)

# लाहिरी अयनांश सेट करने के लिए (यह भारतीय ज्योतिष के लिए जरूरी है)
swe.set_ephe_path('/usr/share/ephe') # Default path
swe.set_sid_mode(swe.SIDM_LAHIRI)

def get_rashi_logic(dob, tob):
    y, m, d = map(int, dob.split('-'))
    h, mn = map(int, tob.split(':'))
    
    # समय को UTC में बदलना (India is UTC+5:30)
    # 06:30 IST = 01:00 UTC
    dt = datetime.datetime(y, m, d, h, mn) - datetime.timedelta(hours=5, minutes=30)
    
    # जूलियन डे कैलकुलेशन
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0)
    
    # चंद्रमा की स्थिति (Siderial Mode में)
    # flag = swe.FLG_SIDEREAL | swe.FLG_SWIEPH
    res, ret = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)
    longitude = res[0]
    
    rashi_names = ["Mesh", "Vrishabh", "Mithun", "Kark", "Singh", "Kanya", "Tula", "Vrishchik", "Dhanu", "Makar", "Kumbh", "Meen"]
    rashi_idx = int(longitude / 30)
    return rashi_names[rashi_idx]

@app.route('/calculate')
def calculate():
    dob = request.args.get('dob')
    tob = request.args.get('tob')
    try:
        rashi = get_rashi_logic(dob, tob)
        return jsonify({"status": "success", "rashi": rashi})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/')
def home():
    return "Astro API Live"
