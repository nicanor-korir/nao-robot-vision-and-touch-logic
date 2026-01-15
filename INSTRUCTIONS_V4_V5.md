# NAO V4 / V5 Setup Guide (Legacy/Standard)

## ⚠️ Important Limitations
* **Processor:** These robots run on a single-core Atom Z530. They cannot handle heavy processing
* **Strategy:** "Stop-and-Scan." The robot will stop moving before capturing an image to prevent motion blur and CPU crashes
* **Resolution:** Limited to **QVGA (320x240)** to maintain acceptable frame rates

---

## 1. Laptop (Server) Setup
*The "Brain" of the operation. This must run on a laptop on the same Wi-Fi.*

1.  **Install Python 3.x** on your laptop
2.  **Install Dependencies:**
    ```bash
    pip install flask ultralytics numpy opencv-python
    ```
3.  **Run the Server:**
    Navigate to the `server/` folder in this repo and run:
    ```bash
    python nao_server.py
    ```
    *Ensure the terminal says `Running on http://0.0.0.0:5000`*

---

## 2. Robot (Client) Setup (Choregraphe)

### Step A: The Python Script Box
1.  Open Choregraphe
2.  Create a new **Python Script** box
3.  Double-click to edit the code
4.  Copy the code from `robot_code/v4_v5_client.py` in this repo

### Step B: Configuration
Inside the script box, look for the `__init__` method and update your IP:
```python
# REPLACE with your Laptop's IP address (e.g., 192.168.1.15)
self.server_url = "http://YOUR_LAPTOP_IP:5000/detect"

```

### Step C: The Behavior Flow

For V4/V5, there's no loop continuously while walking. We create a "Check -> Act" cycle

1. **Vision Box:** Returns `onPerson`, `onLaptop`, or `onNothing`
2. **Logic:**
* If `onPerson` -> Connect to a **Say** box ("Hello Human")
* If `onNothing` -> Connect to a **Move To** box (Move X: 0.0, Theta: 0.5) to turn slightly and look again


3. **Loop:** Link the end of the `Say` and `Move` boxes back to the **Start** of the Vision box
