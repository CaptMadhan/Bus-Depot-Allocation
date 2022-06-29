from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk, filedialog
import sqlite3 as base
import sys
import tkinter
import numpy as np
import pandas as pd
from pip import main
import Logic as compute
from datetime import datetime
from tkinter.messagebox import showerror

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
        cursor.execute('''SELECT * FROM Data''')
        previous_data = pd.DataFrame(cursor.fetchall())
        previous_data.to_sql('Backup_Data', data_base, if_exists='replace', index=False)
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
        except ValueError:
            messagebox.showerror('Error', 'File could not be opened')
        except FileNotFoundError:
            messagebox.showerror('Error', "File Not Found")
    sys.stdout.close()
    show_data()
    for item in result_tree.get_children():
      result_tree.delete(item)
    text1.set("Compute to get cost")
    text2.set("Compute to get allocation")
    download_button.place_forget()
    detailed_Result.place_forget()

def clear_data():
    for item in weights_tree.get_children():
      weights_tree.delete(item)
    for item in supply_tree.get_children():
      supply_tree.delete(item)
    for item in demand_tree.get_children():
      demand_tree.delete(item)
    for item in result_tree.get_children():
      result_tree.delete(item)
    text1.set("Compute to get cost")
    text2.set("Compute to get allocation")
    download_button.place_forget()
    detailed_Result.place_forget()

def show_data():
    global demand,supply,weights
    cursor.execute('''SELECT * FROM Data''')
    data = pd.DataFrame(cursor.fetchall())
    # Warehouse data only -->Change variables later
    demand = list(data.iloc[0, :])
    demand = demand[1:]

    ## Factory data only
    supply = list(data.iloc[:, 0])
    supply = supply[1:]

    ## Weights
    weights = np.array(data.iloc[1:, 1:])
    sys.stdout.close()
    table_from_df(pd.DataFrame(weights),weights_tree,pd.DataFrame(weights).columns)
    table_from_df(pd.DataFrame(demand),demand_tree,["Bus count"])
    table_from_df(pd.DataFrame(supply),supply_tree,["Depots size"])


def table_from_df(data,tree,columns):
    for item in tree.get_children():
        tree.delete(item)
    tree["column"] = list(columns)
    tree["show"] = "headings"
    for column in tree["column"]:
        tree.column(column, anchor=CENTER)
        tree.heading(column,text=column)
    df_rows = data.to_numpy().tolist()
    for row in df_rows:
        tree.insert("","end",values=row)
    tree.pack()

def allocate():
    sys.stdout = open("test.txt", "w")
    cursor.execute('''SELECT * FROM Data''')
    data = pd.DataFrame(cursor.fetchall())
    if chosen_choice.get() == "North-West rule":
        result_cost, result_alloc, ibfs,detailed_txt = compute.main_fun(data,2)
    #elif chosen_choice.get() == "Least-Cost Method":
    #    result_cost, result_alloc, ibfs,detailed_txt = compute.main_fun(data,3)
    else:
        result_cost, result_alloc, ibfs,detailed_txt = compute.main_fun(data,1)
    table_from_df(pd.DataFrame(result_alloc),result_tree,pd.DataFrame(result_alloc).columns)
    text1.set("Optimal Cost = "+ str(result_cost[0]))
    text2.set("IBFS = "+ str(ibfs))
    download_button.place(relx=0.35,rely=0.93)
    detailed_Result.place(relx=0.55,rely=0.93)

