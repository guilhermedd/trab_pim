class Voxel:
    def __init__(self, x, y, z, voxel_value):
        self.x = x
        self.y = y
        self.z = z
        self.voxel_value = voxel_value
        self.neighbors = []
        self.was_visited = False