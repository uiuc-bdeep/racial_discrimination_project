import re 
import os
import sys
import csv 
import random 
import linecache
import numpy as np
import pandas as pd

NUM_IDENTITES_PER_RACE = 6

def initialize_data_sheets(status, email, phone, df_names, LPI):
	num_cols = (LPI*3) + 1
	timestamp_cols = ['handled']

	for i in range(1, num_cols):
		timestamp_cols.append('address ' + str(i))
		timestamp_cols.append('timestamp ' + str(i))
		timestamp_cols.append('inquiry order ' + str(i))
#----------------------------------------------------------------------------------------------------------------------------------
	email_cols = []
	for i in range(1, num_cols): 
		email_cols.append('address ' + str(i))
		email_cols.append('total responses ' + str(i))
		email_cols.append('response timestamp ' + str(i))
		email_cols.append('total unavailable ' + str(i))
		email_cols.append('unavailable ' + str(i))
#----------------------------------------------------------------------------------------------------------------------------------
	# new column names for the phone sheet
	phone_cols = []
	for i in range(1, num_cols):
		phone_cols.append('address ' + str(i)) 
#----------------------------------------------------------------------------------------------------------------------------------
	df_new          = (pd.DataFrame(columns=timestamp_cols)).fillna(' ')		# empty dataframe with new columns for status sheet 

	df_timestamp    = df_names[df_names.columns[0:8]] 							# create a new dataframe from the return sheet

	df_timestamp    = pd.concat([df_timestamp, df_new], axis = 1).fillna(' ')	# concatenate old values with the new columns
	df_timestamp['handled'] = 0
	df_timestamp.to_csv(status,mode='w',index=False)
#----------------------------------------------------------------------------------------------------------------------------------
	df_new          = (pd.DataFrame(columns=email_cols)).fillna(' ')			# empty dataframe with new columns for phone sheet

	df_email       	= df_names[df_names.columns[0:8]]							# create a new dataframe from the return sheet

	df_email       	= pd.concat([df_email, df_new], axis = 1).fillna(' ')		# concatenate old values with the new columns
	df_email.to_csv(email,mode='w',index=False)
#----------------------------------------------------------------------------------------------------------------------------------
	df_new   		= (pd.DataFrame(columns=phone_cols)).fillna(' ')			# empty dataframe with new columns for phone sheet

	df_phone 		= df_names[df_names.columns[0:8]]							# create a new dataframe from the return sheet

	df_phone 		= pd.concat([df_phone, df_new], axis = 1).fillna(' ')		# concatenate old values with the new columns
	df_phone.to_csv(phone,mode='w',index=False)
#----------------------------------------------------------------------------------------------------------------------------------
	return df_timestamp, df_email,df_phone

def get_dataframes(names, status, email, phone, LPI): 
	df_names = pd.read_csv(names) 						# create a dataframe with the names csv

	if os.path.isfile(status) == False: 				# check if the status sheet exists
		print('Status Sheet Not Initialized\nInitializing ...')
		df_timestamp, df_email,df_phone = initialize_data_sheets(status, email, phone, df_names, LPI)

	else: 
		# create a dataframe from saved status sheet csv
		df_timestamp = pd.read_csv(status)
		df_email     = pd.read_csv(email) 
		df_phone     = pd.read_csv(phone)

	return df_names, df_timestamp, df_email,df_phone

def test_output(df_csv): 
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
		for i in range(1,67):
			y = row['address ' + str(i)].split(',')[0][1:]
			address_dict[y][row['racial category']].append(row['first name']) 
	# is_correct maps an address to a 0 or 1
		# 0 - if the listing of the adress was NOT sent to all 3 racial categories
		# 1 - if the listing of the address was sent to all 3 racial categories
	is_correct = {}

	# populate is_correct
	for key,value in address_dict.items(): 
		# print('---------------------------------------------------------------------------------------------')
		# print(str(key) + ': ' + str(value))
		correct = 1
		for k,val in value.items(): 
			if len(val) != 1: 
				correct = 0
			if len(val) > 1: 
				print(k)
		is_correct.update({key:correct})

	# correct_address is a list of addresses which received an inquiry from all three racial groups
	correct_address = []
	for key, value in is_correct.items(): 
		if value == 1: 
			correct_address.append(key)
	correct_address = list(set(correct_address))
	print('Sent an inquiry: ' + str(len(address)))	
	print('Sent to all three racial groups(by dict): '+ str(len(correct_address)))

	counter = 0
	three_list = []
	for index, row in df_csv.iterrows(): 
		for i in range(1,67): 
			if row['inquiry order ' + str(i)] == 3: 
				three_list.append(row['address ' + str(i)].split(',')[0][1:])
	three_list = list(set(three_list))
	print('Sent to all three racial groups(by counter): ' + str(len(three_list)))

	print('Set difference: ' + str(list(set(three_list) - set(correct_address))))

