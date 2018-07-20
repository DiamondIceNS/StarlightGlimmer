# Helper class to store coordinate pairs
class Coords:
    def __init__(self, x, y):
        self.coord = (x, y)

    @property
    def x(self):
        return self.coord[0]

    @property
    def y(self):
        return self.coord[1]

    def __iter__(self):
        yield from self.coord

    def __add__(self, other):
        return Coords(self.coord[0] + other, self.coord[1] + other)

    def __sub__(self, other):
        return Coords(self.coord[0] - other, self.coord[1] - other)

    def __mul__(self, other):
        return Coords(self.coord[0] * other, self.coord[1] * other)

    def __floordiv__(self, other):
        return Coords(self.coord[0] // other, self.coord[1] // other)

    def __mod__(self, other):
        return Coords(self.coord[0] % other, self.coord[1] % other)

    def __repr__(self):
        return "Coord({}, {})".format(*self.coord)
