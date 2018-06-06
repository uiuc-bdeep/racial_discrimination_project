import os
import re
import csv
import sys
import random
import base64
import pickle
import psutil
import imaplib
import getpass
import datetime
import webbrowser
import linecache
import numpy as np
import pandas as pd
from time import sleep 
from selenium import webdriver
from pyvirtualdisplay import Display 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# COMMAND TO RUN THIS SCRIPT: python trulia_rental_message_sender.py trulia_rental_message_sender_data.txt <THE DAY YOU ARE RUNNING THIS SCRIPT[1-3]>

CUST_MSG = "I'm looking for a place in this neighborhood."

NUM_IDENTITES_PER_RACE = 6

NAME_CSS    = "#nameInput"  
EMAIL_CSS   = "#emailInput"
PHONE_CSS   = "#phoneInput"
SEND_CSS    = '#topPanelLeadForm > div > div > span > div > button'
MESSAGE_CSS = '#topPanelLeadForm > div > div > span > div > div.madlibsForm.form > div:nth-child(6) > a'
TEXTB_CSS   = '#textarea'

def initialize_data_sheets(status, email, phone, df_names, sold, LPI):
	num_cols = (LPI*3) + 1
	timestamp_cols = ['handled']

	for i in range(1, num_cols):
		timestamp_cols.append('timestamp ' + str(i))

	for i in range(1, num_cols): 
		timestamp_cols.append('address ' + str(i))
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
	sold_list = []

	with open(sold, 'wb') as fd: 
		pickle.dump(sold_list,fd)

	return df_timestamp, df_email,df_phone, sold_list

def get_dataframes(names, status, email,phone, sold,LPI): 
	df_names = pd.read_csv(names) 						# create a dataframe with the names csv

	if os.path.isfile(status) == False: 				# check if the status sheet exists
		print('Status Sheet Not Initialized\nInitializing ...')
		df_timestamp, df_email,df_phone, sold_list = initialize_data_sheets(status, email, phone, df_names, sold, LPI)

	else: 
		# create a dataframe from saved status sheet csv
		df_timestamp = pd.read_csv(status)
		df_email     = pd.read_csv(email) 
		df_phone     = pd.read_csv(phone)

		with open(sold,'rb') as fd: 
			sold_list = pickle.load(fd)

	return df_names, df_timestamp, df_email,df_phone, sold_list

def get_partitions(df_rentals): 
	# cut the main rentals dataframe down by a criteria MAY NEED CHANGING IN THE FUTURE
	df_mod_rentals   = df_rentals[(df_rentals['Bedroom_max'] == '3') & (df_rentals['Bathroom_max'] == 2.0)]

	# equally divide up the dataframe based on the number of races, in this case we have white, black, and hispanic
	split_df    = np.array_split(df_mod_rentals, 3)
	group_one   = split_df[0]
	group_two   = split_df[1]
	group_three = split_df[2]

	#  calculate the Listings Per Identity by getting the minimum of the three groups and dividing it by the number of identities per race
	LPI         = int(min([len(group_one), len(group_two), len(group_three)])/NUM_IDENTITES_PER_RACE)

	return group_one, group_two, group_three, LPI

def get_day_dict(df_rentals, day_num):
	 	group_one, group_two, group_three, LPI = get_partitions(df_rentals)

	 	day_trial_dict = {}
	 	if day_num == 1:
	 		day_trial_dict.update({'black': group_one, 'white': group_two, 'hispanic': group_three})
	 	elif day_num == 2:
	 		day_trial_dict.update({'black': group_two, 'white': group_three, 'hispanic': group_one})
	 	elif day_num == 3:  
	 		day_trial_dict.update({'black': group_three, 'white': group_one, 'hispanic': group_two})
	 	else: 
	 		print('not a valid number')
	 		exit()
 		return day_trial_dict, LPI

def wait_and_get(browser, cond, maxtime): 
	flag = True

	while flag:
		try: 
			ret = WebDriverWait(browser, maxtime).until(cond)
			sleep(2)
			ret = WebDriverWait(browser, maxtime).until(cond)
			flag = False
			return ret
		except TimeoutException:
			print("Time out")
			flag = False
			while len(browser.window_handles) > 1:
				browser.switch_to_window(browser.window_handles[-1])
				browser.close()
				browser.switch_to_window(browser.window_handles[0])
				flag = True
			if not flag:
				try:
					browser.find_elements_by_id("searchID").click()
					flag = True
				except:
					print("Time out without pop-ups. Exit.")
					return 0

		except ElementNotVisibleException:
			print("Element Not Visible, presumptuously experienced pop-ups")
			while len(browser.window_handles) > 1:
				browser.switch_to_window(browser.window_handles[-1])
				browser.close()
				browser.switch_to_window(browser.window_handles[0])
				flag = True

def get_prev_addr(handled_state,race,df_status): 
	# get a list of all of the previously inquired addresses
	prev_addresses = []
	df_race = df_status[df_status['racial category'] == race]

	for index,row in df_race.iterrows():
		for i in range(1,int(handled_state)+2): 
			address_string = 'address ' + str(i)
			if row[address_string] not in [None, '', ' ']: 
				prev_addresses.append((row[address_string][1:-2]).split(',')[0])

	return prev_addresses

