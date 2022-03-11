from database import db
from flask_security import UserMixin, RoleMixin
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Boolean, DateTime, Column, Integer, \
                       String, ForeignKey, Float, Table


class LabUserSession(db.Model):
    __tablename__ = 'lab_user_session'
    labSessionId = Column(Integer(), ForeignKey('lab_session.id'), primary_key=True)
    labUserId = Column(Integer(), ForeignKey('lab_user.id'), primary_key=True)
    dateStart = Column(DateTime(), nullable=False)
    dateEnd = Column(DateTime())

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


class LabSession(db.Model):
    __tablename__ = 'lab_session'
    id = Column(Integer(), primary_key=True)

    labmanagerId = Column(Integer(), ForeignKey('lab_user.id'))
    sessionType = Column(String(80))
    dateStart = Column(DateTime())
    dateEnd = Column(DateTime())
    labUserSessions = relationship('LabUserSession', lazy=True, backref=backref('usersSession'))
    # labUserSessions = relationship('LabUserSession', secondary=labUserSession, lazy='subquery',
    #                                backref=backref('sessions', lazy=True))
#    machineReservations = relationship('MachineReservation', lazy=True,
#                                   backref=backref('session', lazy=True))
#
# class LabUserRole(Base):
#     __tablename__ = 'lab_role'
#     id = Column(Integer(), primary_key=True)
#     labUserId = Column(Integer(), ForeignKey('LabUser.id'), nullable=False)
#     type = Column(String(80), nullable=False)
#     dateStart = Column(DateTime())
#     dateEnd = Column(DateTime())
#
# class LabUserPhoto(Base):
#     __tablename__ = 'lab_user_photo'
#     id = Column(Integer(), primary_key=True)
#     path = Column(String(255), nullable=False)
#     labUserId = Column(Integer(), ForeignKey('LabUser.id'), nullable=False)

class LabUser(db.Model):
    __tablename__ = 'lab_user'
    id = Column(Integer(), primary_key=True)
    name = Column(String(255), nullable=False)
    surname = Column(String(255), nullable=False)
    dateOfBirth = Column(DateTime(), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hash = Column(String(80)) #Hash to be used in QRCodes
    password = Column(String(80))
    firstMsDay = Column(DateTime(), nullable=False)
    sessions = relationship('LabUserSession', lazy=True, backref=backref('users'))
    # photos = relationship('LabUserPhoto', lazy=True, backref=backref('labUser'))
    # memberships = relationship('LabUserMembership', lazy=True, backref=backref('labUser'))
    # machineAuthorizations = relationship('MachineAuthorization', lazy=True, backref=backref('labUser'))
    # skills = relationship('Skill', lazy=True, backref=backref('labUser'))
    # invoices = relationship('Invoice', lazy=True, backref=backref('labUser'))
    # roles = relationship('LabUserRole', lazy=True, backref=backref('labUser'))

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}

