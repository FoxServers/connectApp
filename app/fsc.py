import os
import time
import signal
import subprocess
import sqlite3
from pathlib import Path
from shutil import which
import fslg

class autoLauncher:
    def __init__(self, database):
        self.processes = []
        self.database = database
        self.conn = sqlite3.connect(self.database)
        self.cursor = self.conn.cursor()
        self.full_path = None
        self.app_name = None
        self.app_name_short = None
        self.app_process = None

        self.log = fslg.log('current.txt')
        self.log.initlog()

    def _isInstalled(self, tool):
        if which(tool) is not None:
            self.log.log("Checking installation... Found", 1)
            return True
        else:
            self.log.log("Checking installation... Not Found", 1)
            raise Exception(f"{tool} not found")
        
    def _installCloudflaredWinget(self, VERBOSE = False):
        isWinget = False
        isCloudflared = False
        try:
            if VERBOSE: print("     Attempting to get cloudflared from Winget")
            self._isInstalled("winget")
            isWinget = True
            subprocess.run("winget install --id Cloudflare.cloudflared", shell=True, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                self._isInstalled("cloudflared")
                isCloudflared = True
            except BaseException:
                None
        except BaseException:
            if VERBOSE: print("     Winget not detected on current system")
        return isWinget, isCloudflared
        
    def _installCloudflaredBrew(self, VERBOSE = False):
        isBrew = False
        isCloudflared = False
        try:
            if VERBOSE: print("     Attempting to get cloudflared from Brew")
            self._isInstalled("brew")
            isBrew = True
            subprocess.run('brew install cloudflared', shell=True, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                self._isInstalled("cloudflared")
                isCloudflared = True
            except:
                None
        except BaseException:
            if VERBOSE: print("     Brew not installed on current system")
        return isBrew, isCloudflared

    def _installCloudflared(self, VERBOSE = False):
        isSupported = False
        isInstalled = False
        print("Installing cloudflared...")
        isSupported, isInstalled = self._installCloudflaredWinget(VERBOSE)
        isSupported, isInstalled = self._installCloudflaredBrew(VERBOSE)
        if not isSupported:
            print("Platform not supported for automatic updates, please install brew or winget")
        elif not isInstalled:
            print("cloudflared did not install successfully")
        else:
            print("cloudflared installed successfully!")

    def _updateCloudflaredWinget(self, VERBOSE = False):
        self.log.log("Updating via winget...", 1)
        isWinget = False
        isCloudflared = False
        try:
            if VERBOSE: print("     Attempting to update cloudflared from Winget")
            self.log.log("Checking Winget is installed...", 1)
            self._isInstalled("winget")
            isWinget = True
            self.log.log("Getting Cloudflared...", 1)
            subprocess.run("winget upgrade --id Cloudflare.cloudflared", shell=True, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                self.log.log("Checking Installation...", 1)
                self._isInstalled("cloudflared")
                isCloudflared = True
            except BaseException:
                self.log.log("Installation failed", 1)
        except BaseException:
            self.log.log("Winget is not installed on current system", 1)
            if VERBOSE: print("     Winget not detected on current system")
        return isWinget, isCloudflared
        
    def _updateCloudflaredBrew(self, VERBOSE = False):
        self.log.log("Updating via Brew", 1)
        isBrew = False
        isCloudflared = False
        try:
            if VERBOSE: print("     Attempting to update cloudflared from Brew")
            self.log.log("Checking Brew is installed", 1)
            self._isInstalled("brew")
            isBrew = True
            subprocess.run('brew upgrade cloudflared', shell=True, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                self.log.log("Checking installation...", 1)
                self._isInstalled("cloudflared")
                isCloudflared = True
            except:
                self.log.log("Installation failed", 1)
        except BaseException:
            self.log.log("Brew is not on current system", 1)
            if VERBOSE: print("     Brew not installed on current system")
        return isBrew, isCloudflared

    def _updateCloudflared(self, VERBOSE = False):
        self.log.log("Updating installation...", 1)
        isSupported = False
        isInstalled = False
        print("Updating cloudflared...")
        isSupported, isInstalled = self._updateCloudflaredWinget(VERBOSE)
        isSupported, isInstalled = self._updateCloudflaredBrew(VERBOSE)
        if not isSupported:
            self.log.log("Platform is not supported for automatic updates, please install brew or winget", 1)
            print("Platform not supported for automatic updates, please install brew or winget")
        elif not isInstalled:
            self.log.log("Cloudflared did not update successfully", 1)
            print("cloudflared did not update successfully")
        else:
            self.log.log("Cloudflared updated successfully", 1)
            print("cloudflared installed successfully!")

    def checkCloudflared(self, UPDATE = True, VERBOSE = False):
        self.log.log("Checking installation...")
        try:
            self._isInstalled("cloudflared")
            if UPDATE: self._updateCloudflared(VERBOSE= VERBOSE)
        except:
            self._installCloudflared(VERBOSE = VERBOSE)

    def _pullServers(self):
        self.log.log("Reading servers from database", 1)
        table = "Server_Bindings"
        self.cursor.execute(f'''SELECT * FROM "{table}" ORDER BY isActive DESC, hostShort ASC, hostname ASC, port ASC''')
        servers = self.cursor.fetchall()
        if len(servers) == 0:
            self.log.log("No servers found", 1)
            return None
        return servers
    
    def _pushPID(self, VERBOSE=False):
        self.log.log(f"Pushing process onto 'heap'", 1)
        for pid in self.processes:
            if VERBOSE: print(pid.pid)
            self.cursor.execute(f'''INSERT OR IGNORE INTO PID (Data) VALUES ('{pid.pid}')''')
            self.conn.commit()
        self._popProcesses()

    def _getPID(self, VERBOSE=False):
        self.log.log(f"Reading current PIDs from 'heap'", 1)
        self.cursor.execute(f'''SELECT * FROM PID''')
        data = self.cursor.fetchall()
        for pid in data:
            if VERBOSE: print(pid)
            self.processes.append(pid)

    def _popPID(self, VERBOSE=False):
        self.log.log(f"Removing PID from heap...", 1)
        self._getPID(VERBOSE=VERBOSE)
        for pid in self.processes:
            self.log.log(f"Removed {pid[0]}", 1)
            if VERBOSE: print(pid[0])
            self.cursor.execute(f'''DELETE FROM PID WHERE (Data = '{pid[0]}')''')
            self.conn.commit()
        self._popProcesses()

    def openConnections(self, VERBOSE=False):
        self.log.log("Opening Connections...")
        time.sleep(1)
        errors = []
        if VERBOSE: print("Connecting to servers:")
        for output in self._pullServers():
            hostname = output[0]
            port = output[1]
            isActive = output[2]
            if isActive:
                if VERBOSE: print(hostname, port)
                try:
                    process = subprocess.Popen(f"cloudflared access tcp --hostname {hostname} --url 127.0.0.1:{port}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    output, error = process.communicate(timeout=0.1)
                    error = str(error)
                    if "address already in use" in error:
                        error = "Address already in use"
                    if "permission denied" in error:
                        error = "Permission denied, port is taken by other process"
                    errorMessage = str(f'Error: Could not connect to {hostname} on {port}. {error}.')
                    errors.append(errorMessage)
                    self.log.log(f"Error connecting to {hostname}:{port}, {errorMessage}", 1)
                except:
                    self.log.log(f"Created connection to {hostname}:{port}", 1)
                    print("Timeout")
                self.processes.append(process)
        self._pushPID(VERBOSE=VERBOSE)
        if VERBOSE: print("Done!")
        return errors
        

    def openLauncher(self, VERBOSE = False):
        self.log.log(f"Opening the launcher")
        if VERBOSE: print("Opening launcher...")
        table = "Keyed_Data"
        self.cursor.execute(f'''SELECT Data FROM {table} WHERE ("path_to_launcher" = Key)''')
        pulled_path = self.cursor.fetchall()
        self.log.log(f"Reading data...")
        if len(pulled_path) == 0:
            self.log.log(f"No path found", 1)
            return None
        self.full_path = pulled_path[0][0]
        if len(self.full_path) == 0:
            self.log.log(f"No path found", 1)
            return None
        self.app_name = self.full_path.split('/')[-1]
        if len(self.app_name) == 0:
            self.log.log(f"No valid app name", 1)
            return None
        self.app_name_short = self.app_name.split('.')[0]
        if len(self.app_name_short) == 0:
            self.log.log(f"No valid short app name", 1)
            return None
        try:
            self.log.log(f"Checking if open command is installed...")
            self._isInstalled('open')
            self.log.log(f"Opening Launcher...")
            subprocess.run(f'open {self.full_path}', shell=True)
            self.app_process = subprocess.run(f'pgrep -n {self.app_name_short}', shell=True, stdout=subprocess.PIPE)
        except:
            try:
                self.log.log(f"Checking if tasklist is installed...")
                self._isInstalled('tasklist')
                self.log.log(f"Opening Launcher...")
                subprocess.run(f'{self.app_name}', shell=True)
                self.app_process = subprocess.run(f'tasklist /nh /fi "IMAGENAME eq {self.app_name}"', shell=True, stdout=subprocess.PIPE)
            except:
                self.log.log(f"Could not open Launcher application, path is incorrect or open command undefined")
                print("Cannot find process id for application, autoclosing connections is not possible")

        if VERBOSE: print("Done!")
                

    def _waitProcesses(self, VERBOSE = False):
        self.log.log(f"Waiting processes...", 1)
        if VERBOSE: print("Waiting processes...")
        for process in self.processes:
            if VERBOSE: print(process.pid)
            process.wait()
        if VERBOSE: print("Done")

    def _popProcesses(self):
        self.log.log(f"Removing process from memory", 1)
        for process in self.processes:
            self.processes.remove(process)

    def _killProcesses(self, VERBOSE = False):
        self.log.log(f"Stopping processes...", 1)
        self._getPID(VERBOSE=True)
        for pid in self.processes:
            if VERBOSE: print(int(pid[0]))
            try:
                os.kill(int(pid[0]), signal.SIGTERM)
                self.log.log(f"Killed {pid[0]}", 1)
            except:
                self.log.log(f"Could not find process {pid[0]}", 1)
        self._popPID(VERBOSE=True)

    def quit(self):
        self.log.log(f"Quitting Processes...", 1)
        self._killProcesses()
        exit()


