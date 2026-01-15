import cv2
from flask import Flask, request, jsonify
import numpy as np
from ultralytics import YOLO

app = Flask(__name__)

# Load Model
print("Loading Model...")
model = YOLO("yolov8n.pt") 

@app.route('/detect', methods=['POST'])
def detect():
    try:
        # 1. Parse Data
        width = int(request.args.get('width'))
        height = int(request.args.get('height'))
        raw_data = request.data
        
        # 2. Construct Image from Raw Bytes
        img_array = np.frombuffer(raw_data, dtype=np.uint8)
        image = img_array.reshape((height, width, 3))

        # 3. COLOR CORRECTION (OpenCV usage)
        # NAO sends RGB, but OpenCV uses BGR
        # We convert it so colors look correct on your screen
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # 4. Run Inference
        results = model(image_bgr, verbose=False)
        
        # 5. VISUALIZATION (OpenCV usage)
        # This draws the boxes (Person, Laptop, etc) onto the image
        annotated_frame = results[0].plot()
        
        # Show the "Robot View" window on your laptop screen
        cv2.imshow("NAO Robot Vision - Live Feed", annotated_frame)
        cv2.waitKey(1) # Required to update the window

        # 6. Extract Logic
        detected_object = "nothing"
        highest_conf = 0.0
        
        for r in results:
            for box in r.boxes:
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                label = model.names[cls]
                
                if conf > 0.5 and conf > highest_conf:
                    highest_conf = conf
                    detected_object = label

        print(f"Robot saw: {detected_object}")
        return jsonify({"result": detected_object})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"result": "error"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
