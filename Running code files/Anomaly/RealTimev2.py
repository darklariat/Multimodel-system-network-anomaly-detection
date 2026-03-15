import time
import joblib
import logging
import datetime
import threading
import subprocess
import pandas as pd
from xgboost import XGBClassifier
from flask import Flask, request, jsonify

#log = logging.getLogger('werkzeug')
#log.setLevel(logging.ERROR)

model = XGBClassifier()
model.load_model("C:/Internship/NetSleuth/Anomaly/models/xgb_model.json")
scaler = joblib.load("C:/Internship/NetSleuth/Anomaly/models/scaler.pkl")

app = Flask(__name__)


received_flows = []

def start_cicflowmeter():
    command = [
        "cicflowmeter",
        "-i", "Ethernet 2",
        "-u", "http://localhost:5000/flows"
    ]
    subprocess.Popen(command)

@app.route('/flows', methods=['POST'])
def receive_flow():
    try:
        flow_data = request.get_json(force=True)
        received_flows.append(flow_data)

        df = pd.DataFrame([flow_data])
        
        df = df.drop(['src_ip', 'dst_ip', 'timestamp'], axis=1)
        '''
        selectied_columns = [
            "flow_duration",
            "tot_fwd_pkts",
            "tot_bwd_pkts",
            "totlen_fwd_pkts",
            "totlen_bwd_pkts",
            "flow_byts_s",
            "flow_pkts_s",
            "pkt_len_mean",
            "fwd_pkt_len_mean",
            "bwd_pkt_len_mean",
            "Label"
        ]
        df = df[selectied_columns]
        '''
        df_scaled = scaler.transform(df)

        predictions = model.predict(df_scaled)
        probabilities = model.predict_proba(df)
        confidence_scores = probabilities.max(axis=1)
        
        output = [
            ['Anomaly' if (predictions == 1) else 'Normal', round(float(score), 4)]
            for pred, score in zip(predictions, confidence_scores)
        ]

        print(output, datetime.datetime.now().strftime('%H:%M:%S'))
        return jsonify({"status": "success", "predictions": output}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/stats', methods=['GET'])
def get_stats():
    return jsonify({"total_flows_received": len(received_flows)})

def run_flask():
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    time.sleep(1)

    start_cicflowmeter()

    while True:
        time.sleep(60)