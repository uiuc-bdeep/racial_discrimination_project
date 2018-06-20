import pandas as pd
import os
import datetime, pytz

def inquiryParse(d):
	tmp = d.split('/')
	tmp2 = tmp[2].split(' ')
	tmp3 = tmp2[1].split(':')
	month, day, year, hour, minute = int(tmp[0]), int(tmp[1]), int('20' + tmp2[0]), int(tmp3[0]), int(tmp3[1])
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

def find(A, x):
	for i in range(len(A)):
		if A[i] == x:
			return abs((((len(A) - 1) - i) % len(A)) + 1)
	return -1

if __name__ == '__main__':
	print("")

	inquiry_dict = {}

	# get addresses
	df = pd.read_csv('Atlanta_trulia_tract_6_7_18_round_3.csv')
	#df = df.loc[(df['Bedroom_max'] == '3') & (df['Bathroom_max'] == 2.0)]
	df = df.drop_duplicates(subset = 'Address')
	df = df.reset_index(drop=True)
	df.to_csv('Trulia.csv', index=False)

	print("Trulia.csv has been written. \n")

	# create individual address timestamp files
	df = pd.read_csv('atlanta_ga_metro_6_11_18_round_3_timestamp_fin.csv')
	num_inquiries = int(df.columns.tolist()[-1].split(" ")[-1])
	df['people_name_selection/person_name'] = df['first name'] + ' ' + df['last name']
	for i in range(1, num_inquiries + 1):
		cols = ['person id', 'people_name_selection/person_name', 'gender', 'racial category',
			'education level', 'address ' + str(i), 'timestamp ' + str(i), 'inquiry order ' + str(i)]
		tempDF = df[cols]
		tempDF = tempDF.loc[tempDF['address ' + str(i)] != 'NA']
		tempDF = tempDF.reset_index(drop=True)
		if len(tempDF) != 0:
			tempDF['address ' + str(i)] = tempDF['address ' + str(i)].str.split(',', expand=True)[0].str.split('(', expand=True)[1]
			for j in range(len(tempDF)):
				inquiry_dict[(tempDF['people_name_selection/person_name'][j], tempDF['address ' + str(i)][j], tempDF['timestamp ' + str(i)][j])] = tempDF['inquiry order ' + str(i)][j]
			tempDF.to_csv('individual timestamp files/timestamp' + str(i) + '.csv',
				columns=['person id', 'people_name_selection/person_name', 'gender', 'racial category',
					'education level', 'address ' + str(i), 'timestamp ' + str(i)],
				header=['person id', 'people_name_selection/person_name', 'gender', 'racial category',
					'education level', 'address_selection/property', 'timestamp inquiry sent out'],
				index=False)
			print("timestamp" + str(i) + ".csv has been written.")

	print("")

	# join addresses file with each individual timestamp file
	files = os.listdir('individual timestamp files')
	df = pd.read_csv('Trulia.csv')
	for file in files:
		if file != ".DS_Store":
			df2 = pd.read_csv('individual timestamp files/' + file)
			df2 = pd.merge(df, df2,
				left_on=['Address'],
				right_on=['address_selection/property'],
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
			df = pd.read_csv('individual joins/' + file)
			flag = False
		else:
			df = df.append(pd.read_csv("individual joins/" + file), ignore_index=True)
	
	print("Trulia.csv merged with all timestamp files. \n")

	# MIGHT NEED TO FIX THIS (depends on headers)
	# merge file with combined responses
	df = pd.merge(df, pd.read_csv('responses_concatenated.csv'),
			left_on=['people_name_selection/person_name', 'address_selection/property'],
			right_on=['people_name_selection/person_name', 'address_selection/property'],
			how='left')
	print("Trulia.csv merged with all timestamp files merged with all responses. \n")

	# create new column for timedelta and "response"
	diffs = []
	resp = []
	for i in range(len(df)):
		if len(str(df['timestamp inquiry sent out'][i])) > 5 and len(str(df['dateTime_selection/timestamp'][i])) > 5:
			diffs.append(responseParse(str(df['dateTime_selection/timestamp'][i])) - inquiryParse(str(df['timestamp inquiry sent out'][i])))
			diffs[-1] = (diffs[-1].days*24*60) + (diffs[-1].seconds/60.0)
			resp.append(1)
		else:
			diffs.append("")
			resp.append(0)
	df['timeDiff'] = pd.Series(diffs)
	df['response'] = pd.Series(resp)
	
	print("'timeDiff' and 'response' columns have been made. \n")

	#df = df.drop_duplicates()
	
	D = {}
	for i in range(len(df)):
		if df['response'][i] == 1:
			if not (df['people_name_selection/person_name'][i], df['Address'][i]) in D:
				D[(df['people_name_selection/person_name'][i], df['Address'][i])] = [responseParse(df['dateTime_selection/timestamp'][i])]
			else:
				D[(df['people_name_selection/person_name'][i], df['Address'][i])].append(responseParse(df['dateTime_selection/timestamp'][i]))

	for key in D:
		D[key].sort()
		D[key].reverse()

	order = []
	totalResponses = []
	inquiryOrder = []
	for i in range(len(df)):
		if df['response'][i] == 1:
			order.append(find(D[(df['people_name_selection/person_name'][i], df['Address'][i])], responseParse(df['dateTime_selection/timestamp'][i])))
			totalResponses.append(len(D[(df['people_name_selection/person_name'][i], df['Address'][i])]))
			inquiryOrder.append(inquiry_dict[(df['people_name_selection/person_name'][i], df['Address'][i], df['timestamp inquiry sent out'][i])])
		else:
			order.append('n/a')
			totalResponses.append(0)
			inquiryOrder.append('n/a')

	df['response order'] = pd.Series(order)
	df['total responses'] = pd.Series(totalResponses)
	df['inquiry order'] = pd.Series(inquiryOrder)
	
	print("'response order', 'total responses', and 'inquiry order' columns have been made. \n")

	# reorder columns
	cols = df.columns.tolist()
	cols = [cols[83]] + [cols[82]] + [cols[114]] + [cols[96]] + [cols[85]] + [cols[113]] + [cols[3]] + cols[115:] + [cols[15]] + [cols[62]] + [cols[78]] + cols[:3] + cols[4:15] + cols[16:62] + cols[63:78] + cols[80:82] + [cols[84]] + cols[86:96] + cols[97:113]
	df = df[cols]
	
	df.to_csv('GA_Trulia_MERGED_allTimestamps_MERGED_allResponses.csv', index=False)
	print('GA_Trulia_MERGED_allTimestamps_MERGED_allResponses.csv has been written. \n')
