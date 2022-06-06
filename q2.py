import csv
import sys

file = open(sys.argv[1], "r")
reader = csv.reader(file)
c = 1
d = {"Maths": [0, ""], "Biology": [0, ""], "Chemistry": [0, ""],
     "Physics": [0, ""], "English": [0, ""], "Hindi": [0, ""]}
Total = [0, 0, 0]
Names = ["", "", ""]
for row in reader:
    if(c == 1):
        c += 1
        continue
    x = row
    tot = 0
    m = int(row[1])
    b = int(row[2])
    e = int(row[3])
    p = int(row[4])
    c = int(row[5])
    h = int(row[6])
    name = row[0]
    if(d["Maths"][0] < m):
        d["Maths"][0] = m
        d["Maths"][1] = name
    elif(d["Maths"][0] == m):
        temp = d["Maths"][1]
        temp = temp + " " + name
        d["Maths"][1] = temp
    if(d["Physics"][0] < p):
        d["Physics"][0] = p
        d["Physics"][1] = name
    elif(d["Physics"][0] == p):
        temp = d["Physics"][1]
        temp = temp + " " + name
        d["Physics"][1] = temp
    if(d["English"][0] < e):
        d["English"][0] = e
        d["English"][1] = name
    elif(d["English"][0] == e):
        temp = d["English"][1]
        temp = temp + " " + name
        d["English"][1] = temp
    if(d["Biology"][0] < b):
        d["Biology"][0] = b
        d["Biology"][1] = name
    elif(d["Biology"][0] == b):
        temp = d["Biology"][1]
        temp = temp + " " + name
        d["Biology"][1] = temp
    if(d["Chemistry"][0] < c):
        d["Chemistry"][0] = c
        d["Chemistry"][1] = name
    elif(d["Chemistry"][0] == c):
        temp = d["Chemistry"][1]
        temp = temp + " " + name
        d["Chemistry"][1] = temp
    if(d["Hindi"][0] < h):
        d["Hindi"][0] = h
        d["Hindi"][1] = name
    elif(d["Hindi"][0] == h):
        temp = d["Hindi"][1]
        temp = temp + " " + name
        d["Hindi"][1] = temp

    tot = m+b+e+p+c+h
    if(tot > Total[0]):
        Total[0] = tot
        Names[0] = name
    elif(tot > Total[1]):
        Total[1] = tot
        Names[1] = name
    elif(tot > Total[2]):
        Total[2] = tot
        Names[2] = name


for i in d:
    print("Topper in", i, "is", d[i][1])

print("\n")
print("Best students in the class are", Names[0], Names[1], Names[2])

print("Total time complexity: O(n)")
print("where n in number of student records")
