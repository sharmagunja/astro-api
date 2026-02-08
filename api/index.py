from flask import Flask, request, jsonify
from flask_cors import CORS
import swisseph as swe
import datetime

app = Flask(__name__)
CORS(app)

@app.route('/calculate', methods=['GET'])
def calculate():
    # डेटा लेना: ?dob=1979-06-17&tob=06:30&lat=23.95&lon=86.81
    dob = request.args.get('dob')
    tob = request.args.get('tob')
    lat = float(request.args.get('lat', 23.95))
    lon = float(request.args.get('lon', 86.81))

    y, m, d = map(int, dob.split('-'))
    h, mn = map(int, tob.split(':'))
    
    # UTC समय में बदलना (IST - 5:30)
    dt = datetime.datetime(y, m, d, h, mn) - datetime.timedelta(hours=5, minutes=30)
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0)
    
    # चंद्रमा की गणना (Moon = 1)
    res, ret = swe.calc_ut(jd, swe.MOON)
    longitude = res[0]
    
    # राशि निकालना (360 / 30 = 12)
    rashi_names = ["Mesh", "Vrishabh", "Mithun", "Kark", "Singh", "Kanya", "Tula", "Vrishchik", "Dhanu", "Makar", "Kumbh", "Meen"]
    rashi_idx = int(longitude / 30)
    
    return jsonify({
        "longitude": longitude,
        "rashi": rashi_names[rashi_idx],
        "dob": dob,
        "status": "success"
    })

if __name__ == '__main__':
    app.run()
