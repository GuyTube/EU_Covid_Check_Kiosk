import dateUtils
from labDatastore import LabDatastore
from sqlalchemy import func
from lab_model import LabUser

class LabUserDatastore(LabDatastore):

    def __init__(self, db, labUser_model):
        LabDatastore.__init__(self, db)
        self.labUser_model = labUser_model


    def get_labUser(self, id):
        return self.find_labUsers(id=id).first()

    def create_labUser(self, **kwargs):
        """Creates and returns a new user from the given parameters."""
        user = self.labUser_model(**kwargs)
        return self.put(user)

    def delete_labUser(self, user):
        """Deletes the specified user.
        :param user: The user to delete
        """
        self.delete(user)

    def find_labUsers(self, **kwargs):
        return self.labUser_model.query.filter_by(**kwargs)

    def find_labUserByPersonalDetails(self, name, surname, date_of_birth):
        list = self.labUser_model.query.filter(func.lower(LabUser.surname) == func.lower(surname))
        if list is not None:
            for user in list:
                if user.name.lower() == name.lower() and user.dateOfBirth == date_of_birth:
                    return user