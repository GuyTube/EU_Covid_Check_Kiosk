from flask import Flask, render_template_string
from flask_security import Security, login_required, SQLAlchemySessionUserDatastore
from database import db_session, init_db
from models import User, Role

# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['SECURITY_PASSWORD_SALT'] = 'MyGrainOfSalt'
# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db_session,
                                                User, Role)
security = Security(app, user_datastore)

# Create a user to test with
@app.before_first_request
def create_user():
    print("CREATING USER")
    init_db()
    user_datastore.create_user(email='matt@nobien.net', password='password')
    db_session.commit()

# Views
@app.route('/')
@login_required
def home():
    return render_template_string('Here you go!')

if __name__ == '__main__':
    app.run()