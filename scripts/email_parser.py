import email
from email import policy
from email.parser import BytesParser
from bs4 import BeautifulSoup
import os
import re
import pandas as pd

NEWLINE = '\n'

PROJ_ROOT = '/path/to/racial_discrimination_project/'

NAMES_MARKET_CSV = PROJ_ROOT+'project_files/names_market.csv'
CITY_RENTALS_CSV = PROJ_ROOT+'champaign_pretest_1/champaign_rentals.csv'
MERGE_SHEET_CSV = PROJ_ROOT+'champaign_pretest_1/champaign_merge_sheet.csv'
EMAIL_DIR = PROJ_ROOT+'scripts/emails/'


names_market = pd.read_csv(NAMES_MARKET_CSV)
champaign_rentals = pd.read_csv(CITY_RENTALS_CSV)
merge_sheet = pd.read_csv(MERGE_SHEET_CSV)

ACCOUNT_LIST = [account+"/" for account in names_market['email'].values]

phone_number_re = re.compile('\(?([0-9]{3})\)?([ .-]?)([0-9]{3})\2([0-9]{4})')
google_maps_re = re.compile('https:\/\/maps.google.com\/\?q=((\w|\d|\.|\,)+\+)+((\w|\d|\.|\,)+)')
trulia_listing_re = re.compile('www.trulia.com/rental/\d*')
trulia_listing_re2 = re.compile('www\.trulia\.com\/rental\/\d+((\w|\d|\.|\,)+-)+((\w|\d|\.|\,)+)')

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
        if (m!=None):
            match_set.add(m.group(0))

    return match_set

def make_soup(msg):
    """
    Input: msg, email.message.EmailMessage
    Output: dict, {string feature_name: list feature_observation}
    """
    email_json = {}

    html_body_text = msg.get_body(preferencelist=('html','plain')).get_content()
    soup = BeautifulSoup(html_body_text, 'html.parser')

    links = set(extract_hyperlinks(soup))

    email_json['trulia'] = extract_regex(links,trulia_listing_re)
    email_json['gmaps'] = extract_regex(links, google_maps_re)
    email_json['tel'] = [link.split(':')[1] for link in links if link.startswith('tel')]
    email_json['mailto'] = [link.split(':')[1] for link in links if link.startswith('mailto')]

#     email_json['text'] = extract_text(soup)
    email_json['text']=extract_text_test(soup)

    return email_json

def extract_text(soup):
    str_builder = ''
    for p in soup.find_all('p'):
        str_builder += p.get_text(separator = NEWLINE)

    return str_builder

def extract_text_test(soup):
    str_builder = ''

#     print("===Trying: \t 'p', {'class':'MsoNormal'}")
    MsoNormal = soup.findAll('p', {'class':'MsoNormal'})
    for tag in MsoNormal:
        str_builder+=tag.get_text()

    if not MsoNormal:
#         print('No MsoNormal found')
#         print("===Trying: \t 'p'")
        all_p  = soup.findAll('p')
        for tag in all_p:
            str_builder+=tag.get_text()
    else:
#         print('No all_p found')
#         print("===Trying: \t 'div',{'dir':['ltr','rtl','auto']}")
        div_dir = soup.findAll('div',{'dir':['ltr','rtl','auto']})
        for tag in div_dir:
            str_builder+=tag.get_text()
        if not div_dir:
            print('=========================== No Text Found')
    return str_builder

def count_extracted_fields(account_name):
    email_names = [account_name+'.'+email for email in email_json_dict.keys()]

    email_summary = pd.DataFrame(0,index=email_names, columns=email_json_dict['1.eml'].keys())

    for email in email_json_dict:
        email_name = account_name+'.'+email
        for key in email_json_dict[email]:
            if email_json_dict[email][key]:
                if (key=='text'):
#                     email_summary.loc[email][key]=1
                    email_summary.loc[email_name][key]=1
                else:
#                     email_summary.loc[email][key]=len(email_json_dict[email][key])
                    email_summary.loc[email_name][key]=len(email_json_dict[email][key])

all_emails = pd.DataFrame(columns=email_summary_cols.values)
ad_phone_numbers = champaign_rentals['Phone_Number'].values
addresses_inquiries_sent_to = champaign_rentals['Address'].values

for account in ACCOUNT_LIST:
    print("ACCOUNT: " + account)
    email_inbox = EMAIL_DIR+account
    email_json_dict = {} # email_json_dict[E-mail number]=email_json
    for email in os.listdir(email_inbox):
        with open(email_inbox+email, 'rb') as open_email:
            msg = BytesParser(policy=policy.default).parse(open_email)
            print('****** '+email)
            email_json_dict[email] = make_soup(msg)
    email_summary = count_extracted_fields(account[:-1]) # Remove last '/' from string
    all_emails = pd.concat([all_emails,email_summary])
    print(email_summary)
