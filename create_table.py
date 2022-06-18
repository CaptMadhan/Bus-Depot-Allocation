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