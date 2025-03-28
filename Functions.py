import os
from pysat.card import *
from itertools import *

#ltoN : map<str, int>
ltoN =  {"a", 0}
cur_fresh_var = 1
inequivs = []
answer_from_sat = []
switch_cout_mknf = False
switch_cout_equi = False
switch_cout_vars = False

def set_ltoN(mapa : dict):
    global ltoN
    ltoN = mapa

#return current number of variables in our CNF-formula
def get_vars_count() -> int:
    global cur_fresh_var
    return cur_fresh_var - 1

def set_vars_count(cur : int):
    global cur_fresh_var
    cur_fresh_var = cur

#print on screen pairs of number and variable a(step)_i..i(step)_j correspondes to this number
def print_all_LtoN():
    print("ltoN:\n")
    for i in ltoN:
        print(i.first, " ", i.second, "\n")

#prepairing program to work with new code
def set0(n1 :int, k1 :int, d1 :int, mode :int):
    empt_map = {}
    empt_vec_str = []
    empt_vec_int = []
    global inequivs
    global answer_from_sat
    if (mode != 1):
        set_vars_count(1)
        set_ltoN(empt_map)
        inequivs = empt_vec_str;

    answer_from_sat = empt_vec_int


#create new variables
def make_var(step :int, i :str, j :int) -> str:
    a_i_j = "a" + str(step) + "_" + i + "_" + str(j)
    global ltoN
    global cur_fresh_var
    if (ltoN.get(a_i_j) == None):
        if (switch_cout_vars):
            print(a_i_j, cur_fresh_var)
        ltoN.update({ a_i_j : cur_fresh_var })
        cur_fresh_var += 1
    return a_i_j


#creates and returns base variables
def first_step_variables(n :int, k :int) -> str:
    res = ""
    for i in range(1, k + 1):
        for j in range(1, n - k + 1):
            res += str(ltoN[make_var(1, str(i), j)]) + " "
    return res

#creates and returns base variables
def first_step_variables_H(n :int, k :int) -> str:
    res = ""
    for i in range(1, n + 1):
        for j in range(1, n - k + 1):
            res += str(ltoN[make_var(1, str(i), j)]) + " "
    
    return res

#CREATE CNF

#create new variables
def make_var_sb(type :str, id :int, step :int) -> str: # id -- identifier number of left vector
    sb = "sb_" + type + str(id) + "_" + str(step)
    global ltoN
    global cur_fresh_var
    if (ltoN.get(sb) == None):
        ltoN.update({ sb: cur_fresh_var })
        cur_fresh_var += 1
    return sb

def make_sb_conjunkt4(aprev :int, x :int, y :int, a :int) -> str:
	return "[" + str(aprev) + ", " + str(x) + ", " + str(y) + ", " + str(a) + "]"

def make_sb_conjunkt2(aprev :int, acurr :int) -> str:
	return "[" + str(aprev) + ", " + str(acurr) + "]"


#create_variable_c
def create_variable_c(x :int, y :int, i :int) -> str:
    ai = ltoN[make_var_sb("c", x, i)]
    xi = ltoN[make_var(1, str(i), x)]
    yi = ltoN[make_var(1, str(i), y)]
    aiprev = ltoN[make_var_sb("c", x, i - 1)]
    res  = make_sb_conjunkt4(-aiprev,  xi,  yi,  ai) + ", " 
    res += make_sb_conjunkt4(-aiprev,  xi, -yi, -ai) + ", " 
    res += make_sb_conjunkt4(-aiprev, -xi,  yi, -ai) + ", " 
    res += make_sb_conjunkt4(-aiprev, -xi, -yi,  ai) + ", " 
    res += make_sb_conjunkt2(aiprev, -ai)
    return res

