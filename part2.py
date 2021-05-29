from pulp import *
import cplex

n = 4 #number of nodes in one border
length = 14 # string length
nSquare = pow(n, 2)
NMatrix = [] #neighboring matrix
chars = [1,0,0,0,1,0,0,1,1,0,0,0,1,0]
chars2 =[0,1,1,1,0,1,1,0,0,1,1,1,0,1]
index = range(1,nSquare + 1)
position = range(1,length + 1)

#Defining neighbor matrix  
for i in range(0, nSquare):
    row = []
    for j in range(0,nSquare):
        row.append(0)
    if i == 0:                  # üst sol köşe
        row[i + 1] = 1
        row[i + n] = 1
        print("Const : 1","i :" ,i, "Row : ", row)
    elif i < (n - 1):           # üst sınır 
        row[i + 1] = 1
        row[i - 1] = 1
        row[i + n] = 1
        print("Const : 2","i :" ,i, "Row : ", row)
    elif i == (n - 1):          # üst sağ köşe
        row[i - 1] = 1
        row[i + n] = 1
        print("Const : 3","i :" ,i, "Row : ", row)
    elif i == (nSquare - n):      # alt sol köşe
        row[i + 1] = 1
        row[i - n] = 1
        print("Const : 4","i :" ,i, "Row : ", row)
    elif i == (nSquare - 1):      # alt sağ köşe
        row[i - 1] = 1
        row[i - n] = 1
        print("Const : 5","i :" ,i, "Row : ", row)
    elif (i + 1) % n == 0:      # sağ kenar
        row[i - 1] = 1
        row[i + n] = 1
        row[i - n] = 1
        print("Const : 6","i :" ,i, "Row : ", row)
    elif i % n == 0:            # sol kenar
        row[i + 1] = 1
        row[i + n] = 1
        row[i - n] = 1
        print("Const : 7","i :" ,i, "Row : ", row)
    elif (i > (nSquare - n)) and (i < (nSquare - 1)):
        row[i + 1] = 1          # alt kenar
        row[i - 1] = 1
        row[i - n] = 1
        print("Const : 8","i :" ,i, "Row : ", row)
    else:                       #orta bölge
        row[i + 1] = 1
        row[i - 1] = 1
        row[i - n] = 1
        row[i + n] = 1
        print("Const : 9","i :" ,i, "Row : ", row)
    NMatrix.append(row)

#Defining lp problem
prob = LpProblem("PositioningProblem", LpMaximize)

#Defining decision variables
# decision variables for part 1
G = LpVariable.dicts("Node", (index, position), cat="Binary")
I = LpVariable.dicts("OneNode", index, cat="Binary")
E = LpVariable.dicts("Doubleones", (index,index), cat="Binary")
T = LpVariable("TempVariable1", cat="Integer") # This is used for objective function

# decision variables for part 2
I2 = LpVariable.dicts("OneNode2", index, cat="Binary")
E2 = LpVariable.dicts("Doubleones2", (index,index), cat="Binary")
T2 = LpVariable("TempVariable2", cat="Integer") # This is used for part2 constraint

#Defining objective function
prob += (((lpSum(E[i][j]* NMatrix[i-1][j-1] for i in index for j in index)) / 2) - T),"Maximum number of contact"
prob += T - lpSum(chars[k-1] * chars[k] for k in range(1,length)) == 0

# CONSTRAINTS OF PART 1
#Adding Constraints
#First Constraint
for i in index:
    prob += lpSum([G[i][k] for k in position]) <= 1

#Second Constraint
for k in position:
    prob += lpSum([G[i][k] for i in index]) == 1

#Thirds Constraint
for i in index:
    for k in range(2,length + 1):
        prob += G[i][k] - lpSum([G[j][k - 1]*NMatrix[i-1][j-1] for j in index]) <= 0

#Limiting the I values
for i in index:
    prob += I[i] - lpSum([G[i][k]*chars[k-1] for k in position]) == 0

#Limiting the E values
for i in index:
    for j in index:
        prob += E[i][j] - I[i] <= 0
        prob += E[i][j] - I[j] <= 0
        prob += E[i][j] - I[i] - I[j] + 1 >= 0 

# CONSTRAINTS OF PART 2
#Limiting the I values
for i in index:
    prob += I2[i] - lpSum([G[i][k]*chars2[k-1] for k in position]) == 0

#Limiting the E values
for i in index:
    for j in index:
        prob += E2[i][j] - I2[i] <= 0
        prob += E2[i][j] - I2[j] <= 0
        prob += E2[i][j] - I2[i] - I2[j] + 1 >= 0 

prob += T2 - lpSum(chars2[k-1] * chars2[k] for k in range(1,length)) == 0
prob += ((lpSum(E2[i][j]* NMatrix[i-1][j-1] for i in index for j in index)) / 2) - T2 == 0

# The problem data is written to an .lp file
prob.writeLP("Part2.lp")

#The problem is solved using Cplex
solver = getSolver("CPLEX_PY")
prob.solve(solver)

"""
# printing the values of all decision variables
for variable in prob.variables():
    print("{} = {}".format(variable.name, variable.varValue))
"""
# Printing the grid with characters on their place
print()
nodeOrder = []
if LpStatus[prob.status] == "Optimal":
    for i in index:
        t = 0
        for k in position:
            t += (G[i][k].varValue)
            if G[i][k].varValue >= 1:
                nodeOrder.append(k)
        if t == 0:
            nodeOrder.append("N")
        if t == 1 and i % n != 0:
            print(int(I[i].varValue), "--- ", end = "")
        elif t == 1:
            print(int(I[i].varValue))
            if i != nSquare:
                for j in range(0,n):
                    if(j != n-1):
                        print("|     ", end = "")
                    else:
                        print("|")
        elif t == 0 and i % n != 0:
            print("N", "--- ", end = "")
        else:
            print("N")
            if i != nSquare:
                for j in range(0,n):
                    if(j != n-1):
                        print("|     ", end = "")
                    else:
                        print("|")

    print()
    for i in range(0, nSquare):
        if(nodeOrder[i] == "N"):
            print(nodeOrder[i], "   ",  end = "")
        elif(nodeOrder[i] > 9):
            print(nodeOrder[i], "  ",  end = "")
        else:
            print(nodeOrder[i], "   ",  end = "")
        if i != 0 and (i+1) % n == 0:
            print()
    print()

# Printing which nodes contain a char of string and OneNode Values for each node of grid
if LpStatus[prob.status] == "Optimal":
    for i in index:
        t = 0
        for k in position:
            t += (G[i][k].varValue)
        print(i, " = ", int(t), "OneNode", "_", i, I[i].varValue)