from labDatastore import LabDatastore
from lab_model import LabUserSession

class LabSessionDatastore(LabDatastore):

    def __init__(self, db, labSession_model):
        LabDatastore.__init__(self, db)
        self.labSession_model = labSession_model


    def get_labSession(self, id):
        return self.find_labSessions(id=id).first()

    def create_labSession(self, **kwargs):
        """Creates and returns a new session from the given parameters."""
        session = self.labSession_model(**kwargs)
        return self.put(session)

    def delete_labSession(self, session):
        """Deletes the specified user.
        :param user: The user to delete
        """
        self.delete(session)

    def find_labSessions(self, **kwargs):
        return self.labSession_model.query.filter_by(**kwargs)


class LabUserSessionDatastore(LabDatastore):
    def __init__(self, db, labUserSession_model):
        LabDatastore.__init__(self, db)
        self.labUserSession_model = labUserSession_model

    def get_labUserSession(self, id):
        return self.find_labSessions(id=id).first()

    def create_labUserSession(self, **kwargs):
        """Creates and returns a new session from the given parameters."""
        usersession = self.labUserSession_model(**kwargs)
        return self.put(usersession)

    def delete_labUserSession(self, usersession):
        self.delete(usersession)

    def find_labUserSessions(self, **kwargs):
        return self.labUserSession_model.query.filter_by(**kwargs)

    def addlabUserSession(self, session_id, user_id, date):
        return self.create_labUserSession(labSessionId=session_id, labUserId=user_id, dateStart=date)