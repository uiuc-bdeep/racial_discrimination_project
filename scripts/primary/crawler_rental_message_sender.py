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

def initialize_data_sheets(status, email, phone, df_names, handled):
	num_cols = 10
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
	handled_list = []

	with open(handled, 'wb') as fd: 
		pickle.dump(handled_list,fd)

	return df_timestamp, df_email,df_phone, handled_list

def get_dataframes(names, status, email,phone, sold): 
	df_names = pd.read_csv(names) 						# create a dataframe with the names csv

	if os.path.isfile(status) == False: 				# check if the status sheet exists
		print('Status Sheet Not Initialized\nInitializing ...')
		df_timestamp, df_email,df_phone, sold_list = initialize_data_sheets(status, email, phone, df_names, sold)

	else: 
		# create a dataframe from saved status sheet csv
		df_timestamp = pd.read_csv(status)
		df_email     = pd.read_csv(email) 
		df_phone     = pd.read_csv(phone)

		with open(sold,'rb') as fd: 
			sold_list = pickle.load(fd)

	return df_names, df_timestamp, df_email,df_phone, sold_list

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

def send_message(name, email, phone_num, address,url,send):
	fail_count = 0 # counter for how many times this script fails
	while True: 
		page_restart = 0 # tracker for restarting the finction
		options = Options() 
		options.add_argument("-headless")
		driver = webdriver.Firefox(firefox_options = options,executable_path='/usr/local/bin/geckodriver')
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
				return "WAITLIST"
		except NoSuchElementException:
			try: 
				name_handle = driver.find_element_by_css_selector(NAME_CSS)
			except NoSuchElementException:
				driver.quit()
				display.stop()
				print('Listing Already Sold: ' + str(address))
				print('------------------------')
				return "SOLD"

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
	parameter_send      = int(sys.argv[2]) # can be a value of 0 or 1. This will tell the script whether or not to actually send out inquiries
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
			handled_sheet      = parameters[5]					# pickle list containing listings that have been sold already

			df_rentals          = pd.read_csv(rentals_sheet)																																# create a dataframe with the rentals_sheet.
			df_rentals          = df_rentals[pd.notnull(df_rentals['Address'])].dropna(subset = ['state']).drop_duplicates(subset = 'Address')	 		# drop all the NA's in the original DF and shuffle

			#day_trial_dict, LPI = get_day_dict(df_rentals, parameter_day_trial) 																											# get which partition of the df_rentals that a race will be sending inquiries to
			df_names, df_status, df_status_email, df_status_phone, handled_listings = get_dataframes(names_sheet, time_status_sheet, email_status_sheet, phone_status_sheet, handled_sheet)	# get all required dataframes 
			# remove listings that have been completed or have already gone off the market
			df_rentals = df_rentals[~df_rentals['Address'].isin(handled_listings)]
			# if all rentals have been completed or gone off the market, then simply exit
			if df_rentals.empty == True:
				print('No more listings...\nExiting...')
				exit()

			# find the earliest last_run time
			values         = list(df_rentals['last_run'].values)																																		# find the where the script left off last and set it to row_index
			addr_row_index = values.index(min(values))
			print(addr_row_index)
			# store the row of the earliest run address
			curr_addr  = df_rentals.iloc[addr_row_index]
			print(curr_addr)
			# last time the this address was run
			cur_addr_time = datetime.datetime.strptime(str(curr_addr['last_run']), '%Y-%m-%d %H:%M:%S')

			# if an address has just been scraped scraped the timestamp will be 2018-10-10 10:10:10 and will have an inquiry sent out immediately
			if cur_addr_time != datetime.datetime.strptime('2019-10-10 10:10:10','%Y-%m-%d %H:%M:%S'):
				# if the last run was less than 24 hours ago then exit
				if cur_addr_time <= (datetime.datetime.now().replace(microsecond=0) - datetime.timedelta(hours = 24)):
					print('No Address Older Than 24 Hours...\nExiting...')
					exit()

			# store information about the listings
			address  = curr_addr['Address']
			url      = curr_addr['URL']
			print(curr_addr['state'])
			# remaining races that need to send an inquiry to this address
			rem_races= curr_addr['state'].split(',')
			print(rem_races)
			race     = random.choice(rem_races)

			# the identity that will be sending out the inquiry based on a random pick
			iden_row_index = random.choice(list((df_status[df_status['racial category'] == race].index)))
			iden_row       = df_status.iloc[iden_row_index]
			print(iden_row)

			# store information about the person 
			handled_state    = iden_row['handled']
			name             = iden_row['first name'] + ' ' + iden_row['last name']
			email            = iden_row['email']
			phone_num        = iden_row['phone number']
			race             = iden_row['racial category']
			person_id        = iden_row['person id']
			
			# run try to send the inquiry out 
			time_stamp = send_message(name, email, phone_num, address, url, parameter_send)
			# if send_message_returns restart driver, then try sending again
			while time_stamp == 'RESTART DRIVER':
				time_stamp = send_message(name, email, phone_num, address, url, parameter_send)

			# if send_message return waitlist or sold, then we know that we cannot send an inquiry to this listing so add it tot eh handled_listings list
			# it will not be checked in later iterations
			if time_stamp == 'WAITLIST' or time_stamp == 'SOLD':
				handled_listings.append(address)
				with open(handled_sheet, 'wb') as fd: 
					pickle.dump(handled_listings,fd)
				print(str(address) + ': ' + str(time_stamp))
				print('Exiting...')
				exit()
			
			# remove the handled race from this address row's state column
			rem_races.remove(race)
			print(rem_races)
			print(race)
			df_rentals.at[addr_row_index,'state']    = str(rem_races).replace('[','').replace(']','').replace("'",'').replace(' ','')
			df_rentals.at[addr_row_index,'last_run'] = time_stamp

			# incremented the handled state 
			df_status.at[iden_row_index,'handled'] += 1

			# create strings that will be used to located where to store data in df
			address_string  = str('address '   + str(handled_state+1))
			time_stamp_col  = str('timestamp ' + str(handled_state+1))

			# update address/url and timstamp
			df_status.at[iden_row_index,address_string] = str('(' + str(address) + ', '+ str(url) + ')')
			df_status.at[iden_row_index,time_stamp_col] = time_stamp

			df_status_email.at[iden_row_index,address_string] = address

			df_status_phone.at[iden_row_index, address_string] = address

			#write back to csv 
			df_rentals.to_csv(rentals_sheet,mode = 'w', index =False)
			df_status.to_csv(time_status_sheet,mode='w',index=False)
			df_status_email.to_csv(email_status_sheet,mode='w',index=False)
			df_status_phone.to_csv(phone_status_sheet,mode='w',index=False)
			with open(handled_sheet, 'wb') as fd: 
				pickle.dump(handled_listings,fd)
			print(time_stamp)
			print('-------------------------------------------------------------------------------------')
		line_num+=1

#---------------------------------------------------------------------------------------
# 		-to run: 
#				- python trulia_rental_messsage_sender.py trulia_rental_message_sender_data.txt <day trial> <send>
#			
#				- day trial : can be a value of 1, 2, or 3. 
# 				- send      : can be a value of 0 or 1. 0 for do not send inquiries. 1 for send inquiries 
#---------------------------------------------------------------------------------------
for proc in psutil.process_iter():								# check if there is another instance of this script running 
	if 'python' in proc.name() and proc.pid != os.getpid():
		print('-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_')
		print('_-_-_-_-_-_-_-_-_-_Second process running... Killing process_-_-_-_-_-_-_-_-_-')
		print('-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_')
		exit()
main()