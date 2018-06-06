import sys
import imaplib
import getpass
import email
import email.header
import datetime
import re
import webbrowser
import sys
import linecache
import os
import csv
import datetime

#from pyvirtualdisplay import Display 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait

import re
from time import sleep 
import numpy as np
import pandas as pd
import base64

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
					print "Time out without pop-ups. Return."
					return 0


		except ElementNotVisibleException:
			print("Element Not Visible, presumptuously experienced pop-ups")
			while len(browser.window_handles) > 1:
				browser.switch_to_window(browser.window_handles[-1])
				browser.close()
				browser.switch_to_window(browser.window_handles[0])
				flag = True

def get_urls(driver, house_type):
	listings_url = []
	foreclosure_url = []
	page = 1
	if house_type == "sold":
		WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "moreToggle"))).click()
		WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='filterForm']/div[1]/div/div/a[2]"))).click()
		url = driver.current_url
	while True: 
		if house_type != "sold":
			next_page_cond = EC.presence_of_element_located((By.CSS_SELECTOR,'i.iconRightOpen:nth-child(1)'))
			next_page_handle = wait_and_get(driver, next_page_cond, 30)

		listings_on_page = []

		if house_type == "sold":
			listings_on_page = set(re.findall(r'/(?:los-angeles)/.*?"', driver.page_source.encode("utf-8")))
			
		else:
			listings_on_page = set(re.findall(r'/(?:property)/.*?"',driver.page_source.encode("utf-8")))

		temp_listing = []
		for listing in listings_on_page:
			print(listing)
			temp_listing = [listing[:-1]]
			listings_url.append(temp_listing)
		foreclosure_on_page = []
		foreclosure_on_page = set(re.findall(r'/(?:foreclosure)/.*?"',driver.page_source.encode("utf-8")))
		temp_foreclosure = []
		for foreclosure in foreclosure_on_page: 
			#print(foreclosure)
			temp_foreclosure = [foreclosure[:-1]]
			foreclosure_url.append(temp_foreclosure)
		try:
			print('------------------------------')
			print('Page Number: ' + str(page))
			print('Valid Properties on Page: ' + str(len(listings_on_page)))
			print('Foreclosures on Page: ' + str(len(foreclosure_on_page)))
			print('------------------------------')
			print('Properties: ' + str(len(listings_url)))
			print('Foreclosures: ' + str(len(foreclosure_url)))
			print('Total: ' + str(len(listings_url) + len(foreclosure_url)))
			if house_type != "sold":
				if next_page_handle == 0:
					break
			page += 1
			if house_type != "sold":
				next_page_handle.click()
			else:
				sleep(2)
				driver.get(url + str(page) + "_p/")
				if page == 167:
					return listings_url, foreclosure_url
			
		except NoSuchElementException:
			print('cannot go to next page')
			break
	return listings_url, foreclosure_url



def firefox_start(URL,EXPECTED_TITLE,city):
	while True: 
		stop = 0
		driver = webdriver.Firefox()
		#driver = webdriver.Firefox(executable_path=r'I:\\geckodriver.exe')
		try:
			driver.get(URL)
			print(driver.title)
		except WebDriverException:
			print("WEBPAGE CANNOT BE LOADED. RESTARTING...")
			driver.quit()
			stop = 1
		if stop is 0:
			if driver.title == EXPECTED_TITLE:
				try: 
					print(driver.title)
					if driver.title == EXPECTED_TITLE:
						city_input_cond = EC.presence_of_element_located((By.ID,'searchbox_form_location'))
						city_input_handle = wait_and_get(driver, city_input_cond, 10)
						if city_input_handle == 0:
							del city_input_cond
							city_input_cond = EC.presence_of_element_located((By.ID,'searchBox'))
							city_input_handle = wait_and_get(driver, city_input_cond, 10)
						city_input_handle.send_keys(city)
						sleep(5)
						city_input_handle.send_keys(Keys.ENTER)
						sleep(5)
						return driver
					else:
						return driver
				except NoSuchElementException: 
					print("WEBPAGE INCORRECTLY LOADED. RESTARTING...")
					driver.quit()
			else:
				driver.quit()

parameter_file_name = sys.argv[1]

line_num = 1
while True:
	file_line = linecache.getline(parameter_file_name, line_num)
	if file_line is '':
		break
	else:
		file_line = re.sub('\n','',file_line)
		print(file_line)
		parameters = file_line.split("\\")

		city = parameters[0]
		url_csv = parameters[1]
		house_type = parameters[2]

		URL = 'https://www.trulia.com/'
		EXPECTED_TITLE = 'Trulia: Real Estate Listings, Homes For Sale, Housing Data'

		#display = Display(visible=0, size=(800, 600))
		#display.start()
		driver = firefox_start(URL, EXPECTED_TITLE,city)

		listings_urls, foreclosure_url = get_urls(driver, house_type)

		num_listings = []
		num_listings.append(len(listings_urls))
		print("Number of valid listings: " + str(num_listings[0]))
		num_listings.append(len(foreclosure_url))
		print("Number of foreclosure listings: " + str(num_listings[1]))
		with open(url_csv, 'wb') as myfile:
			wr = csv.writer(myfile)	
			for url in listings_urls:
				wr.writerow(url)
			wr.writerow(num_listings)
		#listings_urls = ['/property/5031920104-46-Glenmoor-Dr-New-Haven-CT-06512"', '/property/1044373133-16-Townsend-Ave-New-Haven-CT-06512"']
		#crawl_pages(driver,listings_urls)
		driver.close()
		#display.stop()
	line_num += 1