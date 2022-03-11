from sqlalchemy import func
from flask_restful import Resource
from database import db
from labSessionDatastore import LabSessionDatastore, LabUserSessionDatastore
from labUserDatastore import LabUserDatastore
from lab_model import LabSession, LabUser, LabUserSession
from flask_restful import reqparse, inputs
from datetime import datetime
from dateUtils import getDatetimeReadable
import json

labUserSessionDatastore = LabUserSessionDatastore(db, LabUserSession)
labSessionDatastore = LabSessionDatastore(db, LabSession)
labUserDatastore = LabUserDatastore(db, LabUser)

us_parser = reqparse.RequestParser()
us_parser.add_argument('session_id', type=int, help='Id of the session')
us_parser.add_argument('user_id', type=int, help='Id of the user')

u_parser = reqparse.RequestParser()
u_parser.add_argument('user_id', type=int, help='Id of the user')
u_parser.add_argument('user_name', type=str, help='Name of the user')
u_parser.add_argument('user_surname', type=str, help='Surname of the user')
u_parser.add_argument('user_dob', type=inputs.datetime_from_iso8601, help='Date of birth of the user')
u_parser.add_argument('email', type=str, help='Email of the user')
u_parser.add_argument('first_ms_day', type=str, help='Date of first membership of the user')


class SessionUsers(Resource):
    def get(self):
        args = us_parser.parse_args(strict=True)
        us_list = labUserSessionDatastore.find_labUserSessions(labSessionId=args['session_id'])
        response = [dict(row.as_dict()) for row in us_list]
        # print(response)
        return json.dumps(response)

    def put(self):
        args = us_parser.parse_args(strict=True)
        # print("Adding a user to session : ",args["session_id"],"-",args["user_id"])
        u = labUserSessionDatastore.addlabUserSession(args['session_id'], args['user_id'], datetime.now())
        db.session.commit()
        # print(u)
        return json.dumps(u.as_dict())

    def delete(self):
        args = us_parser.parse_args(strict=True)
        u = labUserSessionDatastore.find_labUserSessions(labSessionId=args['session_id'],
                                                         labUserId=args['user_id']).first()
        if u is not None:
            labUserSessionDatastore.delete_labUserSession(u)
            db.session.commit()
        return '', 204


class LabUsers(Resource):
    def get(self):
        args = u_parser.parse_args(strict=True)
        if args['user_id'] is not None:
            u = labUserDatastore.find_labUsers(id=args['user_id']).first()
            return json.dumps(u.as_dict())
        elif args['user_name'] is not None and args['user_surname'] is not None and args['user_dob'] is not None:
            ur = labUserDatastore.find_labUserByPersonalDetails(name=args['user_name'], surname=args['user_surname'],
                                                                date_of_birth=args['user_dob'])
            if ur is not None:
                return json.dumps(ur.as_dict())
            else:
                return json.dumps([])

    def put(self):
        args = u_parser.parse_args(strict=True)
        print("Adding a user : ", args["user_name"])
        u = labUserDatastore.create_labUser(name=args['user_name'], surname=args['user_surname'],
                                            dateOfBirth=args['user_dob'], email=args['user_email'],
                                            firstMsDay=args['user_first_ms_day'])
        db.session.commit()
        return json.dumps(u.as_dict())

    def delete(self):
        args = u_parser.parse_args(strict=True)
        u = labUserDatastore.find_labUser(labUserId=args['user_id']).first()
        if u is not None:
            labUserDatastore.delete_labUser(u)
            db.session.commit()
        return '', 204