def download_result():
    cursor.execute('''SELECT * FROM Data''')
    data = pd.DataFrame(cursor.fetchall())
    if chosen_choice.get() == "North-West rule":
        result_cost, result_alloc, ibfs,detailed_txt = compute.main_fun(data,2)
    #elif chosen_choice.get() == "Least-Cost Method":
    #    result_cost, result_alloc, ibfs,detailed_txt = compute.main_fun(data,3)
    else:
        result_cost, result_alloc, ibfs,detailed_txt = compute.main_fun(data,1)
    result_df = pd.DataFrame(result_alloc)
    download_filename = "Allocation"+datetime.now().strftime("%d-%m-%Y-%H-%M-%S")+".xlsx"
    #result_df.to_excel(download_filename)
    try:
        savefile = filedialog.asksaveasfilename(filetypes=(("Excel files", "*.xlsx"),("All files", "*.*") ))  
        result_df.to_excel(savefile + ".xlsx", index=False, sheet_name="download_filename")    
    except:
        showerror("Open Source File", "Failed to import file\n'%s'" % savefile)

def show_detailed_result():
    cursor.execute('''SELECT * FROM Data''')
    data = pd.DataFrame(cursor.fetchall())
    steps = Tk()
    steps.title('Detailed Steps')
    steps.configure(bg="#e7f0fd")
    steps.geometry("1500x800")
    v=Scrollbar(steps, orient='vertical')
    v.pack(side=RIGHT, fill='y')
    txtarea = Text(steps, width=180, height=200,bg="#e7f0fd",yscrollcommand=v.set)
    #txtarea.place(relx=0.5,rely=0.0)
    txtarea.pack(padx=40,pady=20)
    v.config(command=txtarea.yview)
    Font_tuple = ("Calibri", 20, "bold")
    txtarea.configure(font = Font_tuple)
    if chosen_choice.get() == "North-West rule":
        result_cost, result_alloc, ibfs,detailed_txt = compute.main_fun(data,2)
    #elif chosen_choice.get() == "Least-Cost Method":
    #    result_cost, result_alloc, ibfs,detailed_txt = compute.main_fun(data,3)
    else:
        result_cost, result_alloc, ibfs,detailed_txt = compute.main_fun(data,1)    
    txtarea.insert(END, detailed_txt)
    steps.state("zoomed")


main_page = Tk()
main_page.title('Bus Depot Allocation')
main_page.configure(bg="#e7f0fd")
main_page.geometry("1500x800")
main_page['bg'] = '#000'
#txtarea = Text(main_page, width=180, height=20,bg="#e7f0fd")
#txtarea.grid(row=1, column=1, padx=50, pady=20)
l = Label(main_page, text = "   Bangalore Metropolitan Transport Corporation    \nBus Depot Allocation")
l.config(font =("Courier", 18))
l.pack(pady = 20)
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
# Frame for Treeview
frame = Frame(main_page)
frame.pack(padx=60,pady=95)
# Weights
weights_tree = ttk.Treeview(frame,show='headings', height=8, selectmode ='browse',style='my.Treeview')
weights_tree.place()
# Horizontal and Vertical Scrollbars for weights start
vScroll =Scrollbar(frame)
vScroll.configure(command=weights_tree.yview)
weights_tree.configure(yscrollcommand=vScroll.set)
vScroll.pack(side= RIGHT, fill= BOTH)

hScroll=Scrollbar(frame, orient='horizontal')
hScroll.configure(command=weights_tree.xview)
weights_tree.configure(xscrollcommand=hScroll.set)
hScroll.pack(side=BOTTOM, fill='x')
# Horizontal and Vertical Scrollbars for weights END

# Demand
demand_tree = ttk.Treeview(frame,show='headings', height=8, selectmode ='browse',style='my.Treeview')
demand_tree.place(x=25,y=45)
# Horizontal and Vertical Scrollbars for demand start
vScroll =Scrollbar(frame)
vScroll.configure(command=demand_tree.yview)
demand_tree.configure(yscrollcommand=vScroll.set)
vScroll.pack(side= RIGHT, fill= BOTH)

