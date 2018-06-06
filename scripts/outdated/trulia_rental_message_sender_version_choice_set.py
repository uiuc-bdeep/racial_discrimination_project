import sys
import imaplib
import getpass
import datetime
import webbrowser
import linecache
import os
import csv
import random
import re
from time import sleep 
import numpy as np
import pandas as pd
import base64
from selenium.webdriver.firefox.options import Options
from pyvirtualdisplay import Display 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException

custom_message = "I'm looking for a place in this neighborhood."

page_one_name__css = "#nameInput"  
page_one_email_css = "#emailInput"
page_one_phone_css = "#phoneInput"
page_one_send__css = '#topPanelLeadForm > div > div > span > div > button'
page_one_mess__css = '#topPanelLeadForm > div > div > span > div > div.madlibsForm.form > div:nth-child(6) > a'
page_one_textb_css = '#textarea'

def initialize_data_sheets(status_sheet,phone_status_sheet,df_input):
	df_status_list = ['handled'     , 'timestamp 1'       , 'timestamp 2'          , 'timestamp 3'         , 'timestamp 4'             ,
					  'timestamp 5' , 'timestamp 6'       , 'timestamp 7'          , 'timestamp 8'         , 'timestamp 9'             ,
					  'timestamp 10', 'timestamp 11'      , 'timestamp 12'         ,
					  'address 1'   , 'total responses 1' , 'response timestamp 1' , 'total unavailable 1' , 'unavailable timestamp 1' ,
					  'address 2'   , 'total responses 2' , 'response timestamp 2' , 'total unavailable 2' , 'unavailable timestamp 2' ,
					  'address 3'   , 'total responses 3' , 'response timestamp 3' , 'total unavailable 3' , 'unavailable timestamp 3' ,
					  'address 4'   , 'total responses 4' , 'response timestamp 4' , 'total unavailable 4' , 'unavailable timestamp 4' ,
					  'address 5'   , 'total responses 5' , 'response timestamp 5' , 'total unavailable 5' , 'unavailable timestamp 5' ,
					  'address 6'   , 'total responses 6' , 'response timestamp 6' , 'total unavailable 6' , 'unavailable timestamp 6' , 
					  'address 7'   , 'total responses 7' , 'response timestamp 7' , 'total unavailable 7' , 'unavailable timestamp 7' ,
					  'address 8'   , 'total responses 8' , 'response timestamp 8' , 'total unavailable 8' , 'unavailable timestamp 8' ,
					  'address 9'   , 'total responses 9' , 'response timestamp 9' , 'total unavailable 9' , 'unavailable timestamp 9' ,
					  'address 10'  , 'total responses 10', 'response timestamp 10', 'total unavailable 10', 'unavailable timestamp 10',
					  'address 11'  , 'total responses 11', 'response timestamp 11', 'total unavailable 11', 'unavailable timestamp 11',
					  'address 12'  , 'total responses 12', 'response timestamp 12', 'total unavailable 12', 'unavailable timestamp 12']
	# new column names for the phone sheet
	df_phone_list = ['address 1' ,'voicemail responses 1' , 'voicemail timestamp 1' , 'voicemail minutes 1' , 'text responses 1' , 'text timestamp 1' , 'unavailable responses 1' , 'unavailable timestamp 1' ,
					 'address 2' ,'voicemail responses 2' , 'voicemail timestamp 2' , 'voicemail minutes 2' , 'text responses 2' , 'text timestamp 2' , 'unavailable responses 2' , 'unavailable timestamp 2' ,
					 'address 3' ,'voicemail responses 3' , 'voicemail timestamp 3' , 'voicemail minutes 3' , 'text responses 3' , 'text timestamp 3' , 'unavailable responses 3' , 'unavailable timestamp 3' ,
					 'address 4' ,'voicemail responses 4' , 'voicemail timestamp 4' , 'voicemail minutes 4' , 'text responses 4' , 'text timestamp 4' , 'unavailable responses 4' , 'unavailable timestamp 4' ,
					 'address 5' ,'voicemail responses 5' , 'voicemail timestamp 5' , 'voicemail minutes 5' , 'text responses 5' , 'text timestamp 5' , 'unavailable responses 5' , 'unavailable timestamp 5' ,
					 'address 6' ,'voicemail responses 6' , 'voicemail timestamp 6' , 'voicemail minutes 6' , 'text responses 6' , 'text timestamp 6' , 'unavailable responses 6' , 'unavailable timestamp 6' ,
					 'address 7' ,'voicemail responses 7' , 'voicemail timestamp 7' , 'voicemail minutes 7' , 'text responses 7' , 'text timestamp 7' , 'unavailable responses 7' , 'unavailable timestamp 7' ,
					 'address 8' ,'voicemail responses 8' , 'voicemail timestamp 8' , 'voicemail minutes 8' , 'text responses 8' , 'text timestamp 8' , 'unavailable responses 8' , 'unavailable timestamp 8' ,
					 'address 9' ,'voicemail responses 9' , 'voicemail timestamp 9' , 'voicemail minutes 9' , 'text responses 9' , 'text timestamp 9' , 'unavailable responses 9' , 'unavailable timestamp 9' ,
					 'address 10','voicemail responses 10', 'voicemail timestamp 10', 'voicemail minutes 10', 'text responses 10', 'text timestamp 10', 'unavailable responses 10', 'unavailable timestamp 10',
					 'address 11','voicemail responses 11', 'voicemail timestamp 11', 'voicemail minutes 11', 'text responses 11', 'text timestamp 11', 'unavailable responses 11', 'unavailable timestamp 11',
					 'address 12','voicemail responses 12', 'voicemail timestamp 12', 'voicemail minutes 12', 'text responses 12', 'text timestamp 12', 'unavailable responses 12', 'unavailable timestamp 12',
					 'undeterminable']

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

