from flask import Flask, request, jsonify
import swisseph as swe
import datetime

app = Flask(__name__)

# पंचांग गणना फंक्शन
def get_rashi(dob, tob):
    y, m, d = map(int, dob.split('-'))
    h, mn = map(int, tob.split(':'))
    
    # IST to UTC conversion
    dt = datetime.datetime(y, m, d, h, mn) - datetime.timedelta(hours=5, minutes=30)
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0)
    
    # Moon longitude calculation
    res, ret = swe.calc_ut(jd, swe.MOON)
    longitude = res[0]
    
    rashi_names = ["Mesh", "Vrishabh", "Mithun", "Kark", "Singh", "Kanya", "Tula", "Vrishchik", "Dhanu", "Makar", "Kumbh", "Meen"]
    rashi_idx = int(longitude / 30)
    return rashi_names[rashi_idx]

@app.route('/')
def home():
    return "Astro API is Live!"

@app.route('/calculate')
def calculate():
    dob = request.args.get('dob')
    tob = request.args.get('tob')
    
    if not dob or not tob:
        return jsonify({"error": "Missing parameters"}), 400
        
    try:
        rashi = get_rashi(dob, tob)
        return jsonify({
            "status": "success",
            "rashi": rashi
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel के लिए इसे 'app' ही रहने दें
