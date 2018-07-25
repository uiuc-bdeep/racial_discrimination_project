import pandas as pd
import os
import datetime, pytz

TRULIA_ADDRESSES_FILE = 'atlanta_ga_7_10_18_round_2_6_census.csv'
TIMESTAMP_FILE = 'atlanta_ga_metro_7_2_18_round_6_timestamp_fin.csv'

def inquiryParse(d):
	tmp = d.split('/')
	tmp2 = tmp[2].split(' ')
	tmp3 = tmp2[1].split(':')
	month, day, year, hour, minute = int(tmp[0]), int(tmp[1]), int('20' + tmp2[0]), int(tmp3[0]), int(tmp3[1])
	if len(str(year)) != 4:
		year = int(str(year)[2:])
	return pytz.timezone('America/Chicago').localize(datetime.datetime(year, month, day, hour, minute))

def responseParse(d):
	tz = d.split('-')[-1]
	year, month, day, hour, minute = int(d[0:4]), int(d[5:7]), int(d[8:10]), int(d[11:13]), int(d[14:16])
	if tz == '07:00': # (PST)
		return pytz.timezone('America/Los_Angeles').localize(datetime.datetime(year, month, day, hour, minute))
	elif tz == '04:00': # (EST)
		return pytz.timezone('America/New_York').localize(datetime.datetime(year, month, day, hour, minute))
	else: # tz == '05:00' (CST)
		return pytz.timezone('America/Chicago').localize(datetime.datetime(year, month, day, hour, minute))

def time_of_day(d, type_):
	curr_date = inquiryParse(d) if type_ == "inquiry" else responseParse(d)
	curr_minutes = curr_date.hour*60 + curr_date.minute
	if curr_minutes <= 119: 	# 00-01:59
		return "00-02"
	elif curr_minutes <= 239: 	# 02-03:59
		return "02-04"
	elif curr_minutes <= 359: 	# 04-05:59
		return "04-06"
	elif curr_minutes <= 479: 	# 06-07:59
		return "06-08"
	elif curr_minutes <= 599: 	# 08-09:59
		return "08-10"
	elif curr_minutes <= 719: 	# 10-11:59
		return "10-12"
	elif curr_minutes <= 839: 	# 12-13:59
		return "12-14"
	elif curr_minutes <= 959: 	# 14-15:59
		return "14-16"
	elif curr_minutes <= 1079: 	# 16-17:59
		return "16-18"
	elif curr_minutes <= 1199: 	# 18-19:59
		return "18-20"
	elif curr_minutes <= 1319: 	# 20-21:59
		return "20-22"
	else: 						# 22-23:59
		return "22-24"

def find(A, x):
	for i in range(len(A)):
		if A[i] == x:
			return abs((((len(A) - 1) - i) % len(A)) + 1)
	return -1

def timestampSubParse(d):
	temp = inquiryParse(d) - datetime.timedelta(hours=5)
	if temp.minute < 10:
		return "{}/{}/{} {}:0{}".format(temp.month, temp.day, temp.year, temp.hour, temp.minute)
	else:
		return "{}/{}/{} {}:{}".format(temp.month, temp.day, temp.year, temp.hour, temp.minute)

def getWeekday(date):
	return {
		0: 'Monday',
		1: 'Tuesday',
		2: 'Wednesday',
		3: 'Thursday',
		4: 'Friday',
		5: 'Saturday',
		6: 'Sunday'
	}[date.weekday()]

