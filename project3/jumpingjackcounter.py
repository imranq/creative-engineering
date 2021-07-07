import time


class JumpingJackCounter:
    counter = 0
    currentPosition = 0 # -1 not ready, 0 low position, 1 mid position, 2 high position
    elbowPosition = 0 # raw coordinates
    pose_definitions = {
        "nose": 0,
        "leftEye": 1,
        "rightEye": 2,
        "leftEar": 3,
        "rightEar": 4,
        "leftShoulder": 5,
        "rightShoulder": 6,
        "leftElbow": 7,
        "rightElbow": 8,
        "leftWrist": 9,
        "rightWrist": 10,
        "leftHip": 11,
        "rightHip": 12,
        "leftKnee": 13,
        "rightKnee": 14,
        "leftAnkle": 15,
        "rightAnkle": 16
    }
    
    face = ["nose", "leftEye", "rightEye", "leftEar", "rightEar"]
    shoulders = ["rightShoulder", "leftShoulder"]
    arms = ["rightWrist", "leftWrist", "rightElbow", "leftElbow"]
    
    coords = {
        
    }
    
    max_y = 255
    max_x = 255

    secondsStart = -1
    secondsLastUpdated = -1
    
    def __init__(self):
        self.coords = self.pose_definitions
        for key in self.coords.keys():
            self.coords[key] = [-1,-1]
            
        secondsStart = time.time()
        
        pass
    
    def availableCoords(self, partsArr, coords):
        result = []
        for part in partsArr:
            if coords[part][0] != -1:
                result.append(part)
        return result
        
    
    def isReady(self,coords):
        # Required: one of the shoulders
        # Required: one of the elbows or wrists
        # Required: one of the face points
        
        if len(self.availableCoords(self.face, coords)) == 0:
            return False
        
        if len(self.availableCoords(self.shoulders, coords)) == 0:
            return False
        
        if len(self.availableCoords(self.arms, coords)) == 0:
            return False
    
        secondsStart = time.time()
        secondsLastUpdated = time.time()
        
        
        return True
    
    def getCount(self):
        return self.counter
    
    # receives positions as per PoseNet specs and updates the state of jumping jacks
    def processCoords(self,coords):
        # counter increases is current position goes from low to high, within a certain angle relative to the center
        # returns true if counter has incremented
        
        
        
        
        if self.isReady(coords):
            shoulderCoordY = self.max_y - coords[self.availableCoords(self.shoulders, coords)[0]][1]
            armCoordY = self.max_y - coords[self.availableCoords(self.arms, coords)[0]][1]
                            
            if armCoordY > shoulderCoordY:
                self.currentPosition = 2
#                 self.speakStatus("Arms raised")
            elif self.currentPosition == 2 and armCoordY < shoulderCoordY:
                self.currentPosition = 0
                self.counter += 1
                secondsLastUpdated = time.time()
                return True
            else:
                self.currentPosition = 0
        else:
            print("Not ready")
            self.currentPosition = -1
            pass
        
        return False
    
    
    def secondsSinceLastRep(self):
        oldTime = self.secondsLastUpdated
        self.secondsLastUpdated = time.time()
        return time.time() - oldTime
    
    def resetCounter(self):
        self.counter = 0
        self.currentPosition == -1
        
 
