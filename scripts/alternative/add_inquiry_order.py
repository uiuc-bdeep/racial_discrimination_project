import re 
import os
import sys
import csv 
import random 
import linecache
import numpy as np
import pandas as pd

csv_file = str(sys.argv[1])
df_csv = pd.read_csv(csv_file)

address = []
#create a list with all addresses that were sent an inquiry
for i in range(1,67): 
	temp = list(df_csv['address ' + str(i)].values)
	for j in range(0,len(temp)): 
		temp[j] = temp[j].split(',')[0][1:]
		address = address + temp
# remove duplicates
address = list(set(address))
address_dict = {}
for add in address: 
	address_dict.update({add:0})


for i in range(1,67): 
	new_col = []
	for index, row in df_csv.iterrows(): 
		if row['address ' + str(i)] != ' ':
			curr_add = row['address ' + str(i)].split(',')[0][1:]
			new_col.append(address_dict[curr_add] + 1)
			address_dict[curr_add] += 1
		else: 
			new_col.append(' ')
	new_col = pd.Series(new_col)
	df_csv['inquiry order ' + str(i)] = new_col

print(df_csv)
df_csv.to_csv(csv_file, index = False)
