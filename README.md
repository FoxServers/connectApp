# FoxServers connectApp Files

### Structure
`flaskr/`: Main app contents<br>
`flaskr/static/`: CSS Files<br>
`flaskr/templates/`: HTML Files<br>
`instance/`: Files contained when the app is running, database is stored here<br>
`.venv/`: Virtual environments for flask

## 
### Testing (Running Locally)

1) Install Python
2) `git clone https://github.com/FoxServers/connectApp/`
3) `cd connectApp`
4) Install virtualenv `pip install virtualenv`
5) Create a virtual environment to isolate packages from system: `virtualenv .venv`
6) Initialize that virtual environment:
    Windows
    `myenv\Scripts\activate`
    macOS and Linux
    `source myenv/bin/activate`
7) Install packages: `pip install -r requirements.txt`
8) Run the app: `python app/app.py`

9) if you want to reset the database, delete the .sqlite3 file out of the /instance folder
