class MotionDetector:

    def __init__(self, cap, timepoint):
        self.cap = cap
        self.mask = array([])
        
    def detect(self):
        
