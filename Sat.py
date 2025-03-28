import pysat

from pysat.card import *
from pysat.solvers import Glucose3
from pysat.solvers import Cadical195
#from myconfig import *

def make_new_clause(a : list) -> list:
    disjunkt = a[0: 250]
    for i in range(len(disjunkt)):
        disjunkt[i] *= -1
    return disjunkt

import time
def sat(cnf :str) -> list:
    start_time = time.time()
    print('reading clauses')

    clauses = eval(cnf)
    print('clauses have been read\n')
    read_time = time.time() - start_time
    print("--- reading %s seconds ---" % (read_time))

    c = Cadical195()
    for clause in clauses:
        c.add_clause(clause)
    
    counter = 0
    file1 = open("sat_results_test2.txt", "a")
    #while(c.solve()):
    counter += 1
    print(counter)
    print(c.solve())

    #file1 = open("sat_result.txt", "w")
    xs = c.get_model()
    ys = c.get_core()
    zs = c.get_proof()
    if (xs != None):
        s = '[' + ', '.join(str(x) for x in xs) + ']'
    else:
        s = None
    ans = ""
    if(s != None):
        ans = s
    else:
        ans = "UNSAT"
    #file1.write(ans)
    #file1.close()
    print(xs)
    print(ys)
    print(zs)

    solve_time = time.time() - read_time - start_time
    print("--- solving %s seconds ---" % (solve_time))
    return [ans, solve_time]
