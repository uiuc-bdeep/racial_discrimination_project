import os
import re
import csv
import sys
import random
import base64
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
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# COMMAND TO RUN THIS SCRIPT: python trulia_rental_message_sender.py trulia_rental_message_sender_data.txt <THE DAY YOU ARE RUNNING THIS SCRIPT[1-3]>

custom_message = "I'm looking for a place in this neighborhood."

number_of_identities_per_race = 6

page_one_name__css = "#nameInput"  
page_one_email_css = "#emailInput"
page_one_phone_css = "#phoneInput"
page_one_send__css = '#topPanelLeadForm > div > div > span > div > button'
page_one_mess__css = '#topPanelLeadForm > div > div > span > div > div.madlibsForm.form > div:nth-child(6) > a'
page_one_textb_css = '#textarea'

def initialize_data_sheets(status_sheet,phone_status_sheet,df_input,LPI):
	df_status_list = ['handled']
	for i in range(1,LPI + 1):
		df_status_list.append('timestamp ' + str(i))
	for i in range(1,LPI + 1): 
		df_status_list.append('address ' + str(i))
		df_status_list.append('total responses ' + str(i))
		df_status_list.append('response timestamp 1' + str(i))
		df_status_list.append('total unavailable ' + str(i))
		df_status_list.append('unavailable ' + str(i))

	# new column names for the phone sheet
	df_phone_list = []
	for i in range(1,LPI+1):
		df_phone_list.append('address ' + str(i)) 
		df_phone_list.append('voicemail responses ' + str(i)) 
		df_phone_list.append('voicemail timestamp ' + str(i)) 
		df_phone_list.append('voicemail minutes ' + str(i)) 
		df_phone_list.append('text responses ' + str(i)) 
		df_phone_list.append('text timestamp ' + str(i)) 
		df_phone_list.append('unavailable responses ' + str(i)) 
		df_phone_list.append('unavailable timestamp ' + str(i)) 
	df_phone_list.append('indeterminable')

	# empty dataframe with new columns for status sheet 
	df_new                = (pd.DataFrame(columns=df_status_list)).fillna(' ')

	# create a new dataframe from the return sheet
	df_status             = df_input[df_input.columns[0:9]] 
	# concatenate old values with the new columns
	df_status             = pd.concat([df_status, df_new], axis = 1).fillna(' ')
	df_status['handled']  = 0
	df_status.to_csv(status_sheet,mode='wb',index=False)

	#empty dataframe with new columns for phone sheet
	df_new                = (pd.DataFrame(columns=df_phone_list)).fillna(' ')

	# create a new dataframe from the return sheet
	df_status_phone    = df_input[df_input.columns[0:9]]
	# concatenate old values with the new columns
	df_status_phone    = pd.concat([df_status_phone, df_new], axis = 1).fillna(' ')
	df_status_phone.to_csv(phone_status_sheet,mode='wb',index=False)

	return df_status, df_status_phone

def get_dataframes(names_sheet, status_sheet, phone_status_sheet, LPI): 
	df_input   = pd.read_csv(names_sheet) # create a dataframe with the return_sheet.
	if os.path.isfile(status_sheet) == False: # check if the status sheet exists
			print('Status Sheet Not Initialized\n Initializing ...')
			df_status, df_status_phone = initialize_data_sheets(status_sheet,phone_status_sheet,df_input, LPI)

	else: 
		# create a dataframe from saved status sheet csv
		df_status = pd.read_csv(status_sheet)
		df_status_phone  = pd.read_csv(phone_status_sheet)

	return df_input, df_status, df_status_phone

