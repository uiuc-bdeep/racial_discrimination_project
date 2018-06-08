import sys
import os
import imaplib
import getpass
import pandas as pd
import json

IMAP_SERVER = 'imap.gmail.com'
EMAIL_FOLDERS = ['INBOX','LA-Response','LA-Nonresponse']
EMAIL_DOMAIN ='@gmail.com'
PASSWORD = 'BdeepTrulia'

PROJ_ROOT = os.environ['PROJ_ROOT']

with open(PROJ_ROOT + 'parameters.json') as parameter_json:
    parameters = json.load(parameter_json)

PROJ_ROOT = parameters['PROJ_ROOT']
TRIAL_DATA = parameters['TRIAL_DATA']
NAMES_FILE = PROJ_ROOT +'project_files/names_market.csv'
DATA_DIR = TRIAL_DATA+'emails/'

names = pd.read_csv(NAMES_FILE)
ACCOUNT_LIST = names['email'].values
print (ACCOUNT_LIST)

EMAIL_FOLDERS=['INBOX','AT-Response','AT-Nonresponse']
ACCOUNT_LIST = ['jramirez7561','woodleslie542','shanicethomas086']

def process_mailbox(M, account_prefix, folder):
    """
    Dump all emails in folder to files in output directory labeled
        <account>.<sequence_number>.eml
    """

    rv, data = M.search(None, "ALL")
    if rv != 'OK':
        print ("No messages found!")
        return

    for num in data[0].split():
        rv, data = M.fetch(num, '(RFC822)')
        if rv != 'OK':
            print ("ERROR getting message", num)
            return
        print ("Writing message ", num)
        print(account_prefix+'.'+num)
        f = open('%s/%s.eml' %(os.getcwd(), account_prefix+'.'+num), 'wb')
        f.write(data[0][1])
        f.close()

def main():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    for folder in EMAIL_FOLDERS:
        if folder in os.listdir(DATA_DIR):
            print("Found "+folder+" in data directory")
        else:
            print("Making folder " + folder)
            os.mkdir(DATA_DIR+folder)

    data_home = DATA_DIR
    os.chdir(data_home)
    print(os.getcwd())

    for account in ACCOUNT_LIST:
        print(account)
        email_account = account + EMAIL_DOMAIN

        M = imaplib.IMAP4_SSL(IMAP_SERVER)
        M.login(email_account, PASSWORD)

        for folder in EMAIL_FOLDERS:
            os.chdir(data_home+folder)
            print(os.getcwd())
            print("Processing mailbox: ", folder)
            rv, data = M.select(folder)
            if rv == 'OK':
                process_mailbox(M,account,folder)
                M.close()
            else:
                print ("ERROR: Unable to open mailbox ", rv)
        M.logout()

if __name__ == "__main__":
    main()
