import os
from flask import Flask, render_template, request, current_app, g, redirect, url_for
from flaskwebgui import FlaskUI
import fsdb
import fsc
import fslg

USE_UI = True

def debug_r(request):
    items = request.items()
    FILE = open('results.txt', 'w')
    for k,v in items:
        FILE.write(f'({k},{v})')
    FILE.close()

def debug_d(dict):
    FILE = open('dict.txt', 'w')
    FILE.write(str(dict['hostname']))
    FILE.write("\n")
    FILE.write(str(dict['port']))
    FILE.write("\n")
    FILE.write(str(dict['isEnabled']))
    FILE.write("\n")
    FILE.write(str(dict['update']))
    FILE.write("\n")
    FILE.write(str(dict['delete']))
    FILE.write("\n")
    FILE.close()

def debug_d2(dict):
    FILE = open('dict.txt', 'w')
    FILE.write(str(dict['hostname']))
    FILE.write("\n")
    FILE.write(str(dict['port']))
    FILE.write("\n")
    FILE.write(str(dict['isEnabled']))
    FILE.write("\n")
    FILE.write(str(dict['add']))
    FILE.write("\n")
    FILE.close()

def debug_d3(dict):
    FILE = open('dict.txt', 'w')
    FILE.write(str(dict['path']))
    FILE.write("\n")
    FILE.write(str(dict['update']))
    FILE.close()

