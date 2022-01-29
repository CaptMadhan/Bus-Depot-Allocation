from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import sqlite3 as base
import sys
import numpy as np
import pandas as pd

# create or connect a data base
data_base = base.connect("demo1.db")
# create a cursor
cursor = data_base.cursor()

# Define a function for opening the file


def open_file():
    sys.stdout = open("test.txt", "w")
    filename = filedialog.askopenfilename(title="Open a File", filetype=(("xlxs files", ".*xlsx"),
                                                                         ("All Files", "*.")))
    if filename:
        try:
            filename = r"{}".format(filename)
            df = pd.read_excel(filename, header=None)
            df.to_sql('Data', data_base, if_exists='replace', index=False)
            cursor.execute('''SELECT * FROM Data''')
            print("FILE UPLOADED ")
            print()
            print("VALUES IN THE FILE ARE:")
            print()
            for row in cursor.fetchall():
                print(row)
            # print(df)
        except ValueError:
            messagebox.showerror('Error', 'File could not be opened')
        except FileNotFoundError:
            messagebox.showerror('Error', "File Not Found")
    sys.stdout.close()
    tf = open('test.txt', 'r')
    data = tf.read()
    txtarea.insert(END, data)
    show_data()
    tf.close()


def show_data():
    sys.stdout = open("test.txt", "w")
    cursor.execute('''SELECT * FROM Data''')
    data = pd.DataFrame(cursor.fetchall())
    # Warehouse data only -->Change variables later
    ware = list(data.iloc[0, :])
    ware = ware[1:]

    # Factory data only
    fact = list(data.iloc[:, 0])
    fact = fact[1:]

    # Weights
    weights = np.array(data.iloc[1:, 1:])
    print()
    print("warehouse: \t", ware)
    print()
    print("Factory: \t", fact)
    print()
    print("Costs:\n", weights)
    print()
    sys.stdout.close()
    tf = open('test.txt', 'r')
    data = tf.read()
    txtarea.insert(END, data)
    tf.close()


main_page = Tk()
main_page.title('Bus Depot Allocation')
main_page.configure(bg="#e7f0fd")
main_page.geometry("1500x800")
main_page['bg'] = '#000'
txtarea = Text(main_page, width=140, height=20)
txtarea.grid(row=1, column=1, padx=50, pady=20)
upload=Button(main_page,text="Upload file",padx=20,pady=3,command=open_file)
upload.grid(row=1,column=1,pady=8,padx=20)
display_data=Button(main_page,text="Display data",padx=20,pady=3,command=show_data)
display_data.grid(row=2,column=1,pady=8,padx=20)
mainloop()