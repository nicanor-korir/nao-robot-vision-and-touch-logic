import time
import vision_definitions
from naoqi import ALProxy
import urllib2
import json

class MyClass(GeneratedClass):
    def __init__(self):
        GeneratedClass.__init__(self)
        self.video_service = ALProxy("ALVideoDevice")
        self.motion = ALProxy("ALMotion")
        self.tts = ALProxy("ALTextToSpeech")
        self.posture = ALProxy("ALRobotPosture")
        
        self.subscriberID = None
        self.is_patrolling = False
        
        # --- CONFIGURATION ---
        # Update with your Laptop's IP
        self.server_url = "http://192.168.1.15:5000/detect" 
        
        # Walking Speed (X = Forward). 
        # 0.5 is fast, 0.2 is safe for testing.
        self.walk_velocity = 0.2 

    def onLoad(self):
        # V6 has better cameras, we can use VGA (640x480) instead of QVGA
        self.fps = 15
        self.resolution = vision_definitions.kVGA 
        self.colorSpace = vision_definitions.kRGBColorSpace

    def onUnload(self):
        self.stop_patrol()

    def onInput_onStop(self):
        self.stop_patrol()

    def stop_patrol(self):
        self.is_patrolling = False
        self.motion.stopMove() # Stop walking immediately
        if self.subscriberID:
            self.video_service.unsubscribe(self.subscriberID)
            self.subscriberID = None
        self.onStopped()

    def onInput_onStart(self):
        if self.is_patrolling:
            return

        self.logger.info("Starting Patrol Mode...")
        self.is_patrolling = True
        
        # 1. Stand up safely if not already
        # self.posture.goToPosture("StandInit", 0.5)

        # 2. Subscribe to Camera
        self.subscriberID = self.video_service.subscribe("python_GVM_V6", self.resolution, self.colorSpace, self.fps)

        # 3. Start Walking (Non-blocking)
        # move(x, y, theta) -> This sets velocity. It does not wait to finish.
        self.motion.move(self.walk_velocity, 0, 0)

        # 4. The Loop
        while self.is_patrolling:
            # Capture Image
            naoImage = self.video_service.getImageRemote(self.subscriberID)
            
            if naoImage:
                # V6 Specific: Handle image data
                width = naoImage[0]
                height = naoImage[1]
                image_bytes = str(naoImage[6])

                # Send to Laptop
                detected_object = self.check_server(width, height, image_bytes)
                
                # REACT to the object
                if detected_object != "nothing":
                    self.handle_encounter(detected_object)
            
            # Small sleep to prevent CPU overload, but keep it responsive
            time.sleep(0.1)

    def check_server(self, w, h, img_bytes):
        full_url = "%s?width=%d&height=%d" % (self.server_url, w, h)
        try:
            req = urllib2.Request(full_url, data=img_bytes)
            req.add_header('Content-Type', 'application/octet-stream')
            response = urllib2.urlopen(req, timeout=1) # Fast timeout for walking
            data = json.loads(response.read())
            return data.get("result", "nothing")
        except Exception as e:
            # self.logger.error("Server error: " + str(e))
            return "nothing"

    def handle_encounter(self, obj_name):
        self.logger.info("Encountered: " + obj_name)
        
        # 1. STOP WALKING
        self.motion.stopMove()
        
        # 2. INTERACT
        if obj_name == "person":
            self.tts.say("Hello there! I see a person.")
            # Optional: Animation or Wave
            
        elif obj_name == "laptop" or obj_name == "tv":
            self.tts.say("I see a laptop. I will turn away.")
            # Turn 90 degrees right
            self.motion.moveTo(0, 0, -1.5) 
            
        elif obj_name == "chair":
            self.tts.say("Obstacle detected.")
            # Move back slightly
            self.motion.moveTo(-0.2, 0, 0)
            
        # 3. RESUME WALKING
        # Only resume if we haven't been stopped externally
        if self.is_patrolling:
            self.tts.say("Resuming patrol.")
            self.motion.move(self.walk_velocity, 0, 0)
  
