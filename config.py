class Config:
    def __init__(self, size, framerate = 60, flags = 0):
        self.width = size[0]
        self.height = size[1]
        self.size = size
        self.center = self.width / 2, self.height / 2
        self.framerate = framerate
        self.flags = flags

        self.env = {}
    