def send_message(name, email, phone_num, address,url,send):
	fail_count = 0 # counter for how many times this script fails
	while True: 
		page_restart = 0 # tracker for restarting the finction
		options = Options() 
		options.set_headless(headless=True) # run in window less mode
		driver = webdriver.Firefox(firefox_options = options,executable_path='/usr/local/bin/geckodriver')
		driver.set_page_load_timeout(30) # set a time out for 30 secons
		display = Display(visible=0, size=(1024, 768)) # start display
		display.start() # start the display
		print('Drive Launched!') 
		try:
			driver.get(url) # start the driver window
			print(driver.title) # print the title of the page
			if driver.title == 'Access to this page has been denied.':
				driver.quit()
				display.stop()
				print('GOT BLOCKED... RESTARTING ' + str(address))
				return "RESTART DRIVER"
			
		except WebDriverException: # check for webdriver exception
			print('WebDriverException: Restarting... ')
			driver.quit()  
			display.stop()
			return "RESTART DRIVER" # "NEED NEW ADDRESS"

		
		send_handle = None # variable for the button click
		try: 
			waitlist_check = driver.find_element_by_css_selector('#WaitlistFormBottom > div:nth-child(1) > button:nth-child(1)')
			if waitlist_check: 
				driver.quit()
				display.stop()
				print("WAITLIST FOR " + address)
				return "NEED NEW ADDRESS"
		except NoSuchElementException:
			try: 
				name_handle = driver.find_element_by_css_selector(NAME_CSS)
			except NoSuchElementException:
				driver.quit()
				display.stop()
				print('Listing Already Sold: ' + str(address))
				print('------------------------')
				return "NEED NEW ADDRESS"

			# set the variables
			name_css  = NAME_CSS
			email_css = EMAIL_CSS
			phone_css = PHONE_CSS
			send_css  = SEND_CSS

			#while name_handle == 0: 
			name_cond   = EC.presence_of_element_located((By.CSS_SELECTOR,name_css))				
			name_handle = wait_and_get(driver, name_cond, 30)
			name_handle.send_keys(name) # once it is found, send the name string to it 

			# send the email string
			email_handle = driver.find_element_by_css_selector(email_css)
			email_handle.send_keys((str(email) + '@gmail.com'))

			# send the phone string
			phone_handle = driver.find_element_by_css_selector(phone_css)
			phone_handle.send_keys(str(phone_num))

			# if custom_msg_bool != True: 
			# 	message_handle = driver.find_element_by_css_selector(MESSAGE_CSS)
			# 	message_handle.click()
			# 	text_box       = driver.find_element_by_css_selector(TEXTB_CSS)
			# 	text_box.send_keys(Keys.COMMAND + 'a')
			# 	text_box.send_keys(Keys.BACKSPACE) 
			# 	text_box.send_keys(CUST_MSG)


			send_handle = driver.find_element_by_css_selector(send_css)

			# Send inquiry. This should be commented out until ready to test
			if send == 1:
				print('Clicking...')
				send_handle.click()
			else: 
				print('Not Clicking...')

			# save the current time and date
			time_sent = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			print('all handled')
			# sleep incase the page doesn't finish sending the inquiry
			sleep(2)
			#quit the driver and display
			driver.quit()
			display.stop()

			return time_sent


#---------------------------------------------------------------------------------------
# input: 
			# 1) path of names_market.csv 
			# 2) path of <city>_timestamp_status_sheet_<date>.csv
			# 3) path of <city>_email_status_sheet_<date>.csv
			# 4) path of <city>_phone_status_sheet_<date>.csv
			# 5) path of <city>_rentals_<date>.csv
			# 6) path of pickle txt file for sold listings
# output:  
			# 1) inquiries sent out to listings in <city>_rentals_<date>.csv
			# 2) <city>_timestamp_status_sheet_<date>.csv
			# 3) <city>_email_status_sheet_<date>.csv
			# 4) <city>_phone_status_sheet_<date>.csv
