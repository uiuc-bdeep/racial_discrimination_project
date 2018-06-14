import email
from email import policy
from email.parser import BytesParser
from bs4 import BeautifulSoup
import os
import re
import pandas as pd
from datetime import datetime

NEWLINE = ' '
DELIMETER = ','  # Will be used to delimit URLs, could be broken with URLs that contain this character
MISSING_VALUE=''
FILE_SEP='/'

PROJ_ROOT = os.environ.get('PROJ_ROOT')+FILE_SEP

TRIAL_NAME = 'losangeles'
DATA_DIR = PROJ_ROOT+'data/losangeles_data/emails/'

print("Found the following folders in the data directory")
print(os.listdir(DATA_DIR))

NAMES_MARKET_CSV = PROJ_ROOT+'project_files/names_market.csv'
names_market = pd.read_csv(NAMES_MARKET_CSV)

ACCOUNT_LIST = names_market['email'].values
print("Account list: ")
print(ACCOUNT_LIST)

# Text Content Regex
phone_number_re = re.compile('\(?([0-9]{3})\)?([ .-]?)([0-9]{3})\2([0-9]{4})')
google_maps_re = re.compile('https:\/\/maps.google.com\/\?q=((\w|\d|\.|\,)+\+)+((\w|\d|\.|\,)+)')
trulia_listing_re = re.compile('www\.trulia\.com/rental/\d*')

# Simple string match to separate email from the rest of the thread
truncate_text_re = re.compile('From:')

def set_to_delimited_string(feature_set):
    ret_string = ''
    if feature_set:
        ret_string = DELIMETER.join([feature for feature in feature_set])
    return ret_string

def extract_hyperlinks(soup):
    link_list = []
    all_a = soup.findAll("a")

    for link in all_a:
        if 'href' in link.attrs:
            if link.attrs['href'] != '#':   # Filter out empty '#' links
                link_list.append(link.attrs['href'])

    return link_list

def extract_regex(set_of_strings, compiled_regex):
    match_set = set()

    for link in set_of_strings:
        m = compiled_regex.search(link)
        if (m!=None): # if there is a regex match
            match_set.add(m.group(0)) # add the match to the match_set

    return match_set

def truncate_series(text_series, truncate_text_re=truncate_text_re):
    """
    Input: pd.Series containing Bytes (representing text)
    Output: pd.Series containing Strings truncated at truncate_text_re
    """
    return_series = text_series.copy()
    matches = return_series.apply(lambda x: re.search(truncate_text_re,x))   # Search for truncate pattern
    truncate_position = matches.dropna().apply(lambda x:x.start())  # Get position of truncate pattern.  Not all series will find truncate position
    for idx,text in truncate_position.iteritems():  # Only iterate through found truncate positions
        return_series.loc[idx]= text_series[idx][:truncate_position[idx]]  # Truncate text

    return return_series

def bytes_to_string(email_text_series):
    """
    Input: pd.Series containing Bytes and Strings
    Output: pd.Series containing Strings
    """
    # Separate text that has decoded into Bytes
    byte_idx = email_text_series.apply(type)==bytes
    str_idx = ~byte_idx

    # Handle Bytes differently than Strings, vast majority will be 'utf-8'
    text_series = email_text_series.loc[byte_idx].apply(lambda x:x.decode('utf-8',errors='ignore'))
    # Truncate Bytes at position found by truncate_text_re
    truncated_series = truncate_series(text_series)

    # Replace original text with truncated text versions
    email_text_series.loc[truncated_series.index]=truncated_series.values

    return pd.Series(email_text_series)

def make_soup(msg):
    """
    Input: msg, email.message.EmailMessage
    Output: dict, {string feature_name: list feature_observation}
    """
    email_json={}
    email_json = {feature:'' for feature in ['subject','from','trulia','gmaps','tel','mailto','text']}
    email_json['from'] = msg['From']
    email_json['subject'] = msg['Subject']
    email_json['date'] = datetime.strptime(msg['Date'], "%a, %d %b %Y %H:%M:%S %z")
    email_json['message-id'] = msg['Message-ID']

    for part in msg.walk():
        if part.get_content_type()=='text/plain':
            if email_json['text']=='':  # If previous msg.part contained text, do not overwrite it
                email_json['text']= part.get_payload(decode=True)
        elif part.get_content_type()=='text/html':
            html_body_text = msg.get_body(preferencelist=('html')).get_content()
            soup = BeautifulSoup(html_body_text, 'lxml')#'html.parser')

            links = set(extract_hyperlinks(soup))
            email_json['all_links'] = set_to_delimited_string(links)
            email_json['all_trulia'] = set_to_delimited_string([link for link in links if re.search('trulia',link)])

            email_json['trulia'] = set_to_delimited_string(extract_regex(links,trulia_listing_re))
            email_json['gmaps'] = set_to_delimited_string(extract_regex(links, google_maps_re))
            email_json['tel'] = set_to_delimited_string([link.split(':')[1] for link in links if link.startswith('tel')])
            email_json['mailto'] = set_to_delimited_string([link.split(':')[1] for link in links if link.startswith('mailto')])

            if email_json['text']=='':  # If previous msg.part contained text, do not overwrite it
                str_builder = ''
                if soup.body:
                    for string in soup.body.stripped_strings:
                        str_builder+=string + NEWLINE  # Delimiting sentences will assist with semantic inferences
                else:
                    for string in soup.stripped_strings:
                        str_builder+=string + NEWLINE  # Delimiting sentences will assist with semantic inferences
                email_json['text'] = str_builder

        else:
            continue

    return email_json


