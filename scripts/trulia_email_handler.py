import ast
import os
import sys
import imaplib
import getpass
import email
import email.header
import datetime
import re
import linecache
import math
import numpy as np
import pandas as pd
import base64

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

filter_emails = ['"Trulia" <no-reply@prop.trulia.com>', '"Trulia" <updates@trulia.com>', 
				  '"Trulia" <no-reply@update.trulia.com>','Trulia <updates@comet.trulia.com>',
				  '"=?UTF-8?Q?Trulia?=" <noreply@trulia.com>', '"=?UTF-8?Q?Trulia=20Community?=" <noreply@trulia.com>']
unavailable_strings = ['not available', 'no longer available', 'off the market']
def check_available(subject_line, body): 
	for string in unavailable_strings: 
		if string in subject_line or string in body: 
			return False
	return True

def address_match(address_string, subject_line, body):
	ret_string = address_string.split(',')[0][1:]
	print(ret_string)
	match_num  = re.match(r'^[0-9]*\s', ret_string)
	if match_num != None: 
		match_num = match_num.group(0)[:-1]
		print('match_num = ' + match_num)
		print(match_num in body)
		if match_num in subject_line: 
			return True
		if match_num in body: 
			return True
	else: 
		match_string  = re.match(r'\w[a-z]*\s', ret_string)
		print('Possible intersection')
		if match_string != None: 
			match_string = match_string.group()
			print(match_string)
			print(type(match_string))
			if match_string in subject_line or match_string in body:
				return True

	return False

def process_message(M, num, msg, username, address_dict):
	body = '' # initialize the body
	if msg.is_multipart():
		for payload in msg.get_payload():
			body = body + ' ' + payload.get_payload()
	else:
		body =  msg.get_payload()
	subject = email.header.decode_header(msg['Subject'])[0][0]
	from_header = email.header.decode_header(msg['From'])[0][0]
	to_header = email.header.decode_header(msg['To'])[0][0]

	print("To: " + str(to_header) + "\n" + "From: " + str(from_header) + "\n" + "Subject: " + str(subject))

	# create a dictionary -> attach a name to a timestamp
	if from_header in filter_emails: 
		print('FOUND TRASH')
		mov = M.store(num, '+FLAGS', r'(\Deleted)')
		M.expunge()
		return address_dict

	for key, value in address_dict.items(): 
		print(key)
		if address_match(key[0], subject, body) == True:
			date_tuple = email.utils.parsedate_tz(msg['Date']) # if it does then get the time
			local_date = str(datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple)).strftime('%Y-%m-%d %H:%M:%S'))
			if check_available(subject,body) == False:
				address_dict[key][1].append(local_date)
				print('UNAVAILABLE: ' + str(key[0]))
			else:
				address_dict[key][0].append(local_date)
				print('FOUND A MATCH!' +str(key[0]))
				#mov = M.store(num, '+FLAGS', r'(\Deleted)')
				#M.expunge()
				print('Email Stored in Starred')
				return address_dict

	return address_dict

def process_mailbox(M, username, address_dict):
	rv, data = M.search(None, "ALL")
	if type(data) is not type(None) and data is not None and data[0] is not None and type(data[0]) is not type(None):
		for num in data[0].split():
			print(num)
			rv, data = M.fetch(num, '(RFC822)')
			if rv != 'OK':
				print "ERROR getting message", num
				return	
			msg = email.message_from_string(data[0][1])
			num = int(num)
			address_dict = process_message(M, num, msg, username, address_dict)
		
	return address_dict


parameter_file_name = sys.argv[1]
counter = 1
one = 1
while one is 1:
	file_line = linecache.getline(parameter_file_name, counter) # 
	if file_line is '':
		break
	else:
		file_line = re.sub('\n','',file_line)
		parameters = file_line.split('\\')

		status_sheet = parameters[0]
		print(status_sheet)

		if os.path.isfile(status_sheet) == False: # check if the status sheet exists
			print('Status Sheet not initialized')
			exit()

		status_df = pd.read_csv(status_sheet) 
		update_dict = {} # dictionary that will be used for updating the status sheet 

		# format for update_dict is {name : { (address,number) : ([availble list],[unavailable list]) } }

		# iterate throught all of the names to handle each name individually
		for index, row in status_df.iterrows():
			M = imaplib.IMAP4_SSL('imap.gmail.com') # log into gmail
			# get the row's information
			name     = row['first name']
			username = row['email'] 
			address_list = [] # format for address
			for i in range(0,5): # this will go through address 1 to address 5 
				address_list.append((row['address ' + str(i + 1)], str(i + 1)))
			address_dict = {k:([],[]) for k in address_list} 

			# format for address_dict is {(address, number) : ([available], [unavailable])}

			try:
				rv, data = M.login(username, 'BdeepTrulia') # log into the gmail accounts, print rv and data if it starts failing 
			except imaplib.IMAP4.error: # check for login failure
				print "LOGIN FAILED!!! "
				break

			rv, mailboxes = M.list()
			if rv == 'OK':
				print "Mailboxes:"

			rv, data = M.select('Inbox')
			if rv == 'OK':
				print "Processing mailbox...\n"
				update_dict.update({name:process_mailbox(M, username, address_dict)}) 
				M.close()
			else:
				print "ERROR: Unable to open mailbox ", rv
			M.logout()

		for index, row in status_df.iterrows(): 
			name = row['first name']
			#print(name)
			address_dict = update_dict[name]
			#print(address_dict)
			if address_dict != None:
				for key, value in address_dict.items():
					print(key)
					# listings that are available and have gotten a response from realtor
					if len(value[0]) != 0: # check if there are responses that were captured
						timestamp_column_string = 'response timestamp ' + key[1]
						total_response_column_string = 'total responses ' + key[1]
						if str(row[timestamp_column_string]) in (None, '', 'nan', ' '): # this means that the cell is empty
							status_df.loc[index, timestamp_column_string] = str(value[0])
							status_df.loc[index, total_response_column_string] = len(value[0])
						else: 
							x = row[timestamp_column_string] # get the current value in the timestamp column
							y = row[total_response_column_string] # get the current number of responses in the number of responses column
							old_list = eval(x) # evalaute the list
							print(old_list)
							new_list = old_list + value[0]
							status_df.loc[index,timestamp_column_string] = str(new_list)
							old_total = int(y)
							print(old_total)
							status_df.loc[index, total_response_column_string] = len(new_list)

					# listings that are not available and have gotten a response		
					if len(value[1]) != 0:
						unavailable_timestamp_column_string = 'unavailable timestamp ' + key[1]
						total_unavailable_column_string = 'total unavailable ' + key[1]
						if str(row[unavailable_timestamp_column_string]) in (None, '', 'nan', ' '): # this means that the cell is empty
							status_df.loc[index, unavailable_timestamp_column_string] = str(value[0])
							status_df.loc[index, total_unavailable_column_string] = len(value[0])
						else: 
							x = row[unavailable_timestamp_column_string] # get the current value in the timestamp column
							y = row[total_unavailable_column_string] # get the current number of responses in the number of responses column
							old_list = eval(x) # evalaute the list
							print(old_list)
							new_list = old_list + value[1]
							status_df.loc[index,unavailable_timestamp_column_string] = str(new_list)
							old_total = int(y)
							print(old_total)
							status_df.loc[index, total_unavailable_column_string] = len(new_list)
		status_df.to_csv(status_sheet,mode='wb',index=False)
		counter += 1
