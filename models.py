from web.server import db

class HashTagModel(db.Model):
    __tablename__ = 'hash_tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45))

    def __init__(self, name):
        self.name = name

    def serialize(self):
        return {
          "id": self.id,
          "name": self.name
        }

class HashTagProductModel(db.Model):
    __tablename__ = 'hash_tag_product'
    id = db.Column(db.Integer, primary_key=True)
    hash_tag_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer)

    def __init__(self, name, hash_tag_id, product_id):
        self.name = name
        self.hash_tag_id = hash_tag_id
        self.product_id = product_id
    def serialize(self):
        return {
          "id": self.id,
          "hash_tag_id": self.hash_tag_id,
          "product_id": self.product_id
        }