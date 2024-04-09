DROP TABLE IF EXISTS Keyed_Data;
DROP TABLE IF EXISTS Server_Bindings;

CREATE TABLE Keyed_Data (
  Key TEXT UNIQUE,
  Data TEXT UNIQUE NOT NULL
);

CREATE TABLE Server_Bindings (
  hostname TEXT UNIQUE,
  port INTEGER NOT NULL,
  isActive INTEGER NOT NULL,
  hostShort TEXT
);

CREATE TABLE PID (
  Data TEXT UNIQUE NOT NULL
);

INSERT INTO Keyed_Data (Key, Data) VALUES ('path_to_launcher', '/Applications/CurseForge.app');

INSERT OR IGNORE INTO Server_Bindings (hostname, port, isActive, hostShort) VALUES ('mc1.foxservers.net', 8000, 1, 'foxservers');
INSERT OR IGNORE INTO Server_Bindings (hostname, port, isActive, hostShort) VALUES ('mc2.foxservers.net', 8000, 0, 'foxservers');
INSERT OR IGNORE INTO Server_Bindings (hostname, port, isActive, hostShort) VALUES ('mc3.foxservers.net', 7000, 1, 'foxservers');
INSERT OR IGNORE INTO Server_Bindings (hostname, port, isActive, hostShort) VALUES ('mc4.foxservers.net', 6000, 1, 'foxservers');
