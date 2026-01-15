import vision_definitions
from naoqi import ALProxy
import urllib2
import json

class MyClass(GeneratedClass):
    def __init__(self):
        GeneratedClass.__init__(self)
        self.video_service = ALProxy("ALVideoDevice")
        self.subscriberID = None
        # REPLACE THIS WITH YOUR LAPTOP'S IP ADDRESS
        self.server_url = "http://192.168.1.15:5000/detect" 

    def onLoad(self):
        self.fps = 5
        self.resolution = vision_definitions.kQVGA # 320x240
        self.colorSpace = vision_definitions.kRGBColorSpace

    def onUnload(self):
        if self.subscriberID:
            self.video_service.unsubscribe(self.subscriberID)

    def onInput_onStart(self):
        # 1. Subscribe to camera
        self.subscriberID = self.video_service.subscribe("python_GVM", self.resolution, self.colorSpace, self.fps)
        
        # 2. Capture Image
        naoImage = self.video_service.getImageRemote(self.subscriberID)
        
        self.video_service.unsubscribe(self.subscriberID)
        self.subscriberID = None

        if naoImage:
            width = naoImage[0]
            height = naoImage[1]
            image_bytes = str(naoImage[6]) # Raw binary data

            # 3. Send to Laptop (Server)
            # We construct the URL with width/height params
            full_url = "%s?width=%d&height=%d" % (self.server_url, width, height)
            
            try:
                req = urllib2.Request(full_url, data=image_bytes)
                req.add_header('Content-Type', 'application/octet-stream')
                
                response = urllib2.urlopen(req, timeout=2)
                data = response.read()
                
                # 4. Parse the answer
                # The server returns {"result": "person"} or {"result": "laptop"}
                json_data = json.loads(data)
                obj = json_data.get("result", "nothing")
                
                self.logger.info("Server saw: " + obj)
                
                # 5. Trigger the specific output
                if obj == "person":
                    self.onPerson()
                elif obj == "laptop" or obj == "tv": # YOLO sometimes calls laptops 'tv'
                    self.onLaptop()
                else:
                    self.onNothing()

            except Exception as e:
                self.logger.error("Connection failed: " + str(e))
                self.onNothing()
        else:
            self.onNothing()