def get_partitions(df_rentals): 
	# cut the main rentals dataframe down by a criteria MAY NEED CHANGING IN THE FUTURE
	df_mod_rentals   = df_rentals[df_rentals['Bedroom_max'] == '3']
	# equally divide up the dataframe based on the number of races, in this case we have white, black, and hispanic
	split_df    = np.array_split(df_mod_rentals, 3)
	group_one   = split_df[0]
	group_two   = split_df[1]
	group_three = split_df[2]
	#  calculate the Listings Per Identity by getting the minimum of the three groups and dividing it by the number of identities per race
	LPI         = min([len(group_one), len(group_two), len(group_three)])/number_of_identities_per_race

	return group_one, group_two, group_three, LPI

def get_day_dict(df_rentals, day_num):
	 	group_one, group_two, group_three, LPI = get_partitions(df_rentals)
		
		day_trial_dict = {}
		if day_num == 1:
			day_trial_dict.update({'black': group_one, 'white': group_two, 'hispanic': group_three})
		elif day_num == 2:
			day_trial_dict.update({'black': group_two, 'white': group_thee, 'hispanic': group_one})
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
			print "Time out"
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
					print "Time out without pop-ups. Exit."
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
	print(race)
	df_race = df_status[df_status['racial category'] == race]

	if handled_state > 0: 
		for index,row in df_race.iterrows():
			for i in range(1,handled_state + 1): 
				address_string = 'address ' + str(i)
				if row[address_string] != None: 
					prev_addresses.append((row[address_string][1:-2]).split(',')[0])
	return prev_addresses

def send_message(name, email, phone_num, url):
	fail_count = 0 # counter for how many times this script fails
	while True: 
		page_restart = 0 # tracker for restarting the finction
		options = Options() 
		options.add_argument('-headless') # run in window less mode
		driver = webdriver.Firefox()#executable_path='/usr/local/bin/geckodriver',firefox_binary='/usr/bin/firefox',firefox_options=options)
		driver.set_page_load_timeout(30) # set a time out for 30 secons
		print('Drive Launched!') 
		try:
			display = Display(visible=0, size=(1024, 768)) # start display
			display.start() # start the display
			driver.get(url) # start the driver window
			print(driver.title) # print the title of the page
			
		except WebDriverException: # check for webdriver exception
			driver.quit()  
			display.stop()
			fail_count += 1
			page_restart = 1
			if fail_count > 3:
				return "NEED NEW ADDRESS"

		if page_restart == 0: # check if the page needs to be restarted
			send_handle = None # variable for the button click
			try:
				name_handle = driver.find_element_by_css_selector(page_one_name__css)
			except NoSuchElementException:
				driver.quit()
				display.stop()
				print('Listing Already Sold')
				return "NEED NEW ADDRESS"

			# set the variables
			name_css  = page_one_name__css
			email_css = page_one_email_css
			phone_css = page_one_phone_css
			send_css  = page_one_send__css

			#while name_handle == 0: 
			name_cond = EC.presence_of_element_located((By.CSS_SELECTOR,name_css))				
			name_handle = wait_and_get(driver, name_cond, 30)
			name_handle.send_keys(name) # once it is found, send the name string to it 

			# send the email string
			email_handle = driver.find_element_by_css_selector(email_css)
			email_handle.send_keys((str(email) + '@gmail.com'))

			# send the phone string
			phone_handle = driver.find_element_by_css_selector(phone_css)
			phone_handle.send_keys(str(phone_num))

			# if custom_msg_bool != True: 
			# 	message_handle = driver.find_element_by_css_selector(page_one_mess__css)
			# 	message_handle.click()
			# 	text_box       = driver.find_element_by_css_selector(page_one_textb_css)
			# 	text_box.send_keys(Keys.COMMAND + 'a')
			# 	text_box.send_keys(Keys.BACKSPACE) 
			# 	text_box.send_keys(custom_message)


			send_handle = driver.find_element_by_css_selector(send_css)

			# Send inquiry. This should be commented out until ready to test
			# send_handle.click()

			# save the current time and date
			time_sent = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			print('all handled')
			# sleep incase the page doesn't finish sending the inquiry
			sleep(2)
			#quit the driver and display
			driver.quit()
			display.stop()

			return time_sent

