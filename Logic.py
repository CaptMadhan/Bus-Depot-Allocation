import numpy as np

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
    global IBFS
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
    return ibfs

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
    for p, v in ws:
        if v > 0: return True
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

def loop_pivoting(bfs, loop):
    #print("thissssss",bfs)
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
        
    return new_bfs

def transportation_method(supply, demand, costs, penalties = None):
    balanced_supply, balanced_demand, balanced_costs = get_balanced(
        supply, demand, costs
    )
    def inner(bfs):
        us, vs = get_us_and_vs(bfs, balanced_costs)
        ws = get_ws(bfs, balanced_costs, us, vs)
        if can_be_improved(ws):
            ev_position = get_entering_variable_position(ws)
            loop = get_loop([p for p, v in bfs], ev_position)
            return inner(loop_pivoting(bfs, loop))
        return bfs
    
    basic_variables = inner(row_MinimaIBFS(balanced_supply, balanced_demand,costs))
    ans = np.zeros((len(costs), len(costs[0])))
    for (i, j), v in basic_variables:
        ans[i][j] = int(v)
    return ans

def get_total_cost(costs, ans):
    total_cost = 0
    for i, row in enumerate(costs):
        for j, cost in enumerate(row):
            total_cost += cost * ans[i][j]
    return total_cost

#import pandas as pd
#data = pd.read_excel("data-copy.xlsx", header=None)
def main_fun(data):
    m = data.shape[0]-1
    n = data.shape[1]-1
    demand = list(data.iloc[0, :])
    demand = demand[1:]

    supply = list(data.iloc[:, 0])
    supply = supply[1:]

    weights = np.array(data.iloc[1:, 1:])

    ans = transportation_method(supply, demand, weights)
    return get_total_cost(weights, ans),ans,IBFS
