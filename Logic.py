import numpy as np
import threading
import os
import pandas as pd
import sqlite3 as base

detailed_info = ""
count = 0

def get_balanced(supply, demand, costs, penalties = None):
    total_supply = sum(supply)
    total_demand = sum(demand)
    
    if total_supply < total_demand:
        if penalties is None:
            raise Exception('Supply less than demand, penalties required')
        new_supply = supply + [total_demand - total_supply]
        new_costs = costs + [penalties]
        return new_supply, demand, new_costs
    if total_supply > total_demand:
        new_demand = demand + [total_supply - total_demand]
        new_costs = costs + [[0 for _ in demand]]
        return supply, new_demand, new_costs
    return supply, demand, costs

def row_MinimaIBFS(fact, ware, weights):
    global IBFS,detailed_info
    n = 0
    w = 0
    cost = 0
    ibfs = []
    arr = np.array([[0 for i in range(len(ware))] for i in range(len(fact))]) 
    while  n < len(fact) and w < len(ware):
        if max(ware) > fact[n]:
            w = ware.index(max(ware))
            arr[n][w] = fact[n]
            ware[w] -= fact[n]
            fact[n] = 0
            n += 1
        elif max(ware) < fact[n]:
            w = ware.index(max(ware))
            arr[n][w] = ware[w]
            fact[n] -= ware[w]
            ware[w] = 0
        else:
            w = ware.index(max(ware))
            arr[n][w] = max(ware)
            fact[n] = 0
            ware[w] = 0
            n += 1
            w + 1
    for i in range(len(arr)):
        for j in range(len(arr[0])):
            cost += arr[i][j] * weights[i][j]
            if(arr[i][j]!=0):
                ibfs.append(((i, j), arr[i][j])) 
    #print('total bfs cost is: ',cost)
    IBFS = cost
    detailed_info += "`"*100+"\n"
    detailed_info += "IBFS Allocation using Row-Minima Method: \n"+str(arr)+"\n"
    detailed_info += "IBFS Value = "+get_total_cost(weights, arr)[0]+"\n"
    detailed_info += "`"*100+"\n"
    return ibfs

def north_west_corner(supply, demand,costs):
    global IBFS,detailed_info
    supply_copy = supply.copy()
    demand_copy = demand.copy()
    i = 0
    j = 0
    cost =0
    bfs = []
    while len(bfs) < len(supply) + len(demand) - 1:
        s = supply_copy[i]
        d = demand_copy[j]
        v = min(s, d)
        supply_copy[i] -= v
        demand_copy[j] -= v
        bfs.append(((i, j), v))
        if supply_copy[i] == 0 and i < len(supply) - 1:
            i += 1
        elif demand_copy[j] == 0 and j < len(demand) - 1:
            j += 1
    arr = indexed_tuple_to_Array(bfs,len(demand),len(supply))
    for i in range(len(arr)):
        for j in range(len(arr[0])):
            cost += arr[i][j] * costs[i][j]
    IBFS = cost
    detailed_info += "`"*100+"\n"
    detailed_info += "IBFS Allocation using North-West rule: \n"+str(arr)+"\n"
    detailed_info += "IBFS Value = "+get_total_cost(costs, arr)[0]+"\n"
    detailed_info += "`"*100+"\n"
    return bfs

def leastCostIBFS(fact, ware,costs):
    #import sys
    global IBFS,detailed_info
    n = 0
    w = 0
    ibfs = 0
    weights = costs.copy()
    temp_weights = weights.copy()
    arr = np.array([[0 for i in range(len(ware))] for i in range(len(fact))])
    while sum(fact) > 0:
        n = np.argwhere(weights == np.min(weights))[0][0]
        w = np.argwhere(weights == np.min(weights))[0][1]
        if fact[n] > ware[w]:
            arr[n][w] = ware[w]
            fact[n] -= ware[w]
            ware[w] = 0
        elif fact[n] < ware[w]:
            arr[n][w] = fact[n]
            ware[w] -= fact[n]
            fact[n] = 0
        else:
            arr[n][w] = fact[n]
            fact[n] = 0
            ware[w] = 0
        weights[n][w] = 9999999
    for i in range(len(arr)):
        for j in range(len(arr[0])):
            ibfs += arr[i][j] * costs[i][j]
    result = []
    for i in range(len(arr)):
        for j in range(len(arr[0])):
             if arr[i][j] != 0:
                    result.append(((i,j),arr[i][j]))
    IBFS = ibfs
    detailed_info += "`"*100+"\n"
    detailed_info += "IBFS Allocation using Least-Cost method: \n"+str(arr)+"\n"
    detailed_info += "IBFS Value = "+get_total_cost(costs, arr)[0]+"\n"
    detailed_info += "`"*100+"\n"
    return result

