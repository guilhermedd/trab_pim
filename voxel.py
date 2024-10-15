class Voxel:
    def __init__(self, x, y, z, voxel_value):
        self.x = x
        self.y = y
        self.z = z
        self.value = voxel_value
        self.neighbors = []
        self.was_visited = False

    def get_group(self, group):
        stack = [self]
        self.was_visited = True
        group.append(self)

        while stack:
            current = stack.pop()
            if self.neighbors:
                for neighbor in current.neighbors:
                    if not neighbor.was_visited and neighbor.value == current.value:
                        neighbor.was_visited = True
                        group.append(neighbor)
                        stack.append(neighbor)

    def __str__(self):
        return f"x: {self.x}, y: {self.y}, z: {self.z}, value: {self.value}, was visited: {self.was_visited}"

