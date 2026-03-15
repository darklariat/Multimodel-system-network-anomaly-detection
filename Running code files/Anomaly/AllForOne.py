import subprocess
import time
import pandas as pd
import joblib
from collections import Counter
from xgboost import XGBClassifier

# -------- CONFIG --------
CAPTURE_FILE = "capture.pcap"
FLOW_CSV = "flows.csv"
CAPTURE_DURATION = 60  # seconds

MODEL_PATH = "models/xgb_multiclass_model.json"
SCALER_PATH = "models/scaler.pkl"
LABEL_ENCODER_PATH = "models/label_encoder.pkl"
# ------------------------

def capture_with_tshark(duration, output_file):
    print(f"[+] Capturing packets with tshark for {duration} seconds...")
    cmd = [
        "tshark",
        "-a", f"duration:{duration}",
        "-w", output_file,
        "-F", "pcap"
        
    ]
    subprocess.run(cmd, check=True)
    print(f"[+] Capture saved to {output_file}")

def run_cicflowmeter(input_pcap, output_csv):
    print("[+] Running CICFlowMeter (Python)...")
    cmd = [
        "cicflowmeter",
        "-f", input_pcap,
        "-c", output_csv
    ]
    subprocess.run(cmd, check=True)
    print(f"[+] Flows saved to {output_csv}")

def predict_attacks(flow_csv, model_path, scaler_path, le_path):
    print(f"[+] Loading model and preprocessing tools...")
    model = XGBClassifier()
    model.load_model(model_path)
    scaler = joblib.load(scaler_path)
    label_encoder = joblib.load(le_path)

    df = pd.read_csv(flow_csv)

    # Drop only required columns
    df = df.drop(['src_ip', 'dst_ip', 'timestamp'], axis=1, errors='ignore')

    features_scaled = scaler.transform(df)

    print("[+] Predicting...")
    preds = model.predict(features_scaled)
    attack_labels = label_encoder.inverse_transform(preds)

    return attack_labels

def main():
    start_time = time.time()

    capture_with_tshark(CAPTURE_DURATION, CAPTURE_FILE)
    run_cicflowmeter(CAPTURE_FILE, FLOW_CSV)
    predictions = predict_attacks(FLOW_CSV, MODEL_PATH, SCALER_PATH, LABEL_ENCODER_PATH)

    attack_counts = Counter(predictions)
    print("\n=== Attack Detection Summary ===")
    for attack, count in attack_counts.items():
        print(f"{attack}: {count}")

    print(f"\n[+] Done in {time.time() - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()
