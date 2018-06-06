import os
import sys 
import pandas as pd 
import numpy as np 
import datetime

def add_state_df(df,col = ['state']): 
	df_temp  = pd.DataFrame(columns = ['state','last_run'])
	df       = pd.concat([df, df_temp],axis = 1)
	df['state']    = "white,hispanic,black"
	df['last_run'] = datetime.datetime.strptime('2019-10-10 10:10:10','%Y-%m-%d %H:%M:%S')
	print(datetime.datetime.strptime('2019-10-10 10:10:10','%Y-%m-%d %H:%M:%S'))

	return df

def clean_df(df, col): 
	df.dropna(subset = col)
	df = df.drop_duplicates(subset = col)
	return df

def main(): 
	crawled_data = str(sys.argv[1])
	queue_data  = str(sys.argv[2])

	if os.path.isfile(crawled_data) == False: 
		print('Nothing crawled')
		exit()
	else:
		df_crawled = pd.read_csv(crawled_data)

	if os.path.isfile(queue_data) == False: 
		print('No queue_data...\n INITIALIZING...')
		df_queue = add_state_df(df_crawled)
		df_queue = clean_df(df_queue, ['Address'])

	else: 
		df_queue = pd.read_csv(queue_data)
		df_diff  = df_crawled[~df_crawled['Address'].isin(df_queue['Address'].values)]

		if df_diff.empty: 
			print('No New Data...\nExiting...')
			exit()
		print('New Data FOUND!')
		df_diff  = add_state_df(df_diff)
		df_queue = pd.concat([df_queue, df_diff])
		df_queue = clean_df(df_queue, ['Address'])

	df_queue.to_csv(queue_data,mode= 'w', index = False)

main()
print('All Done')