#---------------------------------------------------------------------------------------
def main():
	parameter_file_name = str(sys.argv[1])
	parameter_day_trial = int(sys.argv[2]) # can be a value of 1,2,3. The will tell the script which partition to use for a race. 
	parameter_send      = int(sys.argv[3]) # can be a value of 0 or 1. This will tell the script whether or not to actually send out inquiries
	line_num = 1
	while True:
		file_line = linecache.getline(parameter_file_name, line_num)
		if file_line is '':
			break
		else:
			file_line = re.sub('\n','',file_line)
			parameters = file_line.split(",") # parse the text file by the \ character

			# set the string passed in from the text files
			names_sheet 	   = parameters[0] 					# name_market.csv
			time_status_sheet  = parameters[1] 					# timestamp output csv
			email_status_sheet = parameters[2]					# email output csv
			phone_status_sheet = parameters[3] 					# phone output csv
			rentals_sheet 	   = parameters[4] 					# csv that contains listings
			sold_sheet         = parameters[5]					# pickle list containing listings that have been sold already

			df_rentals          = pd.read_csv(rentals_sheet)																																# create a dataframe with the rentals_sheet.
			df_rentals          = df_rentals[pd.notnull(df_rentals['Address'])].drop_duplicates(subset = 'Address').sample(frac = 1, random_state = 0)	 									# drop all the NA's in the original DF and shuffle
			day_trial_dict, LPI = get_day_dict(df_rentals, parameter_day_trial) 																											# get which partition of the df_rentals that a race will be sending inquiries to

			df_names, df_status, df_status_email, df_status_phone, sold_listings = get_dataframes(names_sheet, time_status_sheet, email_status_sheet, phone_status_sheet, sold_sheet,LPI)	# get all required dataframes 
			
			values = list(df_status['handled'].values)																																		# find the where the script left off last and set it to row_index
			row_index = values.index(min(values)) 

			# store the row of the dataframe where the script last left off
			row              = df_status.iloc[row_index]

			# store information about the person 
			handled_state    = row['handled']
			name             = row['first name'] + ' ' + row['last name']
			email            = row['email']
			phone_num        = row['phone number']
			race             = row['racial category']
			person_id        = row['person id']

			if int(handled_state) >= (int(LPI) * int(parameter_day_trial)): 
				print('All names have been handled\nexiting...')
				exit()

			print("HANDLING STATE " + str(handled_state) + '/' + str(LPI * parameter_day_trial) + '\n' +  str(person_id) + '. ' + str(name) + '\n' + '---------------------------------')

			df_cur_race_addr = day_trial_dict[race]                           	 					# all of the listings that this race can choose from on this day
			race_prev_addr   = get_prev_addr(handled_state, race, df_status)						# all of the listings that have been chosen on this day
			df_cur_race_addr = df_cur_race_addr[~df_cur_race_addr['Address'].isin(race_prev_addr)]  # take the difference of the two above by addresses
			df_cur_race_addr = df_cur_race_addr[~df_cur_race_addr['Address'].isin(sold_listings)]
			# create variables to store information about the listing that will be inquired
			time_stamp = "NEED NEW ADDRESS"
			address    = None
			url        = None 

			# create strings that will be used to located where to store data in df
			address_string  = str('address '   + str(handled_state+1))
			time_stamp_col  = str('timestamp ' + str(handled_state+1))
			# keep trying new address until a valid address is found
			while time_stamp == "NEED NEW ADDRESS":
				print('Acquiring New Address')
				random_address = df_cur_race_addr.sample(n = 1)					# randomly choose an address from rentals.csv
				address        = random_address['Address'].values[0]
				url            = random_address['URL'].values[0]
				time_stamp     = send_message(name, email, phone_num, address, url,parameter_send)  	# send out the inquiry and return the timestamp of when the inquiry was sent out
				while time_stamp == "RESTART DRIVER": 
					time_stamp = send_message(name, email, phone_num, address, url,parameter_send)
				if time_stamp == "NEED NEW ADDRESS":
					sold_listings.append(address)
				# after inquiry is sent outremove it from the list of possible listings to inquire
				df_cur_race_addr = df_cur_race_addr[~df_cur_race_addr['Address'].isin([address])]
				if df_cur_race_addr.empty: 		
					time_stamp = ' '								# if the list is empty, the skip
					address    = ' '
					url        = ' '
					print('NO MORE ADDRESSES FOR ' + race + ' GROUP')
					break

			# increment the handled 
			df_status.at[row_index,'handled'] += 1

			# update address/url and timstamp
			df_status.at[row_index,address_string] = str('(' + str(address) + ', '+ str(url) + ')')
			df_status.at[row_index,time_stamp_col] = time_stamp

			df_status_email.at[row_index,address_string] = address

			df_status_phone.at[row_index, address_string] = address

			#write back to csv 
			df_status.to_csv(time_status_sheet,mode='w',index=False)
			df_status_email.to_csv(email_status_sheet,mode='w',index=False)
			df_status_phone.to_csv(phone_status_sheet,mode='w',index=False)
			with open(sold_sheet, 'wb') as fd: 
				pickle.dump(sold_listings,fd)
			print(time_stamp)
			print('-------------------------------------------------------------------------------------')
		#sleep(40)
		#line_num+=1

#---------------------------------------------------------------------------------------
# 		-to run: 
#				- python trulia_rental_messsage_sender.py trulia_rental_message_sender_data.txt <day trial> <send>
#			
#				- day trial : can be a value of 1, 2, or 3. 
# 				- send      : can be a value of 0 or 1. 0 for do not send inquiries. 1 for send inquiries 
#---------------------------------------------------------------------------------------
for proc in psutil.process_iter():								# check if there is another instance of this script running 
	if 'python3.6' in proc.name() and proc.pid != os.getpid():
		print('-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_')
		print('-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_')
		print('_-_-_-_-_-_-_-_-_-_Second process running... Killing process_-_-_-_-_-_-_-_-_-')
		print('-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_')
		print('-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_')
		exit()
main()