parameter_file_name  = sys.argv[1]
parameter_day_trial = sys.argv[2] # can be a value of 1,2,3. The will tell the script which partition to use for a race. 
line_num = 1
while True:
	file_line = linecache.getline(parameter_file_name, line_num)
	if file_line is '':
		break
	else:
		while True: 
			file_line = re.sub('\n','',file_line)
			parameters = file_line.split(",") # parse the text file by the \ character

			# set the string passed in from the text files
			names_sheet 	   = parameters[0] 			# name_market.csv
			status_sheet  	   = parameters[1] 			# status sheet
			phone_status_sheet = parameters[2] 			# phone output csv
			rentals_sheet 	   = parameters[3] 			# csv that contains listings

			df_rentals          = pd.read_csv(rentals_sheet)															# create a dataframe with the rentals_sheet.
			df_rentals          = df_rentals[pd.notnull(df_rentals['Address'])].sample(frac = 1, random_state = 0)	 	# drop all the NA's in the original DF and shuffle
			print(df_rentals)
			day_trial_dict, LPI = get_day_dict(df_rentals, int(parameter_day_trial)) 									# get which partition of the df_rentals that a race will be sending inquiries to

			df_input, df_status, df_status_phone = get_dataframes(names_sheet, status_sheet, phone_status_sheet, LPI)	# get all required dataframes 
			
			if df_status.iloc[-1]['handled'] == LPI: 								# check if all listing have been handled by checking the last value in the handled column
				print('All names have been handled\nexiting...')
				exit()

			values = list(df_status['handled'].values)								# find the where the script left off last and set it to row_index
			row_index = values.index(min(values)) 

			# store the row of the dataframe where the script last left off
			row              = df_status.iloc[row_index]
			handled_state    = row['handled']
			# store information about the person 
			name             = row['first name'] + ' ' + row['last name']
			email            = row['email']
			phone_num        = row['phone number']
			race             = row['racial category']
			df_race_cur_addr = day_trial_dict[race]                           	 	# all of the listings that this race can choose from on this day
			race_prev_addr   = get_prev_addr(handled_state, race, df_status)		# all of the listings that have been chosen on this day
			df_race_cur_addr = df_race_cur_addr[~df_race_cur_addr['Address'].isin(race_prev_addr)]

			# create variables to store information about the listing that will be inquired
			time_stamp = "NEED NEW ADDRESS"
			address    = None
			url        = None 

			# create strings that will be used to located where to store data in df
			address_string  = str('address ' + str(handled_state+1))
			time_stamp_col  = str('timestamp ' + str(handled_state+1))

	 		# keep trying new address until a valid address is found
	 		while time_stamp == "NEED NEW ADDRESS":
	 			print('Acquiring New Address')
	 			random_address = df_race_cur_addr.sample(n = 1)					# randomly choose an address from rentals.csv
				address        = random_address['Address'].values[0]
				url            = random_address['URL'].values[0]
				time_stamp     = send_message(name, email, phone_num, url)  	# send out the inquiry and return the timestamp of when the inquiry was sent out
				if time_stamp == 'NEED NEW ADDRESS': 							# if the address is not able to be inquired then remove it from the list of possible listings to inquire
					df_race_cur_addr = df_race_cur_addr[~df_race_cur_addr['Address'].isin([address])]
				if df_race_cur_addr.empty: 										# if the list is empty, the skip
					print('NO MORE ADDRESSES FOR ' + race + ' GROUP')
					break

			# increment the handled 
			df_status.at[row_index,'handled'] += 1

			# update address/url and timstamp
			df_status.set_value(row_index,address_string,str('(' + str(address) + ', '+ str(url) + ')'))
			df_status.at[row_index,time_stamp_col] = time_stamp

			#write back to csv 
			df_status.to_csv(status_sheet,mode='wb',index=False)
			print('----------------------------------------------------------------------------')