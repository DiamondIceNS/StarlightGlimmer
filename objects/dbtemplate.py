class DbTemplate:
    def __init__(self, gid, name, url, canvas, x, y, width, height, size, date_created, date_updated, md5, owner_id,
                 private=False):
        self.gid = gid
        self.name = name
        self.url = url
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.size = size
        self.date_created = date_created
        self.date_updated = date_updated
        self.md5 = md5
        self.owner_id = owner_id
        self.errors = None
        self.private = private

    def to_tuple(self):
        return (
            self.gid,
            self.name,
            self.url,
            self.canvas,
            self.x,
            self.y,
            self.width,
            self.height,
            self.size,
            self.date_created,
            self.date_updated,
            self.md5,
            self.owner_id,
            self.private
        )

    def center(self):
        return (2 * self.x + self.width) // 2, (2 * self.y + self.height) // 2
