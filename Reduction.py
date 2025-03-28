import os
from Functions import *

def reduction(n :int, k :int, d :int, mode :int, c :int) -> str: #, curr_border :int) -> str:
    #part 0 -- zeroing
    res = "[]"
    ans = ""

    #part 0.1 -- create n,k,d constants needed for code
    set0(n, k, d, mode)
    if not os.path.exists("saved_answers"): 
        os.mkdir("saved_answers")
    answer_file_name = "saved_answers/(" + str(n) + ", " + str(k) + ", " + str(d) + ")" #_wt5_only_step5"
    if not os.path.exists(answer_file_name): 
        os.mkdir(answer_file_name)
    base_variable_numbers = first_step_variables(n, k)
    verification_matrix_mode = True

    #part 1 -- if we already have code matrix add conditions (this will speed up SAT-Solver result generation) //toDo write after conditions generate
    if (mode == 2):
        res = check_m(n, k)
    res = "[]"
    #res = symmetry_breaking(n, k, d)#// +=
    #print(res, "\n")

    #part 2 -- create conditions
    step = 1
    while(d > step and step <= k):
        print("step %i:" % step)
        ans = ""
        #part 2.1 -- create new variables and equivalent conditions for them 
        # a(step)_i1i2..i(step)_j ≡ a(step-1)_i1i2..i(step-1)_j ⊕ a1_i(step)_j
        if (step > 1):
            ans = generate_equi(n, k, d, step, False)
            res = res[0 : -1] + ",\n" + ans[2:]

        #part 2.2 -- create condition, that sum in a row smaller then d 
        # Σ[j = 1..n-k](a(step)_i1.i2..i(step)_j) ≥ d - step
        ans = generate_cnf_inequalities(n, k, d, step, verification_matrix_mode)
        if (res != "[]"):
            res = res[0 : -1] + ",\n]"
        res = res[0 : -1] + ans[2 :]
        step += 1
    ### #ans = experiment_generate_cnf_inequalities(n, k, d, step, verification_matrix_mode, curr_border)
    #if (mode == 1):
    #    output_res_to_file("myconfig2_extra.py", "clauses2 = " + res)
    #else:
    #    output_res_to_file("myconfig.py", "dir_name = \"" + answer_file_name + "/sat_result.txt\"\nclauses = " + res)

    #part 3 save results
    #part 3.1 create directory
    #my_cwd = os.getcwd()
    #new_dir = 'Solutions'
    #path = os.path.join(my_cwd, new_dir)
    #os.mkdir(path)
    #print("New directory created\n")

    #part 3.2 save CNF results for pySat

    #output_res_to_file(answer_file_name + "/(35, 10, 13)_wt5_" + str(curr_border) + ".txt", res_to_Dimacs(res))

    output_res_to_file(answer_file_name + "/cnf.py", "clauses = " + res);
    print(res, "\n")

    #part 3.3 save CNF in Dimacs format + save base variables for quicker sat-solver working
    output_res_to_file(answer_file_name + "/dimacs.txt", res_to_Dimacs(res));
    output_res_to_file(answer_file_name + "/dimacs_core_vars.txt", base_variable_numbers);
    print("Dimacs created")

    return res
