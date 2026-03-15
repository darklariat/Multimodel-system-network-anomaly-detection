import time
import joblib
import logging
import datetime
import threading
import subprocess
import pandas as pd
from queue import Queue, Empty
from xgboost import XGBClassifier
from flask import Flask, request, jsonify

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

results_queue = Queue()

def create_flask_app():
    label_encoder = joblib.load("C:/Internship/One for all/Anomaly/label_encoder.pkl")
    model = XGBClassifier()
    model.load_model("C:/Internship/One for all/Anomaly/xgb_model.json")

    app = Flask(__name__)

    @app.route('/flows', methods=['POST'])
    def receive_flow():
        try:
            flow_data = request.get_json(force=True)

            df = pd.DataFrame([flow_data])
            drop_cols = ['src_ip', 'dst_ip', 'src_port', 'protocol', 'timestamp']
            df = df.drop(columns=[col for col in drop_cols if col in df.columns], errors='ignore')

            prediction = model.predict(df)[0]
            result = label_encoder.inverse_transform([prediction])[0]

            results_queue.put((result, datetime.datetime.now().strftime('%H:%M:%S')))

            return jsonify({"status": "success", "prediction": result}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    return app

def start_cicflowmeter():
    command = [
        "cicflowmeter",
        "-i", "WiFi",
        "-u", "http://localhost:5000/flows"
    ]
    subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def start_server():
    app = create_flask_app()
    flask_thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000))
    flask_thread.daemon = True
    flask_thread.start()

    time.sleep(1)
    start_cicflowmeter()

def get_prediction():
    found_non_benign = None
    while not results_queue.empty():
        try:
            result = results_queue.get_nowait()

            if isinstance(result, tuple):
                result = result[0]

            if result != "BENIGN" and result != "_" and result.strip():
                found_non_benign = result
        except Empty:
            break

    if found_non_benign:
        return found_non_benign, datetime.datetime.now().strftime('%H:%M:%S')
    else:
        return "BENIGN", datetime.datetime.now().strftime('%H:%M:%S')