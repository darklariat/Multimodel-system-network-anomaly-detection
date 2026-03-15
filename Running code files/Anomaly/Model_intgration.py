import os
import sys
import time
import ctypes
import psutil
import socket
import tempfile
import pandas as pd
from xgboost import XGBClassifier
from cicflowmeter.sniffer import Sniffer

def get_top_network_interface(sniff_time):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    default_interface = None
    for iface_name, iface_addrs in psutil.net_if_addrs().items():
        for addr in iface_addrs:
            if addr.family == socket.AF_INET and addr.address == local_ip:
                default_interface = iface_name
                break
        if default_interface:
            break
    return default_interface

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    script = sys.executable
    params = ' '.join([f'"{arg}"' for arg in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", script, params, None, 1)
    sys.exit()

interface = get_top_network_interface(2)

def capture_flows(duration_seconds: int):     
    # Use a temporary directory to store flow CSV
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "flows.csv")

        # Start flow sniffer
        sniffer = Sniffer(
            interface=interface,
            output_mode='csv',
            output_path=output_path,
            live=True,
            show_output=False,
        )

        print(f"[+] Starting flow capture on interface '{interface}' for {duration_seconds} seconds...")
        sniffer.start()

        # Wait for the specified duration
        time.sleep(duration_seconds)

        # Stop capturing
        sniffer.stop()
        print("[+] Flow capture stopped.")

        # Load the CSV output
        if os.path.exists(output_path):
            print("[+] Loading captured flows into DataFrame...")
            df = pd.read_csv(output_path)
            return df
        else:
            raise FileNotFoundError("Flow output file not found!")

if __name__ == "__main__":
    try:
        if not is_admin():
            print("[!] Not running as admin. Attempting to relaunch with admin rights...")
            run_as_admin()
        
        flows_df = capture_flows(30)
        print(f"[+] {len(flows_df)} flows captured.")
        
        df = flows_df.drop(['src_ip', 'dst_ip', 'src_port', 'protocol', 'timestamp'], axis = 1)
        
        model = XGBClassifier()
        model.load_model("xgb_model.json")

        print(model.predict(df).sum())
        
        # === You can now process `flows_df` as you like ===
    except Exception as e:
        print(f"[!] Error: {e}")
