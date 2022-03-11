# Example of combining Flask-Security and Flask-Admin.
# by Steve Saporta
# April 15, 2014
#
# Uses Flask-Security to control access to the application, with "admin" and "end-user" roles.
# Uses Flask-Admin to provide an admin UI for the lists of users and roles.
# SQLAlchemy ORM, Flask-Mail and WTForms are used in supporting roles, as well.


from flask import Flask, render_template, send_from_directory
# from flask_sqlalchemy import SQLAlchemy
from database import db
from api_base import api
from flask_security import current_user, login_required, Security, \
    SQLAlchemyUserDatastore, utils
from flask_mail import Mail
from flask_admin import Admin
from flask_admin.contrib import sqla
from datetime import datetime
from wtforms.fields import PasswordField

# Initialize Flask and set some config values
from labSessionDatastore import LabSessionDatastore, LabUserSessionDatastore
from labUserDatastore import LabUserDatastore
from database import Base
from models import Role, User
from lab_model import LabSession, LabUser, LabUserSession
from dateUtils import getDatetime
from api_session import SessionUsers, LabUsers

app = Flask(__name__)
app.config['DEBUG']=True
# Replace this with your own secret key
app.config['SECRET_KEY'] = 'super-secret'
# The database must exist (although it's fine if it's empty) before you attempt to access any page of the app
# in your browser.
# I used a PostgreSQL database, but you could use another type of database, including an in-memory SQLite database.
# You'll need to connect as a user with sufficient privileges to create tables and read and write to them.
# Replace this with your own database connection string.
#xxxxx
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:xxxxxxxx@localhost/flask_example'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///c:\\workspace\\qrcode\\FabLabMan\\test.db'

# Set config values for Flask-Security.
# We're using PBKDF2 with salt.
app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'
# Replace this with your own salt.
app.config['SECURITY_PASSWORD_SALT'] = 'kdfkdsfj'

# Flask-Security optionally sends email notification to users upon registration, password reset, etc.
# It uses Flask-Mail behind the scenes.
# Set mail-related config values.
# Replace this with your own "from" address
app.config['SECURITY_EMAIL_SENDER'] = 'no-reply@example.com'
# Replace the next five lines with your own SMTP server settings
app.config['MAIL_SERVER'] = '******'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = '*****'
app.config['MAIL_PASSWORD'] = '******'

# Initialize Flask-Mail and SQLAlchemy
mail = Mail(app)

# Create a table to support a many-to-many relationship between Users and Roles
# roles_users = db.Table(
#     'roles_users',
#     db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
#     db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
# )
#
#
# # Role class
# class Role(db.Model, RoleMixin):
#
#     # Our Role has three fields, ID, name and description
#     id = db.Column(db.Integer(), primary_key=True)
#     name = db.Column(db.String(80), unique=True)
#     description = db.Column(db.String(255))
#
#     # __str__ is required by Flask-Admin, so we can have human-readable values for the Role when editing a User.
#     # If we were using Python 2.7, this would be __unicode__ instead.
#     def __str__(self):
#         return self.name
#
#     # __hash__ is required to avoid the exception TypeError: unhashable type: 'Role' when saving a User
#     def __hash__(self):
#         return hash(self.name)
#
#
# # User class
# class User(db.Model, UserMixin):
#
#     # Our User has six fields: ID, email, password, active, confirmed_at and roles. The roles field represents a
#     # many-to-many relationship using the roles_users table. Each user may have no role, one role, or multiple roles.
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(255), unique=True)
#     password = db.Column(db.String(255))
#     active = db.Column(db.Boolean())
#     confirmed_at = db.Column(db.DateTime())
#     roles = db.relationship(
#         'Role',
#         secondary=roles_users,
#         backref=db.backref('users', lazy='dynamic')
#     )

# class LabSession(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     sessionType = db.Column(db.String(80))
#     dateStart = db.Column(db.DateTime())
#     dateEnd = db.Column(db.DateTime())


# Initialize the SQLAlchemy data store and Flask-Security.
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)
labSessionDatastore = LabSessionDatastore(db, LabSession)
labUserDatastore = LabUserDatastore(db, LabUser)
labUserSessionDatastore = LabUserSessionDatastore(db, LabUserSession)

from sqlalchemy import event

@event.listens_for(Base.metadata, 'after_create')
def receive_after_create(target, connection, tables, **kw):
    "listen for the 'after_create' event"
    if tables:
        print('A table was created')
    else:
        print('A table was not created')