hScroll=Scrollbar(frame, orient='horizontal')
hScroll.configure(command=demand_tree.xview)
demand_tree.configure(xscrollcommand=hScroll.set)
hScroll.pack(side=BOTTOM, fill='x')
# Horizontal and Vertical Scrollbars for demand END
# Supply
supply_tree = ttk.Treeview(frame,show='headings', height=8, selectmode ='browse',style='my.Treeview')
supply_tree.place(x=25,y=45)
# Horizontal and Vertical Scrollbars for demand start
vScroll =Scrollbar(frame)
vScroll.configure(command=supply_tree.yview)
supply_tree.configure(yscrollcommand=vScroll.set)
vScroll.pack(side= RIGHT, fill= BOTH)

hScroll=Scrollbar(frame, orient='horizontal')
hScroll.configure(command=supply_tree.xview)
supply_tree.configure(xscrollcommand=hScroll.set)
hScroll.pack(side=BOTTOM, fill='x')
# Horizontal and Vertical Scrollbars for demand END
show_data()

# Result Tree
rframe = Frame(main_page)
rframe.pack(padx=10,pady=7)
result_tree = ttk.Treeview(rframe,show='headings', height=8, selectmode ='browse',style='my.Treeview')
result_tree.place()
# Horizontal and Vertical Scrollbars for Result start
vScroll =Scrollbar(rframe)
vScroll.configure(command=result_tree.yview)
result_tree.configure(yscrollcommand=vScroll.set)
vScroll.pack(side= RIGHT, fill= BOTH)

hScroll=Scrollbar(rframe, orient='horizontal')
hScroll.configure(command=result_tree.xview)
result_tree.configure(xscrollcommand=hScroll.set)
hScroll.pack(side=BOTTOM, fill='x')
# Horizontal and Vertical Scrollbars for Result END
show_data()

#TreeView code ends here

# Variables Initialization
sys.stdout = open("test.txt", "w")
cursor.execute('''SELECT * FROM Data''')
data = pd.DataFrame(cursor.fetchall())
# Warehouse data only -->Change variables later
demand = list(data.iloc[0, :])
demand = demand[1:]

## Factory data only
supply = list(data.iloc[:, 0])
supply = supply[1:]

## Weights
weights = np.array(data.iloc[1:, 1:])
sys.stdout.close()

table_from_df(pd.DataFrame(weights),weights_tree,pd.DataFrame(weights).columns)
table_from_df(pd.DataFrame(demand),demand_tree,["Bus count"])
table_from_df(pd.DataFrame(supply),supply_tree,["Depots size"])

weights_tree.pack()
demand_tree.pack(side=LEFT)
supply_tree.pack(side=RIGHT)
result_tree.pack()
options = [
    "Row-Minima method",
    "North-West rule",
    "Least-Cost Method"
]
chosen_choice = StringVar()
chosen_choice.set( "Row-Minima method" )
drop = OptionMenu( main_page , chosen_choice , *options )

upload=Button(main_page,text="Upload file",padx=20,pady=3,command=open_file).place(relx=0.325,rely=0.1)
display_data=Button(main_page,text="Display data",padx=20,pady=3,command=show_data).place(relx=0.425,rely=0.1)
clear_data_button=Button(main_page,text="clear data",padx=20,pady=3,command=clear_data).place(relx=0.525,rely=0.1)
compute_result=Button(main_page,text="Allocate",padx=20,pady=3,command=allocate).place(relx=0.625,rely=0.1)
drop.place(relx=0.455,rely=0.15)
Label(main_page,text="IBFS used -> ").place(relx=0.4,rely=0.155)

download_button = Button(main_page,text="Download Result",padx=20,pady=3,command=download_result)
detailed_Result = Button(main_page,text="Detailed Calculation",padx=20,pady=3,command=show_detailed_result)
text1 = tkinter.StringVar()
text1.set("Compute to get cost")
text2 = tkinter.StringVar()
text2.set("IBFS")
total_cost_text = Label(main_page,textvariable=text1,bg = "light cyan").place(relx=0.35,rely=0.675) 
IBFS_text = Label(main_page,textvariable=text2,bg = "light cyan").place(relx=0.35,rely=0.625)
allocate()

main_page.state("zoomed")
mainloop()


