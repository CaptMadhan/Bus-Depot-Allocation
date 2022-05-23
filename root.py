from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk, filedialog
import sqlite3 as base
import sys
import numpy as np
import pandas as pd
from pip import main

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
    #tf = open('test.txt', 'r')
    #data = tf.read()
    #txtarea.insert(END, data)
    show_data()
    #tf.close()

def clear_data():
    for item in weights_tree.get_children():
      weights_tree.delete(item)

def show_data():
    sys.stdout = open("test.txt", "w")
    cursor.execute('''SELECT * FROM Data''')
    data = pd.DataFrame(cursor.fetchall())
    # Warehouse data only -->Change variables later
    ware = list(data.iloc[0, :])
    ware = ware[1:]

    ## Factory data only
    fact = list(data.iloc[:, 0])
    fact = fact[1:]

    ## Weights
    weights = np.array(data.iloc[1:, 1:])
    sys.stdout.close()
    table_from_df(pd.DataFrame(weights))


def table_from_df(data):
    for item in weights_tree.get_children():
        weights_tree.delete(item)
    weights_tree["column"] = list(data.columns)
    weights_tree["show"] = "headings"
    for column in weights_tree["column"]:
        weights_tree.column(column, anchor=CENTER)
        weights_tree.heading(column,text=column)
    df_rows = data.to_numpy().tolist()
    for row in df_rows:
        weights_tree.insert("","end",values=row)
    weights_tree.pack()


main_page = Tk()
main_page.title('Bus Depot Allocation')
main_page.configure(bg="#e7f0fd")
main_page.geometry("1500x800")
main_page['bg'] = '#000'
#txtarea = Text(main_page, width=180, height=20,bg="#e7f0fd")
#txtarea.grid(row=1, column=1, padx=50, pady=20)


#Style Code only START
style = ttk.Style()
style.layout('my.Treeview',
             [('Treeview.field', {'sticky': 'nswe', 'border': '2', 'children': [
                 ('Treeview.padding', {'sticky': 'nswe', 'children': [
                     ('Treeview.treearea', {'sticky': 'nswe'})
                     ]})
                 ]})
              ]) 
style.configure('my.Treeview.Heading', background='gray', font=('Arial Bold', 15))
#Style Code only END

#TreeView Code starts here
my_frame = Frame(main_page)
my_frame.pack(padx=80,pady=200)
weights_tree = ttk.Treeview(my_frame,show='headings', height=8, selectmode ='browse',style='my.Treeview')
weights_tree.place(x=25,y=45)

# Horizontal and Vertical Scrollbars start
vScroll =Scrollbar(my_frame)
vScroll.configure(command=weights_tree.yview)
weights_tree.configure(yscrollcommand=vScroll.set)
vScroll.pack(side= RIGHT, fill= BOTH)

hScroll=Scrollbar(my_frame, orient='horizontal')
hScroll.configure(command=weights_tree.xview)
weights_tree.configure(xscrollcommand=hScroll.set)
hScroll.pack(side=BOTTOM, fill='x')
show_data()
# Horizontal and Vertical Scrollbars END
#TreeView code ends here

# Variables Initialization
sys.stdout = open("test.txt", "w")
cursor.execute('''SELECT * FROM Data''')
data = pd.DataFrame(cursor.fetchall())
# Warehouse data only -->Change variables later
ware = list(data.iloc[0, :])
ware = ware[1:]

## Factory data only
fact = list(data.iloc[:, 0])
fact = fact[1:]

## Weights
weights = np.array(data.iloc[1:, 1:])
sys.stdout.close()
table_from_df(pd.DataFrame(weights))

upload=Button(main_page,text="Upload file",padx=20,pady=3,command=open_file).place(relx=0.4,rely=0.06)
display_data=Button(main_page,text="Display data",padx=20,pady=3,command=show_data).place(relx=0.5,rely=0.06)
clear_data=Button(main_page,text="clear data",padx=20,pady=3,command=clear_data).place(relx=0.6,rely=0.06)



main_page.state("zoomed")
mainloop()


