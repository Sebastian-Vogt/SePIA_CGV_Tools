import os
import msaccessdb
import sqlalchemy as sql
import urllib
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

data_dir = filedialog.askdirectory()
db_paths = [folder[0] + "\\" + file for folder in os.walk(data_dir) for file in folder[2] if file.endswith('.mdb')]

msaccessdb.create(data_dir + '\\globalPCM.mdb')
connection_string = (
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    r'DBQ=' + data_dir + '\\globalPCM.mdb;'
    r'ExtendedAnsiSQL=1;'
)
connection_uri = f"access+pyodbc:///?odbc_connect={urllib.parse.quote_plus(connection_string)}"
global_engine = sql.create_engine(connection_uri)
global_metadata = sql.MetaData(global_engine)

global_global_table = sql.Table('global_data', global_metadata,
                                sql.Column('CASEID', sql.String(255), primary_key=True, autoincrement=False),
                                sql.Column('DATETIME', sql.String(255)),
                                sql.Column('PARTICIP', sql.BigInteger),
                                sql.Column('SOLVER', sql.BigInteger),
                                sql.Column('GPSLAT', sql.Float),
                                sql.Column('GPSLON', sql.Float),
                                sql.Column('GPSELE', sql.Float))

global_participant_table = sql.Table('participant_data', global_metadata,
                                sql.Column('CASEID', sql.String(255)),
                                sql.Column('PARTID', sql.BigInteger, primary_key=True, autoincrement=False),
                                sql.Column('PARTTYPE', sql.BigInteger),
                                sql.Column('LENGTH', sql.Float),
                                sql.Column('WIDTH', sql.Float),
                                sql.Column('HEIGHT', sql.Float),
                                sql.Column('TRACKWIDTH', sql.Float),
                                sql.Column('WHEELBASE', sql.Float),
                                sql.Column('FRONTAXLEX', sql.Float),
                                sql.Column('WEIGHT', sql.Float),
                                sql.Column('COGX', sql.Float),
                                sql.Column('COGY', sql.Float),
                                sql.Column('COGZ', sql.Float),
                                sql.Column('IXX', sql.Float),
                                sql.Column('IYY', sql.Float),
                                sql.Column('IZZ', sql.Float))

global_dynamics_table = sql.Table('dynamics', global_metadata,
                                sql.Column('CASEID', sql.String(255), primary_key=True, autoincrement=False),
                                sql.Column('PARTID', sql.BigInteger, primary_key=True, autoincrement=False),
                                sql.Column('VARIATIONID', sql.BigInteger, primary_key=True, autoincrement=False),
                                sql.Column('TIME', sql.Float, primary_key=True, autoincrement=False),
                                sql.Column('POSX', sql.Float),
                                sql.Column('POSY', sql.Float),
                                sql.Column('POSZ', sql.Float),
                                sql.Column('POSPHI', sql.Float),
                                sql.Column('POSTHETA', sql.Float),
                                sql.Column('POSPSI', sql.Float),
                                sql.Column('VX', sql.Float),
                                sql.Column('VY', sql.Float),
                                sql.Column('VZ', sql.Float),
                                sql.Column('AX', sql.Float),
                                sql.Column('AY', sql.Float),
                                sql.Column('AZ', sql.Float),
                                sql.Column('MUE', sql.Float),
                                sql.Column('REC', sql.BigInteger))

global_specification_table = sql.Table('specification', global_metadata,
                                sql.Column('CASEID', sql.String(255), primary_key=True, autoincrement=False),
                                sql.Column('PARTID', sql.BigInteger, primary_key=True, autoincrement=False),
                                sql.Column('VARIATIONID', sql.BigInteger, primary_key=True, autoincrement=False),
                                sql.Column('TIME', sql.Float, primary_key=True, autoincrement=False),
                                sql.Column('SPECIFICATION', sql.Integer),
                                sql.Column('MANEUVER', sql.Integer),
                                sql.Column('APPROACH', sql.Integer))

global_global_table.create()
global_participant_table.create()
global_dynamics_table.create()
global_specification_table.create()

conn = global_engine.connect()
conn.execute(global_global_table.insert(), {"CASEID": '1',
                                            "DATETIME": 'sometime',
                                            "PARTICIP": 0,
                                            "SOLVER": 88888,
                                            "GPSLAT": 0.0,
                                            "GPSLON": 0.0,
                                            "GPSELE": 0.0})
querry = "INSERT INTO global_data ([CASEID], [DATETIME], [PARTICIP], [SOLVER], [GPSLAT], [GPSLON], [GPSELE]) VALUES ('2', 'sometime', 0, 88888, 0.0, 0.0, 0.0)"
conn.execute(querry)
conn.close()

#for db_path in db_paths:


