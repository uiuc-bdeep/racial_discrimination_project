import pandas as pd 
import numpy as np 
import sys

csv_file = sys.argv[1]

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

# create a dictionary that maps an address to another dictionary that maps a racial group to a name
address_dict = {}
for add in address: 
	race_dict    = {'black': [], 'white': [], 'hispanic': []}
	address_dict.update({add:race_dict})

# iterate through the dateframe to populate address_dict 
for index, row in df_csv.iterrows(): 
	if index != 0:
		for i in range(1,67):
			y = row['address ' + str(i)].split(',')[0][1:]
			address_dict[y][row['racial category']].append(row['first name']) 
# is_correct maps an address to a 0 or 1
	# 0 - if the listing of the adress was NOT sent to all 3 racial categories
	# 1 - if the listing of the address was sent to all 3 racial categories
is_correct = {}

# populate is_correct
for key,value in address_dict.items(): 
	print(str(key) + ': ' + str(value))
	correct = 1
	for k,val in value.items(): 
		if not val: 
			correct = 0
	is_correct.update({key:correct})

# correct_address is a list of addresses which received an inquiry from all three racial groups
correct_address = []
for key, value in is_correct.items(): 
	if value == 1: 
		correct_address.append(key)

print('Sent an inquiry: ' + str(len(address)))
print('Sent to all three racial groups: '+ str(len(correct_address)))

