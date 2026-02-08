from flask import Flask, request, jsonify
import swisseph as swe
import datetime

app = Flask(__name__)

# पंचांग गणना फंक्शन
def get_rashi_logic(dob, tob):
    y, m, d = map(int, dob.split('-'))
    h, mn = map(int, tob.split(':'))
    
    # IST to UTC (IST - 5:30)
    dt = datetime.datetime(y, m, d, h, mn) - datetime.timedelta(hours=5, minutes=30)
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0)
    
    # Moon longitude calculation
    res, ret = swe.calc_ut(jd, swe.MOON)
    longitude = res[0]
    
    rashi_names = ["Mesh", "Vrishabh", "Mithun", "Kark", "Singh", "Kanya", "Tula", "Vrishchik", "Dhanu", "Makar", "Kumbh", "Meen"]
    rashi_idx = int(longitude / 30)
    return rashi_names[rashi_idx]

# यह रूट होम पेज और कैलकुलेट दोनों को संभालेगा
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if path == 'calculate':
        dob = request.args.get('dob')
        tob = request.args.get('tob')
        
        if not dob or not tob:
            return jsonify({"error": "Date (dob) or Time (tob) missing"}), 400
            
        try:
            rashi = get_rashi_logic(dob, tob)
            return jsonify({
                "status": "success",
                "rashi": rashi,
                "input": {"dob": dob, "tob": tob}
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return "Astro API is Live! Use /calculate?dob=YYYY-MM-DD&tob=HH:MM"

# Vercel के लिए जरूरी
if __name__ == "__main__":
    app.run()
