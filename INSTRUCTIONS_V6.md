# NAO V6 Setup Guide (Advanced/Patrol)

## 🚀 Performance Features
* **Processor:** Quad-core Atom E3845 allows for multitasking
* **Strategy:** "Continuous Patrol." The robot walks continuously (`ALMotion.move`) while streaming video in a background thread
* **Resolution:** Uses **VGA (640x480)** for higher accuracy object detection from further distances

---

## 1. Laptop (Server) Setup
*Same server setup as V4/V5. The server is hardware agnostic*

1.  **Install Python 3.x** on your laptop
2.  **Install Dependencies:**
    ```bash
    pip install flask ultralytics numpy opencv-python
    ```
3.  **Run the Server:**
    ```bash
    python nao_server.py
    ```

---

## 2. Robot (Client) Setup (Choregraphe)

### Step A: The Patrol Script Box
1.  Open Choregraphe
2.  Create a new **Python Script** box
3.  Copy the code from `robot_code/v6_patrol_client.py`
    * *Note: This script uses `ALMotion.move()` (non-blocking) instead of `moveTo()`*

### Step B: Critical Configuration
Inside the script, update these two variables:

```python
# 1. Your Laptop IP
self.server_url = "http://YOUR_LAPTOP_IP:5000/detect"

# 2. Walking Speed (0.1 = Safe/Slow, 0.5 = Fast)
self.walk_velocity = 0.2

```

### Step C: Safety Wiring

Since the robot moves autonomously in this mode, you **must** wire a safety stop

1. Drag a **Tactile Head** box into the flow
2. Connect the **Tactile Head** output to the **onStop** input of your Python Patrol box
3. **Operation:** Touching the robot's head will immediately cut power to the motors and stop the loop

---

## 3. Optimization for V6

* **Head Pitch:** In the `onStart` method, ensure the head is pitched up slightly (`-0.2` radians) to see faces rather than knees
* **Blur Reduction:** If the robot is walking too fast, the camera image will blur, causing YOLO to miss objects. Reduce `self.walk_velocity` if detection accuracy drops
* **Focus:** The V6 cameras have fixed focus. Objects closer than 30cm may appear blurry. Keep a safe interaction distance

```