#
# class LabUserMembership(Base):
#     __tablename__ = 'lab_user_membership'
#     labUserId = Column(Integer(), ForeignKey('LabUser.id'), primary_key=True)
#     msPeriodId = Column(Integer(), ForeignKey('MembershipPeriod.id'), primary_key=True)
#     gender = Column(String(80))
#     street = Column(String(255))
#     addressDetail = Column(String(255))
#     postalCode = Column(String(80))
#     streetNumber = Column(String(20))
#     country = Column(String(100))
#     phoneNumber1 = Column(String(25))
#     phoneNumber2 = Column(String(25))
#     contactName1 = Column(String(255))
#     contactSurname1 = Column(String(255))
#     contactNumber1 = Column(String(25))
#     contactName2 = Column(String(255))
#     contactSurname2 = Column(String(255))
#     contactNumber2 = Column(String(25))
#     paymentType = Column(String(80))
#     paymentId = Column(String(80))
#     dateStart = Column(DateTime())
#     dateEnd = Column(DateTime())
#     type = Column(Integer(), ForeignKey('MembershipType.id'), nullable=False)
#     imageRights = Column(Boolean())
#
# class MembershipPeriod(Base):
#     __tablename__ = 'membership_period'
#     msPeriodId = Column(Integer(), primary_key=True)
#     name = Column(String(80))
#     dateStart = Column(DateTime())
#     dateEnd = Column(DateTime())
#
# class MembershipType(Base):
#     __tablename__ = 'membership_type'
#     id = Column(Integer(), primary_key=True)
#     name = Column(String(80))
#     price = Column(Float())
#
#
# class Machine(Base):
#     __tablename__ = 'machine'
#     id = Column(String(80), primary_key=True)
#     name = Column(String(80), nullable=False)
#     description = Column(String(255))
#     type = Column(String(80), nullable=False)
#     docUrl = Column(String(500))
#
# class MachineAuthorization(Base):
#     __tablename__ = 'machine_authorization'
#     id = Column(Integer, primary_key=True)
#     machineId = Column(String(80), ForeignKey('Machine.id'), nullable=False)
#     labUserId = Column(Integer(), ForeignKey('LabUser.id'), nullable=False)
#     dateStart = Column(DateTime(), nullable=False)
#     dateEnd = Column(DateTime())
#     type = Column(String(80), nullable=False)
#
# class Skill(Base):
#     __tablename__ = 'skill'
#     id = Column(Integer, primary_key=True)
#     labUserId = Column(Integer(), ForeignKey('LabUser.id'), nullable=False)
#     dateStart = Column(DateTime(), nullable=False)
#     dateEnd = Column(DateTime())
#     type = Column(String(80), nullable=False)
#
# class MachineReservation(Base):
#     __tablename__ = 'machine_reservation'
#     id = Column(Integer, primary_key=True)
#     labUserId = Column(Integer(), ForeignKey('LabUser.id'), nullable=False)
#     labSessionId = Column(Integer(), ForeignKey('LabSession.id'), nullable=False)
#     dateStart = Column(DateTime(), nullable=False)
#     dateEnd = Column(DateTime(), nullable=False)
#     machineId = Column(Integer(), ForeignKey('Machine.id'), nullable=False)
#     comment = Column(String(2000))
#
# class MachineUsage(Base):
#     __tablename__ = 'machine_usage'
#     id = Column(Integer, primary_key=True)
#     labUserId = Column(Integer(), ForeignKey('LabUser.id'), nullable=False)
#     projectId = Column(Integer(), ForeignKey('Project.id'))
#     machineId = Column(Integer(), ForeignKey('Machine.id'), nullable=False)
#     date = Column(DateTime(), nullable=False)
#     duration = Column(Integer(), nullable=False)
#     jobId = Column(String(255))
#     userComment = Column(String(2000))
#     billable = Column(Boolean)
#     internalComment = Column(String(2000))
#
# class Project(Base):
#     __tablename__ = 'project'
#     id = Column(Integer, primary_key=True)
#     name = Column(String(80))
#     type = Column(String(80))
#     description = Column(String(2000))
#     machineUsages = relationship('MachineUsage', lazy=True, backref=backref('project'))
#
# class Invoice(Base):
#     __tablename__ = 'invoice'
#     id = Column(Integer, primary_key=True)
#     labUserId = Column(Integer(), ForeignKey('LabUser.id'), nullable=False)
#     date = Column(DateTime(), nullable=False)
#
# class InvoiceDetail(Base):
#     __tablename__ = 'invoice_detail'
#     id = Column(Integer, primary_key=True)
#     invoiceId = Column(Integer(), ForeignKey('Invoice.id'))
#     machineUsageId = Column(Integer(), ForeignKey('MachineUsage.id'))
#     prestationId = Column(Integer(), ForeignKey('Prestation.id'))
#     vat = Column(Float, nullable=False)
#     price = Column(Float, nullable=False)