def get_partitions(df_rentals): 
	# cut the main rentals dataframe down by a criteria MAY NEED CHANGING IN THE FUTURE
	df_mod_rentals   = df_rentals[(df_rentals['Bedroom_max'] == '3') & (df_rentals['Bathroom_max'] == 2.0)].sample(frac = 1)
	# equally divide up the dataframe based on the number of races, in this case we have white, black, and hispanic
	split_df    = np.array_split(df_mod_rentals, 3)
	group_one   = split_df[0]
	#print(len(group_one))
	group_two   = split_df[1]
	#print(len(group_two))
	group_three = split_df[2]
	#print(len(group_three))
	group_one_addr = group_one['Address'].values
	group_two_addr = group_two['Address'].values
	group_three_addr = group_three['Address'].values


	#  calculate the Listings Per Identity by getting the minimum of the three groups and dividing it by the number of identities per race
	LPI         = int(min([len(group_one), len(group_two), len(group_three)])/NUM_IDENTITES_PER_RACE)

	return group_one, group_two, group_three, LPI

def get_day_dict(df_rentals, day_num = 3):
	 	group_one, group_two, group_three, LPI = get_partitions(df_rentals)

	 	day_trial_dict = {}
	 	for i in range(1,day_num + 1): 
	 		if i == 1:
	 			race_dict = {'black': group_one, 'white': group_two, 'hispanic': group_three}
	 		elif i == 2: 
	 			race_dict = {'black': group_two, 'white': group_three, 'hispanic': group_one}
	 		else: 
	 			race_dict = {'black': group_three, 'white': group_one, 'hispanic': group_two}
	 		day_trial_dict.update({i:race_dict})

 		return day_trial_dict, LPI	

def main():
	parameter_file_name = str(sys.argv[1])

	file_line =  linecache.getline(parameter_file_name, 1)
	file_line = re.sub('\n','',file_line)
	parameters = file_line.split(",") # parse the text file by the \ character

	names_sheet 	   = parameters[0] 					# name_market.csv
	time_status_sheet  = parameters[1] 					# timestamp output csv
	email_status_sheet = parameters[2]					# email output csv
	phone_status_sheet = parameters[3] 					# phone output csv
	rentals_sheet 	   = parameters[4] 					# csv that contains listings


	df_rentals = pd.read_csv(rentals_sheet)
	df_rentals = df_rentals[pd.notnull(df_rentals['Address'])].drop_duplicates(subset = 'Address')

	day_trial_dict, LPI = get_day_dict(df_rentals) 

	df_names, df_status_timestamp, df_status_email, df_status_phone = get_dataframes(names_sheet, time_status_sheet, email_status_sheet, phone_status_sheet,LPI)

	inquiry_order = {}
	loc = 1
	for key, value in day_trial_dict.items():
		day_num = int(key)
		for i in range(loc, (LPI * day_num + 1)):
			for index,row in df_status_timestamp.iterrows(): 
				race          = row['racial category']
				rand_row      = day_trial_dict[key][race].sample(n=1) 
				rand_row_add  = rand_row['Address'].values[0]
				rand_row_url  = rand_row['URL'].values[0]
				day_trial_dict[key][race] = day_trial_dict[key][race][~day_trial_dict[key][race]['Address'].isin([rand_row_add])]
				if rand_row_add not in inquiry_order: 
					inquiry_order.update({rand_row_add:1})
				else: 
					inquiry_order[rand_row_add] += 1

				df_status_timestamp.at[index, 'inquiry order ' + str(i)] = str(inquiry_order[rand_row_add]) 
				df_status_timestamp.at[index,'address ' + str(i)] = '('+ rand_row_add + ', ' + rand_row_url + ')'
				df_status_phone.at[index, 'address ' + str(i)]    = rand_row_add
				df_status_email.at[index, 'address ' + str(i)]    = rand_row_add
			loc += 1

	df_status_timestamp.to_csv(time_status_sheet,mode='w',index=False)
	df_status_email.to_csv(email_status_sheet,mode='w',index=False)
	df_status_phone.to_csv(phone_status_sheet,mode='w',index=False)

	test_output(df_status_timestamp)



main()