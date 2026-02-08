from flask import Flask, request, jsonify
import swisseph as swe
import datetime

app = Flask(__name__)

def get_rashi_logic(dob, tob):
    y, m, d = map(int, dob.split('-'))
    h, mn = map(int, tob.split(':'))
    dt = datetime.datetime(y, m, d, h, mn) - datetime.timedelta(hours=5, minutes=30)
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0)
    res, ret = swe.calc_ut(jd, swe.MOON)
    longitude = res[0]
    rashi_names = ["Mesh", "Vrishabh", "Mithun", "Kark", "Singh", "Kanya", "Tula", "Vrishchik", "Dhanu", "Makar", "Kumbh", "Meen"]
    rashi_idx = int(longitude / 30)
    return rashi_names[rashi_idx]

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # अगर URL में 'calculate' शब्द है, तो कैलकुलेशन करो
    if 'calculate' in path or request.args.get('dob'):
        dob = request.args.get('dob')
        tob = request.args.get('tob')
        
        if not dob or not tob:
            return jsonify({"error": "Missing params. Use ?dob=YYYY-MM-DD&tob=HH:MM"}), 400
            
        try:
            rashi = get_rashi_logic(dob, tob)
            return jsonify({
                "status": "success",
                "rashi": rashi
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # वरना होम पेज का मैसेज दिखाओ
    return "Astro API is Live! Use /calculate?dob=YYYY-MM-DD&tob=HH:MM"

if __name__ == "__main__":
    app.run()
