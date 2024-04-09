import platform
import datetime
import yaml

class log():
    def __init__(self, logfile):
        self.logfile = logfile
        self.verbose = None
        self.time = None

        with open('config.yaml', "r") as file:
            options = yaml.safe_load(file)
            self.verbose = options['debug_log']

    def initlog(self, wipelog=False):
        self.updateTime()
        if(self.verbose and wipelog):
            with open(self.logfile, "w") as log:
                log.write(f"[{self.time}]: ")
                log.write("Initialized Logfile...\n")
                log.write(f"[{self.time}]: ")
                log.write(f"Current system: {platform.platform()}\n")

    def updateTime(self):
        self.time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")


    def log(self, data, level=0):
        self.updateTime()
        if(self.verbose):
            with open(self.logfile, "a") as log:
                for i in range(level):
                    log.write("     ")
                log.write(f"[{self.time}]: {data}\n")

    def fatal(self):
        self.log(f"A fatal error has occured, exiting...")
        exit()