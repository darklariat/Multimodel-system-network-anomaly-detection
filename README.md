# 🕵️‍♂️ Multimodel-System-Network-Anomaly-Detector

**Multimodel System Network Anomaly Detector** is a real-time network bottleneck monitoring and anomaly-detection system. It identifies performance issues across End-User devices, ISPs, and LAN/Router/Server environments, while simultaneously detecting cyber threats such as MITM, DoS, and scanning attacks. The system leverages passive traffic capture, rolling feature buffers, and multiple XGBoost-based classifiers.

---

> [!NOTE]
> ## 📺 LIVE DEMO CLIPS

<div align="center">
  <h3>🚀 End-User Device Bottleneck Detection</h3>
  <video src="https://github.com/user-attachments/assets/2e91e568-0048-43ea-9973-415ee1acfc5b" width="90%" controls></video>
  <p><i>Real-time classification of local system resource issues.</i></p>
</div>

<br>

<div align="center">
  <h3>🌐 ISP & Network Bottleneck Detection</h3>
  <video src="https://github.com/user-attachments/assets/be32e703-ed66-48e5-8992-d9e429e97e8b" width="90%" controls></video>
  <p><i>Detection of external latency, packet loss, and routing issues.</i></p>
</div>

---

> [!NOTE]
> ## 🏗️ SYSTEM ARCHITECTURE
> The system utilizes parallel threads to extract features in real-time, ensuring 100% monitoring uptime.

### **1. Bottleneck Detection Pipeline**
*Detailed multi-model architecture incorporating End-User, ISP, and Router/LAN features.*
<div align="center">
  <img src="https://github.com/user-attachments/assets/a9cc0233-3d9e-42ef-be97-159f68bf3fa3" alt="Bottleneck Pipeline" width="100%">
  <p><i>(Click the image in GitHub to view the full-resolution architecture)</i></p>
</div>

### **2. Anomaly Detection Pipeline**
*Streamlined flow conversion via CICFlowMeter for immediate threat classification.*
<div align="center">
  <img src="https://github.com/user-attachments/assets/b4af583d-e931-41cb-8840-c1a795267d35" alt="Anomaly Pipeline" width="500">
</div>

---

> [!TIP]
> ## 📈 MODEL PERFORMANCE & METRICS
> The system achieves high recall across all fault domains by utilizing **adaptive baselining** to account for varying hardware capabilities.

| Diagnostic Domain | Macro Average F1 Score |
| :--- | :---: |
| **Router / LAN** | **99%** |
| **ISP Features** | **95%** |
| **Anomaly Detection** | **94%** |
| **End-User Device** | **89%** |

---

## 📊 **CLASSIFICATION MATRICES**
<details open>
<summary><b>Click to expand/collapse detailed model reports</b></summary>
<br>

### **Fault Domain Reports **
<div align="center">
  <table border="0">
    <tr>
      <td align="center"><b>End-User Device</b> <br><img src="https://github.com/user-attachments/assets/a5e209be-15ce-4766-b60b-de3c39d76fa2" width="400"></td>
      <td align="center"><b>ISP Features</b> <br><img src="https://github.com/user-attachments/assets/b860a918-d0a1-44ec-a2b5-8c0638ba4f53" width="400"></td>
    </tr>
    <tr>
      <td align="center"><b>Router/LAN</b> <br><img src="https://github.com/user-attachments/assets/b761c814-e9ff-4e14-85b0-8d3a47c8a277" width="400"></td>
      <td align="center"><i>Space reserved for future modules</i></td>
    </tr>
  </table>
</div>

### **Detailed Anomaly Detection Report**
*This matrix handles high-volume attack traffic and is displayed at full scale for maximum detail.*
<div align="center">
  <img src="https://github.com/user-attachments/assets/edcbbf3f-b84a-4c0f-a139-bc00721b423b" alt="Anomaly Matrix" width="100%">
</div>
</details>

---

> [!NOTE]
> ## 🛠️ KEY ENGINEERING FEATURES

* **Adaptive Baselining:** Stores a buffer of the latest 50 non-anomaly values to calculate rolling baselines with decay, reducing false positives.
* **Privacy-First:** Prioritizes flow-level and metadata features over packet payload retention to maintain user privacy.
* **Custom Dataset:** Created via Linux VM simulations to address the lack of suitable public datasets for specific bottleneck scenarios.
* **Telemetry Fusion:** Ingests host metrics via `psutil`, `TShark` captures, and active probes like ping/traceroute.
* **Parallel Extraction:** Implements multiple threads for simultaneous feature extraction to support 100% monitoring uptime.

---

> [!IMPORTANT]
> ## 🚀 GETTING STARTED

### **1. Prerequisites**
* **TShark:** Installed and added to system PATH.
* **CICFlowMeter:** Required for generating flow-based features for anomaly detection.
* **Npcap:** (Windows Only) Required for packet capture via TShark.

### **2. Setup**
1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/MuhammadSaad-1/Multimodel-System-Network-Anomaly-Detector.git](https://github.com/MuhammadSaad-1/Multimodel-System-Network-Anomaly-Detector.git)
    ```
2.  **Wireshark Installation:** 
    You must place the **Wireshark** installation folder inside the `Bottleneck` directory.

### **3. Execution**
Navigate to `Running code files` and run the script for your specific needs:

#### **Anomaly Detection System**
* **Linux:** `python Anomaly/AllForOne.py`
* *(Note: Anomaly detection is currently only supported on Linux)*

#### **Bottleneck Detection System**
* **Windows:** `python Bottleneck/Windows/ALLFORONE_W.py`
* **Linux:** `python Bottleneck/Linux/ALLFORONE_L.py`