#create_variable_d
def create_variable_d(x :int, y :int, i :int) -> str:
    bi = ltoN[make_var_sb("d", x, i)]
    xi = ltoN[make_var(1, str(i), x)]
    yi = ltoN[make_var(1, str(i), y)]
    aiprev = ltoN[make_var_sb("c", x, i - 1)]
    res  = make_sb_conjunkt4(-aiprev,  xi, -yi,  bi) + ", " 
    res += make_sb_conjunkt4(-aiprev,  xi,  yi, -bi) + ", "
    res += make_sb_conjunkt4(-aiprev, -xi,  yi, -bi) + ", "
    res += make_sb_conjunkt4(-aiprev, -xi, -yi, -bi) + ", "
    res += make_sb_conjunkt2(aiprev, -bi)
    return res

#create_variable_d
def create_condition_e(x :int, y :int, length :int) -> str:

    res = "[]" 
    ans = "[]"
    for i in range(1, length + 1):
        bi = ltoN[make_var_sb("d", x, i)]
        ans = ans[0: len(ans) - 1] + str(bi) + ", ]"

    ai = ltoN[make_var_sb("c", x, length)]
    ans = ans[0: len(ans) - 1] + str(ai) + "]"
    res = ans #fix ans = "[]"
    return res

def create_condition_vector_x_smaller_vector_y(x :int, y :int, length :int) -> str:
    res = "[]"
    create_c = "[]"
    create_d = "[]"
    create_c = "[" + str(ltoN[make_var_sb("c", x, 0)]) + "]]"
    for i in range(1, length + 1):
       create_c = create_c[0: len(create_c) - 1] + ", " + create_variable_c(x, y, i) + "]"
    
    create_d = create_variable_d(x, y, 1) + "]"
    for i in range(2, length + 1):
        create_d = create_d[0: len(create_d) - 1] + ", " + create_variable_d(x, y, i) + "]"
    res  = create_c[0: len(create_c) - 1] + ",\n" 
    res += create_d[0: len(create_d) - 1] + ",\n" 
    res += create_condition_e(x, y, length)
    return res

#
def symmetry_breaking(n : int, k :int, d :int) -> str:
    ans = "[]"
    res = "[]"
    #step 1 вес хотя бы одной из строк равен d

    #experimental maybe FATAL but try
    for j in range(1, n - k + 1):
        if (j <= (n - k) - d + 1):
            ans = ans[0: len(ans) - 1] + "[-" + str(ltoN[make_var(1, "1", j)]) + "], ]"
        else:
            ans = ans[0: len(ans) - 1] + "[" + str(ltoN[make_var(1, "1", j)]) + "], ]"
    res = ans[0: len(ans) - 3] + "]";

    #step 2 лексикографическая сортировка столбцов 
    if (n - k >= 2):
        ans = "[" #fix 
        for j in range (1, n - k):        
            ans = ans[0: len(ans) - 1] + create_condition_vector_x_smaller_vector_y(j, j + 1, k) + ",\n]"
        res = res[0: len(res) - 1] + ",\n" + ans[0: len(ans) - 3] + "]"
    
    return res

def symmetry_breaking_H(n : int, k :int, d :int) -> str:
    ans = "[]"
    res = "[]"
    #step 1 справа единичная матрица

    for i in range(k + 1, n + 1):
        for j in range(1, n - k + 1):
            if(i - k == j):
                ans = ans[:-1] + "[" + str(ltoN[make_var(1, str(i), j)]) + "], ]"
            else:
                ans = ans[:-1] + "[-" + str(ltoN[make_var(1, str(i), j)]) + "], ]"
    
    res = ans[0: len(ans) - 3] + "]";

    return res

#create printable version of inequality
def make_printable_inequality(jmax :int, d :int, step :int, i :str) -> str: # x1 + x2 + .. + x_jmax >= d - step

    inequality = ""
    a_i_j = ""
    for j in range(1, jmax + 1):
        a_i_j = make_var(step, i, j)
        if (j != 1):
            a_i_j = " + " + a_i_j
        inequality += a_i_j
    
    inequality += " >= " + str(d - step)
    return inequality

