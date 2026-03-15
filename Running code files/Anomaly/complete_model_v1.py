import os
import sys
import time
import subprocess
import socket
import psutil
import pandas as pd
from xgboost import XGBClassifier

def is_admin():
    if os.name != 'nt':
        return True
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def get_top_network_interface(sniff_time):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    for iface_name, iface_addrs in psutil.net_if_addrs().items():
        for addr in iface_addrs:
            if addr.family == socket.AF_INET and addr.address == local_ip:
                return iface_name
    return None

def wait_for_file_release(filepath, timeout=5):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with open(filepath, 'r'):
                return True
        except PermissionError:
            time.sleep(0.5)
    raise RuntimeError(f"Timeout waiting for file release: {filepath}")

def capture_flows(duration_seconds=180, output_csv="flows.csv"):
    iface = get_top_network_interface(2)
    if iface is None:
        raise RuntimeError("Unable to determine network interface.")

    if os.path.exists(output_csv):
        try:
            os.remove(output_csv)
        except PermissionError:
            wait_for_file_release(output_csv)   
            os.remove(output_csv)

    print("[*] Starting Flow Capture...")
    process = subprocess.Popen(
        ['cicflowmeter', '-i', iface, '-c', output_csv],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    time.sleep(duration_seconds)

    process.terminate()
    process.wait()
    print("[*] Flow capture finished.")

    wait_for_file_release(output_csv)
    print("[*] Output file released.")
    return pd.read_csv(output_csv)

if __name__ == "__main__":
    if os.name == 'nt':
        if "--elevated" not in sys.argv:
            if not is_admin():
                print("[*] Requesting admin privileges...")

                subprocess.run([
                    'powershell', '-Command',
                    f'Start-Process "{sys.executable}" -ArgumentList \'"{__file__}" --elevated\' -Verb RunAs'
                ])
                sys.exit(0)
            else:
                print("[*] Already running as admin.")

    try:
        print("[+] Running core logic...")

        flows_df = capture_flows()  # Uncomment if capturing live
        #flows_df = pd.read_csv("C:/Internship/flows.csv")
        print(f"[+] {len(flows_df)} flows loaded.")

        df = flows_df.drop(['src_ip', 'dst_ip', 'src_port', 'protocol', 'timestamp'], axis=1)

        model = XGBClassifier()
        model.load_model("C:/Internship/Model Scripts/Anomaly/xgb_model.json")

        predictions = model.predict(df)
        print(f"[+] Anomalies detected: {sum(predictions)}")

    except Exception as e:
        print(f"[!] Error: {e}")

    input("Press Enter to exit...")