if __name__ == '__main__':
	print("")

	inquiry_dict = {}

	# get addresses
	df_trulia = pd.read_csv(os.getcwd() + '/input/' + TRULIA_ADDRESSES_FILE)
	df_trulia = df_trulia.drop_duplicates(subset = 'Address')
	df_trulia = df_trulia.reset_index(drop=True)
	
	print("Acquired Trulia addresses. \n")

	# create individual address timestamp files
	df = pd.read_csv(os.getcwd() + '/input/' + TIMESTAMP_FILE)
	num_inquiries = int(df.columns.tolist()[-1].split(" ")[-1])
	df['person_name'] = df['first name'] + ' ' + df['last name']
	for i in range(1, num_inquiries + 1):
		cols = ['person id', 'person_name', 'gender', 'racial category',
			'education level', 'address ' + str(i), 'timestamp ' + str(i), 'inquiry order ' + str(i)]
		tempDF = df[cols]
		tempDF = tempDF.loc[tempDF['address ' + str(i)] != 'NA']
		tempDF = tempDF.reset_index(drop=True)
		if len(tempDF) != 0:
			tempDF['address ' + str(i)] = tempDF['address ' + str(i)].str.split(',', expand=True)[0].str.split('(', expand=True)[1]
			for j in range(len(tempDF)):
				inquiry_dict[(tempDF['person_name'][j], tempDF['address ' + str(i)][j])] = tempDF['inquiry order ' + str(i)][j]
			tempDF.to_csv('individual timestamp files/timestamp' + str(i) + '.csv',
				columns=['person id', 'person_name', 'gender', 'racial category',
					'education level', 'address ' + str(i), 'timestamp ' + str(i)],
				header=['person id', 'person_name', 'gender', 'racial category',
					'education level', 'inquiry_address', 'timestamp inquiry sent out'],
				index=False)
			print("timestamp" + str(i) + ".csv has been written.")

	print("")

	# join trulia addresses file with each individual timestamp file
	files = os.listdir('individual timestamp files')
	for file in files:
		if file != ".DS_Store":
			df2 = pd.read_csv(os.getcwd() + '/individual timestamp files/' + file)
			df2 = pd.merge(df_trulia, df2,
				left_on=['Address'],
				right_on=['inquiry_address'],
				how='right')
			df2 = df2.sort_values('person id')
			df2.to_csv('individual joins/Trulia_MERGED_' + file, index=False)
			print("Trulia_MERGED_" + file + " has been written.")

	print("")

	# combine individual joined files
	files = os.listdir('individual joins')
	df = None
	flag = True
	for file in files:
		if flag:
			df = pd.read_csv(os.getcwd() + '/individual joins/' + file)
			flag = False
		else:
			df = df.append(pd.read_csv(os.getcwd() + "/individual joins/" + file), ignore_index=True)
	
	print("Trulia addresses merged with all timestamp files. \n")

	# merge file with combined responses
	df = pd.merge(df, pd.read_csv(os.getcwd() + '/input/responses_concatenated.csv'),
			left_on=['person_name', 'inquiry_address'],
			right_on=['people_name_selection/person_name', 'address_selection/property'],
			how='left')
	print("Trulia addresses merged with all timestamp files merged with all responses. \n")

	# create new column for "timeDiff" and "response"
	diffs = []
	resp = []
	for i in range(len(df)):
		# dateTime_selection/timestamp := timestamp of response received
		# timestamp inquiry sent out := timestamp of inquiry sent out
		if len(str(df['timestamp inquiry sent out'][i])) > 5 and len(str(df['dateTime_selection/timestamp'][i])) > 5:
			# decrease 'timestamp inquiry sent out' column by 5 hours
			df['timestamp inquiry sent out'][i] = timestampSubParse(str(df['timestamp inquiry sent out'][i]))
			# append to time diff column
			diffs.append(responseParse(str(df['dateTime_selection/timestamp'][i])) - inquiryParse(str(df['timestamp inquiry sent out'][i])))
			diffs[-1] = (diffs[-1].days*24*60) + (diffs[-1].seconds/60.0)
			resp.append(1)
		else:
			diffs.append("n/a")
			resp.append(0)
	df['timeDiff'] = pd.Series(diffs) # timeDiff is in minutes
	df['response'] = pd.Series(resp)
	
	print("'timeDiff' and 'response' columns have been made. \n")

	D = {}
	for i in range(len(df)):
		if df['response'][i] == 1:
			if not (df['person_name'][i], df['address_selection/property'][i]) in D:
				D[(df['person_name'][i], df['address_selection/property'][i])] = [responseParse(df['dateTime_selection/timestamp'][i])]
			else:
				D[(df['person_name'][i], df['address_selection/property'][i])].append(responseParse(df['dateTime_selection/timestamp'][i]))

	for key in D:
		D[key].sort()
		D[key].reverse()

	order = []
	totalResponses = []
	inquiryOrder = []
	inquiryWeekday = []
	responseWeekday = []
	income = []
	references = []
	credit = []
	employment = []
	coRenters = []
	family = []
	smoking = []
	pets = []
	criminal_history = []
	eviction_history = []
	rental_history = []
	government_housing_vouchers = []
	inquiry_time_of_day = []
	response_time_of_day = []
	for i in range(len(df)):
		# for matches
		if df['response'][i] == 1:
			order.append(find(D[(df['person_name'][i], df['address_selection/property'][i])], responseParse(df['dateTime_selection/timestamp'][i])))
			totalResponses.append(len(D[(df['person_name'][i], df['address_selection/property'][i])]))
			inquiryOrder.append(inquiry_dict[(df['person_name'][i], df['inquiry_address'][i])])
			inquiryWeekday.append(getWeekday(inquiryParse(str(df['timestamp inquiry sent out'][i]))))
			responseWeekday.append(getWeekday(responseParse(str(df['dateTime_selection/timestamp'][i]))))
			inquiry_time_of_day.append(time_of_day(str(df['timestamp inquiry sent out'][i]), "inquiry"))
			response_time_of_day.append(time_of_day(str(df['dateTime_selection/timestamp'][i]), "response"))

			if str(df['screening_selection/screening_terms'][i] != 'nan'):
				income.append(1) if 'Income' in df['screening_selection/screening_terms'][i] else income.append(0)
				references.append(1) if 'References' in df['screening_selection/screening_terms'][i] else references.append(0)
				credit.append(1) if 'Credit' in df['screening_selection/screening_terms'][i] else credit.append(0)
				employment.append(1) if 'Employment/Job' in df['screening_selection/screening_terms'][i] else employment.append(0)
				coRenters.append(1) if 'Co-renters/Roommates' in df['screening_selection/screening_terms'][i] else coRenters.append(0)
				family.append(1) if 'Family' in df['screening_selection/screening_terms'][i] else family.append(0)
				smoking.append(1) if 'Smoking' in df['screening_selection/screening_terms'][i] else smoking.append(0)
				pets.append(1) if 'Pets' in df['screening_selection/screening_terms'][i] else pets.append(0)
				criminal_history.append(1) if 'Criminal History' in df['screening_selection/screening_terms'][i] else criminal_history.append(0)
				eviction_history.append(1) if 'Eviction History' in df['screening_selection/screening_terms'][i] else eviction_history.append(0)
				rental_history.append(1) if 'Rental History' in df['screening_selection/screening_terms'][i] else rental_history.append(0)
				government_housing_vouchers.append(1) if 'Government Housing Vouchers' in df['screening_selection/screening_terms'][i] else government_housing_vouchers.append(0) 
		else:
			if len(str(df['timestamp inquiry sent out'][i])) > 5:
				inquiryOrder.append(inquiry_dict[(df['person_name'][i], df['inquiry_address'][i])])
				inquiryWeekday.append(getWeekday(inquiryParse(str(df['timestamp inquiry sent out'][i]))))
			else:
				inquiryOrder.append('n/a')
				inquiryWeekday.append('n/a')
			
			# for non-matches
			order.append('n/a')
			totalResponses.append(0)
			responseWeekday.append('n/a')
			income.append('n/a')
			references.append('n/a')
			credit.append('n/a')
			employment.append('n/a')
			coRenters.append('n/a')
			family.append('n/a')
			smoking.append('n/a')
			pets.append('n/a')
			criminal_history.append('n/a')
			eviction_history.append('n/a')
			rental_history.append('n/a')
			government_housing_vouchers.append('n/a')

	df['response_order'] = pd.Series(order)
	df['total_responses'] = pd.Series(totalResponses)
	df['inquiry_order'] = pd.Series(inquiryOrder)
	df['inquiry_weekday'] = pd.Series(inquiryWeekday)
	df['response_weekday'] = pd.Series(responseWeekday)
	
	print("'response_order', 'total_responses', 'inquiry_order', 'inquiry_weekday', and 'response_weekday' columns have been made. \n")

	# reorder columns
	cols = df.columns.tolist()
	cols = cols[79:85] + [cols[118]] + [cols[95]] + [cols[119]] + cols[113:115] + [cols[117]] + [cols[115]] + [cols[116]] + cols[1:79] + cols[85:95] + cols[96:109] + cols[110:113]
	df = df[cols]

	# add additional columns
	df['Income'] = pd.Series(income)
	df['References'] = pd.Series(references)
	df['Credit'] = pd.Series(credit)
	df['Employment/Job'] = pd.Series(employment)
	df['Co-renters/Roommates'] = pd.Series(coRenters)
	df['Family'] = pd.Series(family)
	df['Smoking'] = pd.Series(smoking)
	df['Pets'] = pd.Series(pets)
	df['criminal_history'] = pd.Series(criminal_history)
	df['eviction_history'] = pd.Series(eviction_history)
	df['rental_history'] = pd.Series(rental_history)
	df['government_housing_vouchers'] = pd.Series(government_housing_vouchers)

	print("'Income', 'References', 'Credit', 'Employment/Job', 'Co-renters/Roommates', 'Family', 'Smoking', 'Pets', 'Criminal History', 'Eviction History', 'Rental History', and 'Government Housing Vouchers' columns have been made. \n")

	df["response_time_of_day"] = pd.Series(response_time_of_day)
	df["inquiry_time_of_day"] = pd.Series(inquiry_time_of_day)

	print("'response_time_of_day' and 'inquiry_time_of_day' columns have been written. \n")

	# make sure all column names do not have spaces
	cols = df.columns.tolist()
	new_headers = [col.replace(" ", "_") for col in cols]

	df.to_csv(os.getcwd() + '/output/atlanta_ga_final.csv', 
		columns=cols,
		header=new_headers,
		index=False)
	print('atlanta_ga_final.csv has been written. \n')