#generate CNF version of inequality
def inequality_to_cnf( n :int, k :int, d :int, step :int, i_main :str) -> str:
    a_i_j = ""
    literals = []
    global ltoN
    for j in range(1, n - k + 1):
        a_i_j = make_var(step, i_main, j)
        literals.append(ltoN[a_i_j])
    
    cnf = CardEnc.atleast(lits=literals, bound=d-step, top_id=cur_fresh_var, vpool=None, encoding=1)
    set_vars_count(cnf.nv + 1)
    return str(cnf.clauses)

#generate CNF version of inequality
def verification_disjunkt( n :int, k :int, d :int, step :int, i_main :str) -> str:
    a_i_j = ""
    literals = []
    global ltoN
    for j in range(1, n - k + 1):
        a_i_j = make_var(step, i_main, j)
        literals.append(ltoN[a_i_j])
    return "[" + str(literals) + "]"

#creates 
def generate_cnf_inequalities(n :int, k :int, d :int, step :int, verification_matrix_mode :bool) -> str: # x1 + x2 + x3 >= d
    res = ""
    ans = ""
    i_main = ""
    global inequivs
    for comb in combinations(range(1, k + 1), step):
        i_main = ""
        for co in comb:
            i_main += str(co) + "."
        i_main = i_main[:-1]
        inequivs.insert(len(inequivs), make_printable_inequality(n - k, d, step, i_main))
        if (switch_cout_mknf):
            print(inequivs[len(inequivs) - 1] + "\n")
        if (verification_matrix_mode and (d > (step + 1))):
            ans = verification_disjunkt(n, k, d, step, i_main)
            res = res[0: len(res) - 1] + ",\n" + ans[1: len(ans) - 1] + "]"
        ans = inequality_to_cnf(n, k, d, step, i_main)
        res = res[0: len(res) - 1] + ",\n\n" + ans[1: len(ans) - 1] + "]"
    return res

#creates 
def generate_cnf_inequalities_H(n :int, k :int, d :int, step :int, verification_matrix_mode :bool) -> str: # x1 + x2 + x3 >= d
    res = ""
    ans = ""
    i_main = ""
    global inequivs
    use_identity_part = True
    last = k + 1
    if(use_identity_part):
        last = n + 1
    for comb in combinations(range(1, last), step):
        i_main = ""
        for co in comb:
            i_main += str(co) + "."
        i_main = i_main[:-1]
        ans = verification_disjunkt(n, k, d, step, i_main)
        res = res[0: len(res) - 1] + ",\n" + ans[1: len(ans) - 1] + "]"
    return res

#creates partially
def experiment_generate_cnf_inequalities(n :int, k :int, d :int, step :int, verification_matrix_mode :bool, curr_border :int) -> str: # x1 + x2 + x3 >= d, sometimes x1 + x2 + x3 >= d-1
    res = ""
    ans = ""
    i_main = ""
    partially_count = curr_border
    curr_count = 0
    global inequivs
    for comb in combinations(range(1, k + 1), step):
        curr_count += 1
        i_main = ""
        for co in comb:
            i_main += str(co) + "."
        i_main = i_main[:-1]
        inequivs.insert(len(inequivs), make_printable_inequality(n - k, d, step, i_main))
        if (switch_cout_mknf):
            print(inequivs[len(inequivs) - 1] + "\n")
        if (verification_matrix_mode and (d > (step + 1))):
            ans = inequality_to_cnf(n, k, step + 1, step, i_main)
            res = res[0: len(res) - 1] + ",\n" + ans[1: len(ans) - 1] + "]"
        if(step > 5 or (step == 5 and curr_count > partially_count)):
            ans = inequality_to_cnf(n, k, d - 1, step, i_main)
        else:
            ans = inequality_to_cnf(n, k, d, step, i_main)
        res = res[0: len(res) - 1] + ",\n" + ans[1: len(ans) - 1] + "]"
    return res


def make_equi(newLet :str, let1 :str, let2 :str) -> str: # x1 + x2 + x3 >= d
    equi = newLet + " equiv " + let1 + " xor " + let2
    return equi

