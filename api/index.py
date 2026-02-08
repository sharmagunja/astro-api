from flask import Flask, request, jsonify
import swisseph as swe
import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return "Astro API is Running! Use /calculate?dob=YYYY-MM-DD&tob=HH:MM"

@app.route('/calculate')
def calculate():
    try:
        dob = request.args.get('dob')
        tob = request.args.get('tob')
        
        if not dob or not tob:
            return jsonify({"error": "Missing parameters"}), 400

        y, m, d = map(int, dob.split('-'))
        h, mn = map(int, tob.split(':'))
        
        # IST to UTC (IST - 5:30)
        dt = datetime.datetime(y, m, d, h, mn) - datetime.timedelta(hours=5, minutes=30)
        jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0)
        
        # Moon Calculation
        res, ret = swe.calc_ut(jd, swe.MOON)
        longitude = res[0]
        
        rashi_names = ["Mesh", "Vrishabh", "Mithun", "Kark", "Singh", "Kanya", "Tula", "Vrishchik", "Dhanu", "Makar", "Kumbh", "Meen"]
        rashi_idx = int(longitude / 30)
        
        return jsonify({
            "status": "success",
            "rashi": rashi_names[rashi_idx],
            "longitude": longitude
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel के लिए यह जरूरी है
def handler(event, context):
    return app(event, context)
