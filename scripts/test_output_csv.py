import pandas as pd 
import numpy as np 
import sys

csv_file = sys.argv[1]

df_csv = pd.read_csv(csv_file)
address = []
for i in range(1,4): 
	temp = list(df_csv['address ' + str(i)].values)
	for j in range(0,len(temp)): 
		temp[j] = temp[j].split(',')[0][1:]
	address = address + temp
address_dict = {}
race_dict    = {'black': [], 'white': [], 'hispanic': []}
for x in address: 
	address_dict.update({x:race_dict})
x = 1
for index, row in df_csv.iterrows(): 
	for i in range(1,4):
		y = row['address ' + str(i)].split(',')[0][1:]
		address_dict[y][row['racial category']].append(row[]) 
print(address_dict)