#return 1 if for this parameters from a: y equivalent to x1 xor x2
def func_y_equi_x1_xor_x2(a :int) -> bool: #y equi x1 xor x2
    x2 = a % 2
    a = int(a/2)
    x1 = a % 2
    a = int(a/2)
    y = a % 2
    if ((x1 + x2 + y) % 2 == 1):
        return False
    else:
        return True


#adding conditions for new variable that equivalents to xor of 2 already exizting variables
def adding_new_xor_variable(newLet :int, let1 :int, let2 :int) -> str: #equi(введение новой переменной) работает за константу, не требует remake
    equi = "["
    for line in range(1, pow(2, 3) + 1):
        if (not func_y_equi_x1_xor_x2(line)):
            # \/ //toDo delete copypaste

            disunkt = "["
            linecopy = line
            a = newLet
            a_i1 = let1
            a1_i2 = let2
            if (linecopy % 2):
                a1_i2 = -1 * let2
            linecopy = int(linecopy/2)
            if (linecopy % 2):
                a_i1 = -1 * let1
            linecopy = int(linecopy/2)
            if (linecopy % 2):
                a *= -1
            linecopy = int(linecopy/2)
            disunkt += str(a) + ", " + str(a_i1) + ", " + str(a1_i2)
            disunkt += "]"
            # /\

            if (equi != "["):
                equi += ", "
            equi += disunkt
    
    equi += "]"
    if (switch_cout_equi):
        print(equi)
    return equi

def generate_equi(n :int, k :int, d :int, step :int, use_identity_part : bool) -> str: 
    res = ""
    ans = ""
    i_main = ""
    last = ""
    last = k + 1
    if(use_identity_part):
        last = n + 1
    for comb in combinations(range(1, last), step):
        i_main = ""
        last = ""
        for co in comb:
            i_main += last
            last = ""
            if (i_main != ""):
                last += "."
            last += str(co)
        last = last[1: len(last)]
        for j in range(1, n - k + 1):
            if (switch_cout_equi):
                print(make_equi(make_var(step, i_main + "." + last, j), make_var(step - 1, i_main, j), make_var(1, last, j)) + "\n")
            ans = adding_new_xor_variable(ltoN[make_var(step, i_main + "." + last, j)], 
                                          ltoN[make_var(step - 1, i_main, j)], ltoN[make_var(1, last, j)])
            res = res[0: len(res) - 1] + ",\n" + ans[1: len(ans)]
            
    return res


#check_right_part //toDo correct leftpartchecking
def check_m(n :int, k :int) -> str:
    res = "[]"
    conjunkt = ""
    a = ""
    sj = 0
    for i in range(1, k+1):
        conjunkt = "["
        for j in range(1, n+1):
            sj = int(input())
            if (j <= k):
                a = make_var(0, str(i), j)
            else:
                a = make_var(1, str(i), j - k)
            if ((sj + 1) % 2):
                conjunkt += "-"
            conjunkt += str(ltoN[a]) + "], ["
        conjunkt = conjunkt[0: len(conjunkt) - 3]
        #cout << conjunkt << "\n";
        if (res != "[]"):
            res = res[0: len(res) - 1] + ",\n]"
        res = res[0: len(res) - 1] + conjunkt + "]"
    return res


#CHECK SAT RESULT


#checks all inequalities created by the generating matrix
def check_inequivs(str1 :str) -> bool:
    #print(str1)
    st = str1[1:len(str1) - 1]
    string_var_i = ""
    left_summ = 0
    right_part = 0
    flag = 0
    var_i = 0
    global answer_from_sat
    answer_from_sat = []
    answer_from_sat.insert(0, 0)
    for string_var_i in st.split(', '):
        var_i = int(string_var_i)
        answer_from_sat.insert(len(answer_from_sat), int(((var_i / abs(var_i)) + 1) / 2)) # -a -> 0 , a -> 1
    
    for i in range(0, len(inequivs)):
        left_summ = 0
        right_part
        flag = 0
        ineq = inequivs[i]
        for string_var_i in ineq.split(' '):
            if (string_var_i == "+"):
                continue
            if (string_var_i == ">="):
                flag = 1
                continue
            if (flag):
                right_part = int(string_var_i)
                continue
            left_summ += answer_from_sat[ltoN[string_var_i]]
        
        if (left_summ < right_part):
            return False
    
    #all inequivs are correct
    return True