def get_us_and_vs(bfs, costs):
    us = [None] * len(costs)
    vs = [None] * len(costs[0])
    us[0] = 0
    bfs_copy = bfs.copy()
    while len(bfs_copy) > 0:
        for index, bv in enumerate(bfs_copy):
            i, j = bv[0]
            if us[i] is None and vs[j] is None: continue
                
            cost = costs[i][j]
            if us[i] is None:
                us[i] = cost - vs[j]
            else: 
                vs[j] = cost - us[i]
            bfs_copy.pop(index)
            break
    #print(us,"\n" ,vs)
    return us, vs

def get_ws(bfs, costs, us, vs):
    ws = []
    for i, row in enumerate(costs):
        for j, cost in enumerate(row):
            non_basic = all([p[0] != i or p[1] != j for p, v in bfs])
            if non_basic:
                ws.append(((i, j), us[i] + vs[j] - cost))
    
    return ws

def can_be_improved(ws):
    global detailed_info
    for p, v in ws:
        if v > 0: 
            detailed_info+= "\t\tStill not OPTIMAL, moving towards OPTIMALITY\n"
            return True
    detailed_info+= "\t\tOPTIMAL, Stop here.\n"
    return False

def get_entering_variable_position(ws):
    ws_copy = ws.copy()
    ws_copy.sort(key=lambda w: w[1])
    return ws_copy[-1][0]

def get_possible_next_nodes(loop, not_visited):
    last_node = loop[-1]
    nodes_in_row = [n for n in not_visited if n[0] == last_node[0]]
    nodes_in_column = [n for n in not_visited if n[1] == last_node[1]]
    if len(loop) < 2:
        return nodes_in_row + nodes_in_column
    else:
        prev_node = loop[-2]
        row_move = prev_node[0] == last_node[0]
        if row_move: return nodes_in_column
        return nodes_in_row
    
def get_loop(bv_positions, ev_position):
    def inner(loop):
        if len(loop) > 3:
            can_be_closed = len(get_possible_next_nodes(loop, [ev_position])) == 1
            if can_be_closed: return loop
        
        not_visited = list(set(bv_positions) - set(loop))
        possible_next_nodes = get_possible_next_nodes(loop, not_visited)
        for next_node in possible_next_nodes:
            new_loop = inner(loop + [next_node])
            if new_loop: return new_loop
    
    return inner([ev_position])

def loop_pivoting(bfs, loop,m,n):
    global detailed_info
    even_cells = loop[0::2]
    odd_cells = loop[1::2]
    get_bv = lambda pos: next(v for p, v in bfs if p == pos)
    leaving_position = sorted(odd_cells, key=get_bv)[0]
    leaving_value = get_bv(leaving_position)
    
    new_bfs = []
    for p, v in [bv for bv in bfs if bv[0] != leaving_position] + [(loop[0], 0)]:
        if p in even_cells:
            v += leaving_value
        elif p in odd_cells:
            v -= leaving_value
        new_bfs.append((p, v))
    detailed_info +="+"*m*10 + "\n"
    detailed_info += "New Allocation: \n"+str(indexed_tuple_to_Array(new_bfs,m,n)) +"\n"
    detailed_info +="+"*m*10 + "\n"
    return new_bfs

