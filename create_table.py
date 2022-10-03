'''
    create_table.py file is responsible to create table "Data" and "Backup_Data" if it did not exists.

    This file is run only in the initial stage i.e. when the project is run for the first time.
    "Data" table is used to store all the values needed for the project run, and is accessed when needed.
    "Backup_Data" table is used as a backup wherein no read or write operation is done, to secure from processing error. 
'''
import sqlite3 as base

# create or connect a data base
data_base = base.connect("demo1.db")

# create a cursor
cursor = data_base.cursor()

cursor.execute('''create table IF NOT EXISTS Data(
ELEMENTS INT
);''')

cursor.execute('''create table IF NOT EXISTS Backup_Data(
ELEMENTS INT
);''')
cursor.execute('''SELECT distinct tbl_name from sqlite_master order by 1;''')
for row in cursor.fetchall():
    print(row)
#cursor.execute('''SELECT * from Data''')
#for row in cursor.fetchall():
#    print(row)
cursor.execute('''SELECT * from Backup_Data''')
for row in cursor.fetchall():
    print(row)
#cursor.execute("DROP TABLE Data")