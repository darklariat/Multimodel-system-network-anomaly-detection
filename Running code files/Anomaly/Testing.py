from xgboost import XGBClassifier
import os
import pandas as pd
import joblib
from collections import Counter

# --- Load model and preprocessing ---
model = XGBClassifier()
model.load_model("C:/Internship/NetSleuth/Anomaly/models/xgb_multiclass_model.json")
scaler = joblib.load("C:/Internship/NetSleuth/Anomaly/models/scaler.pkl")
label_encoder = joblib.load("C:/Internship/NetSleuth/Anomaly/models/label_encoder.pkl")

def process_csv_folder(folder_path):
    summary = {}

    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            filepath = os.path.join(folder_path, filename)
            try:
                df = pd.read_csv(filepath)
                df = df.drop(['src_ip', 'dst_ip', 'timestamp'], axis=1, errors='ignore')

                total_flows = len(df)
                if total_flows == 0:
                    summary[filename] = {"total_flows": 0, "class_counts": {}}
                    continue

                # Ensure columns match training data order
                expected_features = scaler.feature_names_in_
                df = df.reindex(columns=expected_features, fill_value=0)

                # Scale and predict
                df_scaled = scaler.transform(df)
                predictions = model.predict(df_scaled)

                # Map numeric predictions back to labels
                pred_labels = label_encoder.inverse_transform(predictions)

                # Count occurrences of each class
                class_counts = dict(Counter(pred_labels))

                summary[filename] = {
                    "total_flows": total_flows,
                    "class_counts": class_counts
                }

            except Exception as e:
                summary[filename] = {"error": str(e)}

    return summary

if __name__ == "__main__":
    folder_path = "C:/Users/aliza/Downloads/wiresharkcapture"
    results = process_csv_folder(folder_path)

    for file, data in results.items():
        print(f"\n{file}:")
        if "error" in data:
            print(f"  Error: {data['error']}")
        else:
            print(f"  Total Flows: {data['total_flows']}")
            print("  Class Counts:")
            for cls, count in data["class_counts"].items():
                print(f"    {cls}: {count}")
