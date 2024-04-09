import sqlite3
#import click
from flask import current_app, g, render_template, Blueprint, flash, request
import fslg

class datbase():
    def __init__(self, database):
        self.db = database
        self.conn = sqlite3.connect(database)
        self.cursor = self.conn.cursor()
        self.log = fslg.log('current.txt')
        self.log.initlog()


    # Read Data from DB
    def read_db_by_key(self, table, key, keyCol, dataCol):
        self.log.log("Reading database by key...")
        self.cursor.execute(f'''SELECT {dataCol} FROM {table} WHERE ("{key}" = {keyCol})''')
        data = self.cursor.fetchall()
        return data
    
    def read_db_all(self, table):
        self.log.log("Reading all from database...")
        self.cursor.execute(f'''SELECT * FROM {table} ORDER BY isActive DESC, hostShort ASC, hostname ASC, port ASC''')
        data = self.cursor.fetchall()
        return data
        
        # Write Data to DB
    def write_key_data(self, key, data):
        self.log.log("Writing to database...")
        self.cursor.execute(f"INSERT OR IGNORE INTO Keyed_Data (Key, Data) VALUES ('{key}', '{data}')")
        self.cursor.execute(f"UPDATE Keyed_Data SET Data = '{data}' WHERE ('{key}' = Key)")
        self.conn.commit()

    def add_server(self, hostname, port, isEnabled):
        try:
            self.log.log("Adding server to database...")
            hostShort = hostname.split('.')[-2]
            hostShort = hostShort.replace('https://', '')
            hostShort = hostShort.replace('http://', '')
            self.log.log("Creating hostshort index...")
            self.cursor.execute(f"INSERT OR IGNORE INTO Server_Bindings (hostname, port, isActive, hostShort) VALUES ('{hostname}', '{port}', '{isEnabled}', '{hostShort}')")
            self.cursor.execute(f"UPDATE Server_Bindings SET port='{port}' WHERE hostname='{hostname}'")
            self.cursor.execute(f"UPDATE Server_Bindings SET isActive='{isEnabled}' WHERE hostname='{hostname}'")
            self.cursor.execute(f"UPDATE Server_Bindings SET hostShort='{hostShort}' WHERE hostname='{hostname}'")
            self.conn.commit()
            self.log.log("Added server to database")
        except:
            self.log.log("Hostshort not createable")
            self.log.fatal()
    
    def update_server(self, hostname, port, isEnabled):
        #try:
            self.log.log("Updating server database...")
            hostShort = hostname.split('.')[-2]
            hostShort = hostShort.replace('https://', '')
            hostShort = hostShort.replace('http://', '')
            self.log.log("Creating hostshort index...")
            self.cursor.execute(f"UPDATE Server_Bindings SET port='{port}' WHERE hostname='{hostname}'")
            self.cursor.execute(f"UPDATE Server_Bindings SET isActive='{isEnabled}' WHERE hostname='{hostname}'")
            self.cursor.execute(f"UPDATE Server_Bindings SET hostShort='{hostShort}' WHERE hostname='{hostname}'")
            self.conn.commit()
            self.log.log("Updated database")
        #except:
            #error = f"{hostname} could not be found"
    
    def delete_server(self, hostname):
        self.log.log("Removing server from database...")
        try:
            self.cursor.execute(f"DELETE FROM Server_Bindings WHERE (hostname = '{hostname}')")
            self.conn.commit()
            self.log.log(f"Server {hostname} removed")
        except:
            error = f"{hostname} could not be found"

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

# Init DB
def init_db():
    #try:
        db = get_db()
        with current_app.open_resource('make_tables.sql') as f:
            db.executescript(f.read().decode('utf8'))
    #except sqlite3.OperationalError:
        #click.echo('Database already exists. Use --force to force (overwrites database)')
        #exit()

def init_db_forced():
    inp = input('WARNING: Delete all data in database (Y/n)? ')
    if (inp == 'N') or (inp == 'n'):
        #click.echo('Aborted!')
        exit()
    db = get_db()
    with current_app.open_resource('make_tables_forced.sql') as f:
        db.executescript(f.read().decode('utf8'))

def init_db_forced_no_check():
    db = get_db()
    with current_app.open_resource('make_tables_forced.sql') as f:
        db.executescript(f.read().decode('utf8'))

#@click.command('init-db')
#@click.option("--force", is_flag=True)
#@click.option("--y", is_flag=True)
#def init_db_command(force, y):
    #"""Clear the existing data and create new tables."""
    #if(force and y):
        #init_db_forced_no_check()
    #elif force:
        #init_db_forced()
    #else:
        #init_db()
    #click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    #app.cli.add_command(init_db_command)