#generate next binary vector and count of one's in it
def next_vec(vec :list[int], c :int) -> list:
    b = vec
    count = c
    for i in range(len(vec) - 1, -1, -1):
        if (vec[i] == 0):
            b[i] = 1
            count += 1
            return [ b, count ]
        else:
            b[i] = 0
            count -= 1
    return [ b, count ]


#return result generating matrix
def print_matrix(n :int, k :int) ->str:
    res = ""
    a_i_j = ""
    for j in range(0, k):
        for i in range(0, n):
            if (i < k):
                if (i == j):
                    res += "1 "
                else:
                    res += "0 "
            else:
                a_i_j = "a1_" + str(j + 1) + "_" + str(i - k + 1)
                res += str(answer_from_sat[ltoN[a_i_j]]) + " "
        res += "\n";
    return res


#print to file
def output_res_to_file(file_name :str, text :str):
    file_out = open(file_name, "w")
    file_out.write(text)
    file_out.close()


#check for all enumerations that they higher or equal Hamming distance(d) // toDo output "+ >=" correct
def check_enumeration(str1 :str, n :int, k :int, d :int) -> bool:

    used_i = [0] * k
    count = 0
    summ = 0
    cur_vec = {}
    a_i_j = ""
    answer = 0
    anslines = ""
    spectr = 0
    for h in range(0, pow(2, k) - 1):
        cur_vec = next_vec(used_i, count)
        used_i = cur_vec[0]
        count = cur_vec[1]

        #a_i_j = "a" + to_string(count) + "_";
        i_main = ""
        line = ""
        for i in range(1, k + 1):
            if (used_i[i - 1] == 1):
                i_main += str(i) + "."
                #cout << "1 + "
                line += "1"
            else:
                #cout << "0 + "
                line += "0"
        i_main = i_main[0: len(i_main) - 1]

        #cout << "| "
        line += "| "
        summ = 0
        for j in range(1, n - k + 1):
            if (len(answer_from_sat) <= ltoN[make_var(count, i_main, j)]):
                #cout << "0 + "
                line += "0 + "
            else:
                if (answer_from_sat[ltoN[make_var(count, i_main, j)]]):
                    summ += 1
                #cout << answer_from_sat[ltoN[make_var(count, i_main, j)]] << " + "
                line += str(answer_from_sat[ltoN[make_var(count, i_main, j)]]) + " + "
        
        #cout << "= " << summ + count << " >= " << d << "\n"
        line += "= " + str(summ + count) + " >= " + str(d) + "\n"

        if (summ + count == d):
            spectr += 1
        if (summ + count < d):
            answer += 1
            anslines += line
            #return false;
    
    #all enumerations(except enumerate with all zeros) checked 
    print("good:"+ str(spectr) + ", bad:" + str(answer))
    if (anslines == ""):
        return True;
    else:
        file_ans = str(answer) + "\n" + anslines + "\n\n" + print_matrix(n, k)
        #output_res_to_file("../saved_answers/(" + to_string(n) + ", " + to_string(k) + ", " + to_string(d) + ")/1000/" + to_string(answer) + ", i = " + to_string(test_number) + ".txt", file_ans)
        print(anslines)
        return False

#RESULT

#convert string version of res with square brackets to Dimacs format //toDo check in later versions how it works with [], [[1, 2, 3]]
def res_to_Dimacs(res :str) -> str:
    counter = 0
    ss = " " + res
    ans = ""
    for conjunct in ss.split(']'):
        if (conjunct != ""):
            conjunct = conjunct[3:]
            for disjunct in conjunct.split(','):
                ans += disjunct
            counter += 1
            ans += " 0\n"
            
    return "p cnf " + str(get_vars_count()) + " " + str(counter) + "\n" + ans