def get_prev_addr(handled_state): 
	# get a list of all of the previously inquired addresses
	prev_addresses = []
	if handled_state > 0: 
		for i in range(1,handled_state + 1): 
			prev_addresses.append((row["address " + str(i)][1:-2]).split(',')[0])
	return prev_addresses

def send_message(name, email, phone_num, url, custom_msg_bool):
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
				return "Failed: New Address"

		if page_restart == 0: # check if the page needs to be restarted
			page_num = 1 # indicates the page type CAN BE 1 OR 2 
			send_handle = None # variable for the button click
			try:
				name_handle = driver.find_element_by_css_selector(page_one_name__css)
			except NoSuchElementException:
				driver.quit()
				display.stop()
				print('Listing Already Sold')
				return "Failed: New Address"

			print('PAGE NUMBER IS ' + str(page_num))
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

			if custom_msg_bool != True: 
				message_handle = driver.find_element_by_css_selector(page_one_mess__css)
				message_handle.click()
				text_box       = driver.find_element_by_css_selector(page_one_textb_css)
				text_box.send_keys(Keys.COMMAND + 'a')
				text_box.send_keys(Keys.BACKSPACE) 
				text_box.send_keys(custom_message)


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

parameter_file_name = sys.argv[1]
line_num = 1
while True:
	file_line = linecache.getline(parameter_file_name, line_num)
	if file_line is '':
		break
	else:
		file_line = re.sub('\n','',file_line)
		print(file_line)
		parameters = file_line.split(",") # parse the text file by the \ character

		# set the string passed in from the text files
		name_sheet 	       = parameters[0] # name sheet
		status_sheet  	   = parameters[1] # status sheet
		phone_status_sheet = parameters[2] # phone output csv
		address_sheet 	   = parameters[3] # csv that contains listings
		choice_set_sheet   = parameters[4] # person-to-address csv


		df_input      = pd.read_csv(name_sheet)       # create a dataframe with the return_sheet.
		df_address    = pd.read_csv(address_sheet)    # create a dataframe with the rentals_sheet.
		df_choice_set = pd.read_csv(choice_set_sheet) # create a dataframe with the choice_set_sheet. 

		if os.path.isfile(status_sheet) == False: # check if the status sheet exists
			print('Status Sheet Not Initialized\n Initializing ...')
			df_status, df_status_phone = initialize_data_sheets(status_sheet,phone_status_sheet,df_input)

		else: 
			# create a dataframe from saved status sheet csv
			df_status        = pd.read_csv(status_sheet)
			df_status_phone  = pd.read_csv(phone_status_sheet)

		# check if all listing have been handled by checking the last value in the handled column
		if df_status.iloc[-1]['handled'] == 12: 
			print('All names have been handled')

		else:
			# find the where the script left off last and set it to row_index
			values = list(df_status['handled'].values)
			row_index = values.index(min(values)) 

			# store the row of the dataframe where the script last left off
			row = df_status.iloc[row_index]
			handled_state    = row['handled']

			# store information about the person 
			person_id        = row['person id']
			name             = row['first name'] + ' ' + row['last name'] # full name
			email            = row['email']								  # email
			phone_num        = row['phone number']						  # phone number
			pair_id          = int(row['pair id'])						  # the id if the identity is a part of a pair
			prev_addresses   = get_prev_addr(handled_state)				  # previously inquired addresses

			custom_msg_bool  = random.choice([True, False])				  # random boolean to check whether or not to send a custom message

			address          = None 									  
			url              = None 									  # MAY NOT NEED THIS ANYMORE
			time_stamp       = None

			# create strings to locate the correct column in the status dataframe
			address_string  = str('address ' + str(handled_state+1))
			time_stamp_col  = str('timestamp ' + str(handled_state+1))
			addr_num_set    = None
			pair_msg_status = None

			# check if the curent name is a part of a pair
			if pair_id != 0: 
				# if it is, then get the pair row index 
				pair_row_index = df_status.iloc[pair_id]['person id']
				addr_num_set   = df_choice_set[str(pair_row_index - 1)].values


			else: 
				# get the address number column for the identity
				addr_num_set   = df_choice_set[str(person_id)].values
			addr_num_set = [ int(x) for x in addr_num_set ]
			# randomly select a address in the set of address numbers
			rand_addr      = int(random.choice(addr_num_set))
			# get the row of the randomly selected address
			selected_addr  = df_address.iloc[rand_addr - 1]
			# get the address itself
			address        = selected_addr['Address']
			# check if the address was already sent an inquiry
			if address in prev_addresses: 
				while address in prev_addresses: 
					rand_addr      = int(random.choice(addr_num_set))
					selected_addr  = df_address.iloc[rand_addr - 1]
					address        = selected_addr['Address']
			# get the url of the address listing
			url            = selected_addr['URL']

			# send out the inquiry and return the timestamp of when the inquiry was sent out
 			time_stamp = send_message(name, email, phone_num, url, custom_msg_bool)

 			# in case the listing is taken off the market, try again 
 			while time_stamp == "Failed: New Address":
 				print(rand_addr)
 				addr_num_set = [x for x in addr_num_set if x != rand_addr]
 				print(addr_num_set)
 				print('Acquiring New Address')
 				rand_addr      = int(random.choice(addr_num_set))
				selected_addr  = df_address.iloc[rand_addr - 1]
				address        = selected_addr['Address']
				if address in prev_addresses: 
					while address in prev_addresses: 
						rand_addr      = int(random.choice(addr_num_set))
						selected_addr  = df_address.iloc[rand_addr - 1]
						address        = selected_addr['Address']
				time_stamp = send_message(name, email, phone_num, url, custom_msg_bool)
				url            = selected_addr['URL']

 			# increment the handled 
 			df_status.at[row_index,'handled'] += 1

 			# update address/url and timstamp
 			df_status.set_value(row_index,address_string,str('(' + str(address) + ', '+ str(custom_msg_bool)  + ', ' + str(url) + ')'))
 			df_status.at[row_index,time_stamp_col] = time_stamp

 			df_status_phone.set_value(row_index,address_string,str('(' + str(address) + ', '+ str(url) + ')'))

 			#write back to csv 
 			df_status.to_csv(status_sheet,mode='wb',index=False)
 			df_status_phone.to_csv(phone_status_sheet,mode='wb',index=False)
 			print('----------------------------------------------------------------------------')

	line_num += 1