def parse_all(response_type):
    email_summary_cols = ['trulia', 'gmaps', 'tel', 'mailto', 'text']
    all_emails = pd.DataFrame(columns=email_summary_cols)

    email_folder_dir = DATA_DIR+response_type
    email_json_dict = {}  # email_json_dict[E-mail number]=email_json
    for email in os.listdir(email_folder_dir):
        with open(email_folder_dir+FILE_SEP+email, 'rb') as open_email:
            msg = BytesParser(policy=policy.default).parse(open_email)
            email_json_dict[email] = make_soup(msg)

    return_df = pd.DataFrame(email_json_dict).T

    return_df['email']=return_df.index.values
    return_df['account']=return_df['email'].apply(lambda x:x.split('.')[0]) #split off account name
    return_df['email']=response_type+'/'+return_df['email'] #then prepend 'response-type/' to email_name.eml

    return return_df


# Parse Responses
responses = parse_all('LA-Response')
responses['response']=1

# Parse Nonresponses
nonresponses = parse_all('LA-Nonresponse')
nonresponses['response']=0

# Merge into all_emails
all_emails = pd.concat([responses,nonresponses], ignore_index=True)
all_emails.reset_index(inplace=True)


# Add racial group
ethn_white =  ['calebpeterson0522', 'rmiller5099', 'amurphy7116', 'ecox3471', 'woodleslie542','charliemyers274']
ethn_black = ['jalenj166', 'dqronison1445', 'niaharris56', 'ebonyjames776', 'shanicethomas086','lamarw1668']
ethn_hispanic = ['rodgriguezjorge45', 'luistorres2866', 'isabellalopez6576', 'moralesmariana9054', 'jramirez7561','psanchez7045']
all_emails['race']='African American'
for account in ethn_hispanic:
    all_emails.loc[all_emails['account']==account,'race']='Hispanic'
for account in ethn_white:
    all_emails.loc[all_emails['account']==account,'race']='White'

# Indicate if there is a trulia indexer present
all_emails['trulia_bool']=0
all_emails.loc[all_emails['trulia']!='','trulia_bool']=1

# Filter False Positives: Email nonresponses that have a Trulia indexer
all_emails.loc[all_emails['from']=='Trulia <updates@comet.trulia.com>','trulia_bool']=0
all_emails.loc[all_emails['from']=='Trulia <no-reply@update.trulia.com>','trulia_bool']=0

# Create the Confusion Matrix
responses = all_emails[all_emails['response']==1]
nonresponses = all_emails[all_emails['response']==0]

FP = nonresponses[nonresponses['trulia_bool']==1]
TN = nonresponses[nonresponses['trulia_bool']==0]

TP = responses[responses['trulia_bool']==1]
FN = responses[responses['trulia_bool']==0]

print("{} nonresponses".format(str(len(nonresponses))))
print("{} responses".format(str(len(responses))))
print("{} emails total".format(str(len(all_emails))))
print("Recall: {0:.2f} % of responses can be indexed by the Trulia URL".format(len(TP)/(len(TP)+len(FN))*100))
print("Precision: {0:.2f} % of emails that contain a Trulia URL are responses".format(len(TP)/(len(TP)+len(FP))*100))


# Clean up text selections by detecting base64 Content Encodings and truncating text sections
all_emails.loc[:,'text'] = bytes_to_string(all_emails['text'])

# Treat Special Cases:
#  1) Where parser includes CSS style code in 'text' sections
selection_list = all_emails[all_emails['text'].str.startswith('@')]['email'].values
def get_text_alt(email):
    with open(DATA_DIR+email, 'rb') as open_email:
        msg = BytesParser(policy=policy.default).parse(open_email)

    html_body_text = msg.get_body(preferencelist=('html')).get_content()
    soup = BeautifulSoup(html_body_text, 'lxml')#'html.parser')

    all_p = soup.findAll('p')

    str_builder = ''
    for p in all_p:
        for string in p.stripped_strings:
            str_builder+=string+NEWLINE
    return str_builder
text_replacement_dict = {}
for email in selection_list:
    text_replacement_dict[email]=get_text_alt(email)

# Replace text selections with custom parser
for email in text_replacement_dict.keys():
    all_emails.loc[all_emails['email']==email,'text'] = text_replacement_dict[email]


# Write
selected_columns = ['email','date','subject','text','response','trulia_bool']
all_emails[selected_columns].to_csv('LA-Trial_parsed_emails.csv', index=None)
