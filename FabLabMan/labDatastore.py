class LabDatastore(object):
    def __init__(self, db):
        self.db = db

    def commit(self):
        self.db.session.commit()

    def put(self, model):
        self.db.session.add(model)
        return model

    def delete(self, model):
        self.db.session.delete(model)