# Executes before the first request is processed.
@app.before_first_request
def before_first_request():

    db.init_app(app)
    # Create any database tables that don't exist yet.
    db.drop_all(app=app)
    db.create_all()

    # Create the Roles "admin" and "end-user" -- unless they already exist
    user_datastore.find_or_create_role(name='admin', description='Administrator')
    user_datastore.find_or_create_role(name='end-user', description='End user')

    # Create two Users for testing purposes -- unless they already exists.
    # In each case, use Flask-Security utility function to encrypt the password.
    encrypted_password = utils.hash_password('password')
    if not user_datastore.get_user('someone@example.com'):
        user_datastore.create_user(email='someone@example.com', password=encrypted_password)
    if not user_datastore.get_user('admin@example.com'):
        user_datastore.create_user(email='admin@example.com', password=encrypted_password)


    #PM START
    sess = labSessionDatastore.create_labSession(sessionType='OPENLAB')
    dob = getDatetime("1973-09-22")
    dob2 = getDatetime("1953-01-01")
    fms = getDatetime("2014-01-01")
    fms2 = getDatetime("2016-01-01")
    user1 = labUserDatastore.create_labUser(name="Philippe", surname="MOREL", dateOfBirth=dob, email="morel.ph@free.fr",firstMsDay=fms)
    user2 = labUserDatastore.create_labUser(name="Guy", surname="DELLE VEDOVE", dateOfBirth=dob2, email="guydvd@free.fr",firstMsDay=fms)
    #PM END

    # Commit any database changes; the User and Roles must exist before we can add a Role to the User
    db.session.commit()

    sess = labSessionDatastore.get_labSession(1)
    print("session 1:",sess)
    sessions = labSessionDatastore.find_labSessions()
    for s in sessions:
        print("session ",s.id)

    labUserSessionDatastore.addlabUserSession(sess.id,user1.id,datetime.now())
    # Give one User has the "end-user" role, while the other has the "admin" role. (This will have no effect if the
    # Users already have these Roles.) Again, commit any database changes.
    user_datastore.add_role_to_user('someone@example.com', 'end-user')
    user_datastore.add_role_to_user('admin@example.com', 'admin')
    db.session.commit()

    api.add_resource(SessionUsers, '/api/session_user')
    api.add_resource(LabUsers, '/api/lab_user')
    # WARNING must be called after all add_resource calls
    api.init_app(app)

# Path for all the static files (compiled JS/CSS, etc.)
@app.route("/<path:path>")
def home(path):
    return send_from_directory('client/public', path)


# Displays the home page.
@app.route('/')
# Users must be authenticated to view the home page, but they don't have to have any particular role.
# Flask-Security will display a login form if the user isn't already authenticated.
@login_required
def index():
    return render_template('index.html')

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    for user in users:
        if user["username"] == username and user["password"] == password:
            user_model = User()
            user_model.id = user["id"]
            login_user(user_model)
            return jsonify({"login": True})

    return jsonify({"login": False})


@app.route("/api/data", methods=["GET"])
@login_required
def user_data():
    user = get_user(current_user.id)
    return jsonify({"username": user["username"]})


@app.route("/api/getsession")
def check_session():
    if current_user.is_authenticated:
        return jsonify({"login": True})

    return jsonify({"login": False})


@app.route("/api/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"logout": True})


# Customized User model for SQL-Admin
class UserAdmin(sqla.ModelView):

    # Don't display the password on the list of Users
    column_exclude_list = ('password',)

    # Don't include the standard password field when creating or editing a User (but see below)
    form_excluded_columns = ('password',)

    # Automatically display human-readable names for the current and available Roles when creating or editing a User
    column_auto_select_related = True

    # Prevent administration of Users unless the currently logged-in user has the "admin" role
    def is_accessible(self):
        return current_user.has_role('admin')

    # On the form for creating or editing a User, don't display a field corresponding to the model's password field.
    # There are two reasons for this. First, we want to encrypt the password before storing in the database. Second,
    # we want to use a password field (with the input masked) rather than a regular text field.
    def scaffold_form(self):

        # Start with the standard form as provided by Flask-Admin. We've already told Flask-Admin to exclude the
        # password field from this form.
        form_class = super(UserAdmin, self).scaffold_form()

        # Add a password field, naming it "password2" and labeling it "New Password".
        form_class.password2 = PasswordField('New Password')
        return form_class

    # This callback executes when the user saves changes to a newly-created or edited User -- before the changes are
    # committed to the database.
    def on_model_change(self, form, model, is_created):

        # If the password field isn't blank...
        if len(model.password2):

            # ... then encrypt the new password prior to storing it in the database. If the password field is blank,
            # the existing password in the database will be retained.
            model.password = utils.hash_password(model.password2)


# Customized Role model for SQL-Admin
class RoleAdmin(sqla.ModelView):

    # Prevent administration of Roles unless the currently logged-in user has the "admin" role
    def is_accessible(self):
        return current_user.has_role('admin')

# Initialize Flask-Admin
admin = Admin(app)

# Add Flask-Admin views for Users and Roles
admin.add_view(UserAdmin(User, db.session))
admin.add_view(RoleAdmin(Role, db.session))


# If running locally, listen on all IP addresses, port 8080
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int('8080'),
        debug=app.config['DEBUG']

    )
