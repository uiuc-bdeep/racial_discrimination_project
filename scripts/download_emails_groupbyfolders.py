import sys
import os
import imaplib
import getpass
import pandas as pd

IMAP_SERVER = 'imap.gmail.com'
#EMAIL_FOLDER = 'LA-Response'
EMAIL_FOLDERS = ['LA-Response','LA-Nonresponse']
EMAIL_DOMAIN ='@gmail.com'
PASSWORD = 'BdeepTrulia'

FILE_SEPARATOR = '/'
PROJ_ROOT = '/path/to/racial_discrimination_project/'
NAMES_FILE = 'project_files/names_market.csv'
TRIAL_NAME= 'losangeles'
DATA_DIR = '/path/to/data/'

names = pd.read_csv(PROJ_ROOT+NAMES_FILE)
# ACCOUNT_LIST = names['email'].values
## Can subset accounts here
ACCOUNT_LIST = ['jramirez7561']

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
            print "ERROR getting message", num
            return
        print "Writing message ", num
        print(account_prefix+'.'+num)
        f = open('%s/%s.eml' %(os.getcwd(), account_prefix+'.'+num), 'wb')
        f.write(data[0][1])
        f.close()

def main():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if TRIAL_NAME in os.listdir(DATA_DIR):
            print ("Found " + TRIAL_NAME + " in the data folder")
    else:
        print ("Making trial directory: " + TRIAL_NAME)
        os.mkdir(DATA_DIR+TRIAL_NAME)
    for folder in EMAIL_FOLDERS:
        if folder in os.listdir(DATA_DIR+TRIAL_NAME+FILE_SEPARATOR):
            print("Found "+folder+" in data directory")
        else:
            print("Making folder " + folder)
            os.mkdir(DATA_DIR+TRIAL_NAME+FILE_SEPARATOR+folder+FILE_SEPARATOR)

    data_home = DATA_DIR+TRIAL_NAME+FILE_SEPARATOR
    os.chdir(data_home)
    print(os.getcwd())

    for account in ACCOUNT_LIST:
        print(account)
        email_account = account + EMAIL_DOMAIN

        M = imaplib.IMAP4_SSL(IMAP_SERVER)
        M.login(email_account, PASSWORD)

        for folder in EMAIL_FOLDERS:
            os.chdir(data_home+FILE_SEPARATOR+folder)
            print(os.getcwd())
            rv, data = M.select(folder)
            if rv == 'OK':
                print "Processing mailbox: ", folder
                process_mailbox(M,account,folder)
                M.close()
            else:
                print "ERROR: Unable to open mailbox ", rv
        M.logout()

if __name__ == "__main__":
    main()