def create_app():
    log = fslg.log('current.txt')
    log.initlog(True) # Wipes log on startup
    database = 'FoxServers_Connect.sqlite3'
    log.log(f"Creating database for app")
    app = Flask(__name__, instance_relative_config=True)
    ui = FlaskUI(app=app, server='flask', port=5000, width=550, height=400)
    log.log(f"Defining app constructs")
    app.config.from_mapping(
            SECRET_KEY="replace before deployment",
            DATABASE=os.path.join(app.instance_path, database),
            ERRORS = [],
        )
    try:
        os.makedirs(app.instance_path)
        log.log(f"Creating instance path... Success")
    except OSError:
        log.log(f"Path already found, skipping creation")
    except:
        log.log(f"Creating instance path... Failure")
        log.fatal()

    try:
        app.app_context().push()
        fsdb.init_db()
        log.log(f"Creating database... sucess")
    except:
        log.log(f"Database already exists, no initialize needed")

    log.log(f"Initializing CloudFlared wrapper...")
    conn = fsc.autoLauncher(current_app.config['DATABASE'])
    conn.checkCloudflared()

    log.log(f"Killing processes on launch: ")
    conn._killProcesses(VERBOSE=False)

    @app.route('/')
    def send_to_home():
        log.log(f"Redirect home")
        return redirect(url_for('home'))

    @app.route('/home')
    def home():
        log.log(f"Reading database")
        datbase = fsdb.datbase(current_app.config['DATABASE'])
        path = datbase.read_db_by_key('Keyed_Data', 'path_to_launcher', 'Key', 'Data')
        try:
            print(path[0][0])
            log.log(f"Path to launcher exists...")
        except:
            path = [['']]
            log.log(f"Path to launcher is not set, setting to default NoneValue")
        log.log(f"Reading server bindings from database...")
        temp = datbase.read_db_all('Server_Bindings')
        all_data = []
        for i in temp:
            Server = i[0]
            Port = i[1]
            if(i[2] == 1):
                isActive = 'checked'
            else:
                isActive = None
            serverTuple = (Server, Port, isActive)
            log.log(f"Found server: {serverTuple[0]}:{serverTuple[1]}, {serverTuple[2]}")
            all_data.append(serverTuple)
        log.log(f"Rendering data to UI...")
        return render_template('index.html', path=path[0][0], server_data=all_data, errors=app.config['ERRORS'])

    @app.route('/updateEntry',methods = ['POST', 'GET'])
    def updateEntry():
        if request.method == 'POST':
            log.log(f"Request Received")
            items = request.form.items()
            #debug_r(request.form)
            log.log(f"Mapping k,v pairs...")
            tempdict={"hostname":None,"port":None, "isEnabled":'off', "update":None, "delete":None}
            for k,v in items:
                log.log(f"Mapping {k} to {v}", 1)
                tempdict[k] = v
            #debug_d(tempdict)
            log.log(f"Opening database")
            datbase = fsdb.datbase(current_app.config['DATABASE'])
            if(str(tempdict['update']) == 'update'):
                hostname = tempdict['hostname']
                port = tempdict['port']
                isEnabled = tempdict['isEnabled']
                log.log(f"Got update request for {hostname}:{port}, {isEnabled}")
                if isEnabled=='on':
                    isEnabled = 1
                else:
                    isEnabled = 0
                datbase.update_server(hostname, port, isEnabled)
                log.log(f"Database updated")
            if(str(tempdict['delete']) == 'delete'):
                id = tempdict['hostname']
                log.log(f"Got delete request for {id}")
                datbase.delete_server(id)
            return redirect(url_for('home'))
        
    @app.route('/addEntry',methods = ['POST', 'GET'])
    def addEntry():
        if request.method == 'POST':
            log.log(f"Request Received")
            items = request.form.items()
            #debug_r(request.form)
            tempdict={"hostname":None,"port":None, "isEnabled":'off', "add":None}
            log.log(f"Mapping k,v pairs...")
            for k,v in items:
                log.log(f"Mapping {k} to {v}", 1)
                tempdict[k] = v
            #debug_d2(tempdict)
            log.log(f"Opening Database...")
            datbase = fsdb.datbase(current_app.config['DATABASE'])
            if(str(tempdict['add']) == 'add'):
                hostname = tempdict['hostname']
                port = tempdict['port']
                isEnabled = tempdict['isEnabled']
                log.log(f"Adding {hostname}:{port}, {isEnabled}")
                if isEnabled=='on':
                    isEnabled = 1
                else:
                    isEnabled = 0
                datbase.add_server(hostname, port, isEnabled)
            return redirect(url_for('home'))
        
    @app.route('/updatePath',methods = ['POST', 'GET'])
    def updatePath():
        app.config['ERRORS'] = []
        if request.method == 'POST':
            log.log(f"Request Recieved")
            items = request.form.items()
            #debug_r(request.form)
            log.log(f"Mapping k,v pairs...")
            tempdict={"path":None,"update":None}
            for k,v in items:
                log.log(f"Mapping {k} to {v}", 1)
                tempdict[k] = v
            #debug_d3(tempdict)
            datbase = fsdb.datbase(current_app.config['DATABASE'])
            if(str(tempdict['update']) == 'update'):
                log.log(f"Updating path: {tempdict['path']}")
                datbase.write_key_data('path_to_launcher', tempdict['path'])
            return redirect(url_for('home'))

    @app.route('/connect',methods = ['POST', 'GET'])
    def connect():
        app.config['ERRORS'] = []
        if request.method == 'POST':
            log.log(f"Request Received")
            conn = fsc.autoLauncher(current_app.config['DATABASE'])
            items = request.form.items()
            #debug_r(request.form)
            tempdict={"connect":None,"disconnect":None}
            log.log(f"Mapping k,v pairs...")
            for k,v in items:
                log.log(f"Mapping {k} to {v}")
                tempdict[k] = v
            if(str(tempdict['connect']) == 'connect'):
                log.log(f"Connecting...")
                errors = conn.openConnections(VERBOSE=False)
                app.config['ERRORS'] = errors
                conn.openLauncher()
            if(str(tempdict['disconnect']) == 'disconnect'):
                log.log(f"Disconnecting...")
                print("Disconnect")
                conn._killProcesses(VERBOSE=False)
        return redirect(url_for('home'))
    
    fsdb.init_app(app)

    if __name__ == '__main__':
        print(app.root_path)
        if USE_UI:
            ui.run()
        else:
            app.run()
    
    return app

create_app()