from flask import Flask, request, jsonify
import numpy as np
from ultralytics import YOLO

app = Flask(__name__)

# Load a lightweight AI model (YOLOv8 Nano)
# It will download automatically on first run
print("Loading AI Model...")
model = YOLO("yolov8n.pt") 

@app.route('/detect', methods=['POST'])
def detect():
    try:
        # 1. Get image dimensions from headers or args
        width = int(request.args.get('width'))
        height = int(request.args.get('height'))
        
        # 2. Get the raw binary data from the robot
        raw_data = request.data
        
        # 3. Convert raw bytes into an image array
        img_array = np.frombuffer(raw_data, dtype=np.uint8)
        image = img_array.reshape((height, width, 3))
        
        # 4. Run AI Detection
        results = model(image, verbose=False)
        
        # 5. Extract the most confident detection
        detected_object = "nothing"
        highest_conf = 0.0
        
        # Check what the AI found
        for r in results:
            for box in r.boxes:
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                label = model.names[cls]
                
                # We only care about objects with >50% confidence
                if conf > 0.5 and conf > highest_conf:
                    highest_conf = conf
                    detected_object = label

        print(f"Robot saw: {detected_object}")
        return jsonify({"result": detected_object})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"result": "error"})

if __name__ == '__main__':
    # '0.0.0.0' allows other devices (the robot) to connect to your laptop
    app.run(host='0.0.0.0', port=5000)
