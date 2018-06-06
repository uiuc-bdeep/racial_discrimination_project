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



def process_message(M, num, msg, username, address_dict):
	body = '' # initialize the body
	for part in msg.walk():
		if part.get_content_type() == 'text/plain':
			body = part.get_payload() # get the contents of the body

	subject = email.header.decode_header(msg['Subject'])[0][0]
	from_header = email.header.decode_header(msg['From'])[0][0]
	to_header = email.header.decode_header(msg['To'])[0][0]

	print("To: " + str(to_header) + "\n" + "From: " + str(from_header) + "\n" + "Subject: " + str(subject))

	# create a dictionary -> attach a name to a timestamp
	if 'Trulia' not in from_header:
		for key, value in address_dict.items(): 
			num = key.split(',')
			num = num[0].split(' ')
			print(num[0][1:])
			if str(num[0][1:]) in body:  # check to see if the email has a street number in it
				date_tuple = email.utils.parsedate_tz(msg['Date']) # if it does then get the time
				local_date = str(datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple)).strftime('%Y-%m-%d %H:%M:%S'))
				print('FOUND A MATCH!')
				print('From :' + from_header +' \n' + 'Subject: ' + subject + '\n' +  "Time: " + local_date)
				address_dict[key].append(local_date)
				#mov = M.store("1:*",'+X-GM-LABELS', '\\Important') # store the email in starred
				#mov = M.store("1:*",'+X-GM-LABELS', '\\Trash')
				print('Email Stored in Starred')

	return address_dict

def process_mailbox(M, username, address_dict):
	rv, data = M.search(None, "ALL")
	if rv != 'OK':
		print "No messages found!"
		return

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
		count = 1
		# iterate throught all of the names to handle each name individually
		for index, row in status_df.iterrows():
			M = imaplib.IMAP4_SSL('imap.gmail.com')
			exit()
			# get the row's information
			name     = row['first name']
			username = row['email'] 
			address_list = [] 
			count +=1 
			for i in range(0,5): # this will go through address 1 to address 5 
				address_list.append(row['address ' + str(i + 1)] + ',' + str(i + 1))
			address_dict = {k:[] for k in address_list}
			try:
				rv, data = M.login(username, 'BdeepTrulia') # log into the gmail accounts, print rv and data if it starts failing 
			except imaplib.IMAP4.error:
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
					if len(value) != 0:
						timestamp_column_string = 'response timestamp ' + key[-1]
						total_response_column_string = 'total responses ' + key[-1]
						if str(row[timestamp_column_string]) in (None, '', 'nan', ' '): # this means that the cell is empty
							status_df.loc[index,timestamp_column_string] = str(value)
							status_df.loc[index, total_response_column_string] = len(value)
						else: 
							x = row[timestamp_column_string]
							y = row[total_response_column_string]
							#print(x)
							old_list = eval(x)
							print(old_list)
							new_list = old_list + value
							status_df.loc[index,timestamp_column_string] = str(new_list)
							old_total = int(y)
							print(old_total)
							status_df.loc[index, total_response_column_string] = str(old_total + len(value))
		status_df.to_csv(status_sheet,mode='wb',index=False)
		counter += 1