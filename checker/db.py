import sqlite3
import pandas as pd
import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

    db = get_db()
    db.execute("delete from thilab_users;")

    col_names = ['surname','name','dob', 'isMember']
    # Use Pandas to parse the CSV file  
    csvData = pd.read_csv(current_app.open_resource('users.csv'),names=col_names, header=None)
    # Loop through the Rows
    for i,row in csvData.iterrows():
        db.execute("insert into thilab_users (name, surname, dateOfBirth, isMember) values (?,?,?,?);", (row['name'],row['surname'],row['dob'],row['isMember']))

    db.commit()
    
    users = db.execute("select name, surname, dateOfBirth from thilab_users;").fetchall()
    
    for user in users:
        print( "USER:" + user["name"] +"-"+user["surname"])



@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