def transportation_method(supply, demand, costs, choice):
    global detailed_info,count
    balanced_supply, balanced_demand, balanced_costs = get_balanced(
        supply, demand, costs
    )
    detailed_info += "Balanced Demand: "+str(balanced_demand)+"\nBalanced Supply: "+str(balanced_supply)+"\n"
    def inner(bfs,m,n):
        global detailed_info,count
        detailed_info += "-"*150+"\n"
        detailed_info += "ITERATION: "+str(count)+"\n"
        count +=1
        detailed_info += "-"*150+"\n"
        us, vs = get_us_and_vs(bfs, balanced_costs)
        ws = get_ws(bfs, balanced_costs, us, vs)
        detailed_info += "Ui: " + str(us)+"\nVj: "+str(vs)+"\n\nD(i,j): \n"+str(indexed_tuple_to_Array(ws,m,n))+"\t"
        if can_be_improved(ws):
            ev_position = get_entering_variable_position(ws)
            loop = get_loop([p for p, v in bfs], ev_position)
            return inner(loop_pivoting(bfs, loop,m,n),m,n)
        return bfs
    if choice == 1:
        basic_variables = inner(row_MinimaIBFS(balanced_supply, balanced_demand,costs),len(balanced_demand),len(balanced_supply))
    elif choice ==2:
        basic_variables = inner(north_west_corner(balanced_supply, balanced_demand,costs),len(balanced_demand),len(balanced_supply))
    elif choice ==3:
        basic_variables = inner(leastCostIBFS(balanced_supply, balanced_demand,costs),len(balanced_demand),len(balanced_supply))
    ans = np.zeros((len(costs), len(costs[0])))
    for (i, j), v in basic_variables:
        ans[i][j] = int(v)
    return ans

def indexed_tuple_to_Array(tup,m,n):
    arr = np.array([[0 for i in range(m)] for i in range(n)])
    for i in tup:
        arr[i[0][0]][i[0][1]] = i[1]
        #print(i[0][0],i[0][1],i[1])
    return arr

def get_total_cost(costs, ans):
    total_cost = 0
    detailed_info =""
    for i, row in enumerate(costs):
        for j, cost in enumerate(row):
            if ans[i][j] !=0:
                total_cost += cost * ans[i][j]
                detailed_info += "("+str(cost)+")*("+str(int(ans[i][j]))+") +"
    detailed_info = str(detailed_info[:-1]) + "= " + str(total_cost)
    return detailed_info,total_cost

#import pandas as pd
#data = pd.read_excel("data-copy.xlsx", header=None)
def main_fun(data,choice=1):
    delay_time = 5       # delay time in seconds
    global detailed_info,count
    detailed_info = ""
    count = 0
    def watchdog():
        data_base = base.connect("demo1.db")
        cursor = data_base.cursor()
        print("Data Incorrect")
        cursor.execute('''SELECT * FROM Backup_Data''')
        previous_data = pd.DataFrame(cursor.fetchall())
        previous_data.to_sql('Data', data_base, if_exists='replace', index=False)
        os._exit(1)

    alarm = threading.Timer(delay_time, watchdog)

    m = data.shape[0]-1
    n = data.shape[1]-1
    demand = list(data.iloc[0, :])
    demand = demand[1:]

    supply = list(data.iloc[:, 0])
    supply = supply[1:]

    weights = np.array(data.iloc[1:, 1:])
    alarm.start()
    ans = transportation_method(supply, demand, weights,choice)
    alarm.cancel()
    detailed_info += "="*100+"\n"
    detailed_info += "Final Allocation: \n"+str(ans) +"\n\nOptimal Cost = "+str(get_total_cost(weights, ans)[0])+"\n\n"
    detailed_info += "IBFS = "+str(IBFS)+"\n\nFinal Optimal Cost = "+str(get_total_cost(weights, ans)[1])+"\n\n"
    detailed_info +="Final Optimal Allocation: \n"+str(ans)+"\n"
    detailed_info += "="*100+"\n"
    
    #print(detailed_info)
    return get_total_cost(weights, ans),ans,IBFS,detailed_info
