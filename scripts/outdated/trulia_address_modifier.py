import re
body = 'Thank you for your interest in the property at 802 S Duncan. I would be happy to set up a viewing for you. Please give us a call at 217-607-1645 to set this up. '
subject = 'New Inquiry for 802 S Duncan Road'

# def check_alt_add(address_string):
# 	ret_string = address_string
# 	if 'st' in address_string
# 		ret_string_1 = ret_string.replace('st', 'street')
# 		ret_string_2 = ret_string.replace('st', '')
# 	if else 'ct' in address_string: 
# 	 	ret_string_1 = ret_string.replace('st', 'street')
# 		ret_string_2 = ret_string.replace('st', '')
# 	if else 'av' in address_string: 
# 		ret_strin
# 	else: 
# 		return 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
# 	return ret_string

# print(check_alt_add(('501 W Green St #3').lower())


address_string = '802 S Duncan Rd'
print(address_string)
possible_address_string = re.match(r'^[0-9]* ([a-z]*)', subject)
if possible_address_string == None: 
	print(possible_address_string.group(0))
	possible_address_string = re.match(r'^[0-9]* ([a-z]*)', body)
	if possible_address_string != None: 
		print(possible_address_string.group(0))

# alt_address = check_alt_add(address_string)
# address_list = [address_string, alt_address]
# if (address_string in body.lower()) or (address_string in subject.lower()) or (alt_address in body.lower()) or (alt_address in subject.lower()):
# #if address_list in body.lower() or address_list in subject.lower():  # check to see if the email has a street number in it
# 	date_tuple = email.utils.parsedate_tz(msg['Date']) # if it does then get the time
# 	local_date = str(datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple)).strftime('%Y-%m-%d %H:%M:%S'))
# 	print('FOUND A MATCH!')
# 	address_dict[key].append(local_date)
# 	mov = M.store(num, '+FLAGS', r'(\Deleted)')
# 	M.expunge()
# 	print('Email Stored in Starred')