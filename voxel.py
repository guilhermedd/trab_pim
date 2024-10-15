class Voxel:
    def __init__(self, x, y, z, voxel_value):
        self.x = x
        self.y = y
        self.z = z
        self.value = voxel_value
        self.neighbors = []
        self.was_visited = False
        self.type = 0 if self.value == 255 else 1 if self.value == 200 else 2