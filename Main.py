import os
import sys
from Reduction import *
from Reduction2 import *
from Functions import *
from Sat import *
import time

def check_input(n: int, k: int, d: int) -> bool:
    if (n < k or n < d or n == 0 or k == 0):
        print("incorrect input\n")
        return False
	
    if (n == k):
        if (d <= 1):
            print("it's Identity matrix of size n\n")
        else:
            print("it's Identity matrix of size n. Current d  cannot be bigger than 1\n")
        return False
	
    return True

''' работа с файлами'''

def prepare_file():
    file = open("sat_result.txt", "w")
    file.write('WAITING SAT')
    file.close()

def main():
    #n, k, d, mode # mode 0 -- без модификаторов, mode 1 -- продолжение прошлого запроса(d увеличилось), mode 2 -- проверка существующего решения(toDo)
    
    #terminal input
    #nkd = input().split(" ")
    
    #console
    nkd = sys.argv
    nkd = nkd[1:]
    
    n = int(nkd[0])
    k = int(nkd[1])
    d = int(nkd[2])
   
    if check_input(n, k, d): 
        # for curr_border in range(1, 201):
        start_time = time.time()
        #prepare_file()
        # part 1 make CNF
        
        cnf = reduction(n, k, d, 0, 20)#, curr_border)
        print(cnf)
        red_time = time.time() - start_time
        saved_redtime = "--- reduction time " + str(red_time) + " seconds ---"
        print(saved_redtime)
        print('\nStarting SAT-solving\n')
        #waiting = input()
        sat_res = sat(cnf)
        str0 = sat_res[0]
        sat_time = sat_res[1]
        #part 2 get results from SAT
        #file_in = open('sat_result.txt', "r")
        #str1 = ""
        #str1 = file_in.readline()
            #file_read
        #file_in.close()
        flag = False

        #part 3 check results //ToDo move to another file
        if (str0 != 'UNSAT' and check_inequivs(str0)):
            if (check_enumeration(str0, n, k, d)):
                print("It's really work correct!\n")
                flag = True
            else:	
                print("Oh, my bad, it's not work!(\n")
        else:
            print("something wrong!!!\n")
        print(saved_redtime)
        print("--- solving %s seconds ---" % (sat_time))
        ans_time = time.time() - start_time
        print("--- answer found in %s seconds ---" % (ans_time))
        time_res = str(red_time) + "\n" + str(sat_time) + "\n" + str(ans_time)
        output_res_to_file("saved_answers/(" + str(n) + ", " + str(k) + ", " + str(d) + ")/time.txt", time_res);
        if (flag):
            #part 4 create code matrix
            res = print_matrix(n, k)
            print(res)

            #part 5 save matrix
            output_res_to_file("saved_answers/(" + str(n) + ", " + str(k) + ", " + str(d) + ")/code.txt", res)
            #output_res_to_file("(" + str(n) + ", " + str(k) + ", " + str(d) + ")_omg_we_found_this_code.txt", res)
            print(get_vars_count())
    return 0

if __name__ == "__main__":
    main()
