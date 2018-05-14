import re
import sys
import linecache
import numpy as np
import pandas as pd
from datetime import datetime,timedelta

class address:
    def __init__(self, address, name, identity, education,time_lapse, number_of_responses, number_of_phone_responses):
        self.address                   = address
        self.name                      = name
        self.identity                  = identity               # 0 = black, 1 = white
        self.education                 = education
        self.time_lapse                = time_lapse
        self.number_of_responses       = number_of_responses
        self.number_of_phone_responses = number_of_phone_responses

    def get_address(self): 
    	return self.address

    def get_name(self): 
    	return self.name

    def get_identity(self): 
    	return self.identity

    def get_education(self): 
        return self.education

    def get_time_lapse(self): 
    	return self.time_lapse

    def get_number_of_responses(self): 
    	return self.number_of_responses

    def get_number_of_phone_responses(self): 
    	return self.number_of_phone_responses
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def retrive_values(address):
	iden = address.get_identity()
	name = address.get_name()
	education = address.get_education()
	time_lapse = address.get_time_lapse()
	num_responses = address.get_number_of_responses()
	number_of_phone_responses = address.get_number_of_phone_responses()

	return (name,iden,education,time_lapse,num_responses,number_of_phone_responses)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_first_response(email_responses_ts, phone_response_ts):
	all_timestamps = []
	if email_responses_ts != 0: 
		all_timestamps.extend(eval(email_responses_ts))

	if phone_response_ts != 0:
		all_timestamps.extend(eval(phone_response_ts))

	if all_timestamps:
		all_timestamps = [datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S") for timestamp in all_timestamps]
		min_time = min(all_timestamps)
		return min_time
	else: 
		return None
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def check_val(value):
	bad_vals = [np.nan, None, ' ', '', '  ']
	ret = None 
	if value in bad_vals: 
		ret = 0
	else:
		ret = value
	return ret
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
parameter_file_name = sys.argv[1]
line_num = 1
while True:
	file_line = linecache.getline(parameter_file_name, line_num)
	if file_line is '':
		break
	else:
		file_line = re.sub('\n','',file_line)
		parameters = file_line.split("\\") # parse the text file by the \ character

		# set the string passed in from the text files
		address_sheet 	   = parameters[0] 			  		 # rentals_sheet
		status_sheet  	   = parameters[1] 			  	     # status sheet
		phone_status_sheet = parameters[2] 			  		 # phone csv
		output_sheet 	   = parameters[3] 			         # csv that contains listings

		df_address  	   = pd.read_csv(address_sheet) 	 # create a dataframe with the return_sheet.
		df_status   	   = pd.read_csv(status_sheet) 	     # create a dataframe for status_sheet
		df_phone    	   = pd.read_csv(phone_status_sheet) # create a dataframe for phone_status_sheet

		address_list 	   = []
		n = 6										         # number of address + 1

		for index,row in df_status.iterrows(): 
			identity = row['racial category']
			name     = str(row['first name']) + ' ' + str(row['last name'])
			if identity == 'black': 
				identity = 0
			else: 
				identity = 1

			phone_row = df_phone.iloc[index]
			for i in range(1,n):
				address_string    = 'address ' + str(i)
				address_loc       = check_val(row[address_string])

                                edu_level         = row['education level']

				timestamp_string  = 'timestamp ' + str(i)
				timestamp_inq     = row[timestamp_string]
				timestamp_inq     = timestamp_inq.replace('/18', '/2018') # change this in the message_sender to avoid this
				timestamp_inq     = datetime.strptime(timestamp_inq, "%m/%d/%Y %H:%M")

				response_t_string = 'response timestamp ' + str(i) # response timestamps
				response_t_e      = check_val(row[response_t_string])
				response_t_p      = check_val(phone_row[response_t_string])
				first_t_response  = get_first_response(response_t_e, response_t_p)

				if first_t_response != None:
					time_lapse = (first_t_response - timestamp_inq).total_seconds()//60
				else: 
					time_lapse = None      

				response_string   = 'total responses ' + str(i)   # total number of responses
				responses_e       = check_val(row[response_string])
				responses_p       = check_val(phone_row[response_string])
				response_total    = int(responses_e) + int(responses_p)

				address_list.append( address(address = address_loc, name = name,identity = identity, education = edu_level, time_lapse = time_lapse, number_of_responses = response_total, number_of_phone_responses = responses_p))

		df_address_cols = ['Address','Name','Identity', 'Education Level','Time Elapsed', 'Number of Responses', 'Number of Phone Responses'] 
		df_address_old_cols = list(df_address.columns.values)[1:]
		df_address_cols.extend(df_address_old_cols)

		print(df_address_cols)
		table = [] 
		for listing in address_list: 
			street_address = listing.get_address().split(',')[0][1:]
			rental_row     = list(df_address[df_address.Address == street_address].values[0])
			inq_data       = retrive_values(listing)
			for inq in inq_data[::-1]:
				rental_row.insert(1,inq)
			table.append(rental_row)
		df_final = pd.DataFrame(table, columns = df_address_cols)
		df_final.to_csv(output_sheet, index_label = False, index = False)
	line_num += 1
