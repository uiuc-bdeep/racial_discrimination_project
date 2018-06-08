import sys
import os
import imaplib
import getpass
import pandas as pd

IMAP_SERVER = 'imap.gmail.com'
EMAIL_FOLDER = 'Inbox'
EMAIL_DOMAIN ='@gmail.com'
PASSWORD = 'BdeepTrulia'

PROJ_ROOT = '/path/to/racial_discrimination_project/'
NAMES_FILE = 'project_files/names_market.csv'

names = pd.read_csv(PROJ_ROOT+NAMES_FILE)
ACCOUNT_LIST = names['email'].values

## Can subset accounts here
# ACCOUNT_LIST = ['jalenj166','lamarw1668']

def process_mailbox(M, output_directory):
    """
    Dump all emails in the folder to files in output directory.
    """

    rv, data = M.search(None, "ALL")
    if rv != 'OK':
        print "No messages found!"
        return

    for num in data[0].split():
        rv, data = M.fetch(num, '(RFC822)')
        if rv != 'OK':
            print "ERROR getting message", num
            return
        print "Writing message ", num
        f = open('%s/%s.eml' %(output_directory, num), 'wb')
        f.write(data[0][1])
        f.close()

def main():
    for account in ACCOUNT_LIST:

        print(account)
        if account in os.listdir('.'):
            print (account + " already exists")
        else:
            os.mkdir(account)

        email_account = account + EMAIL_DOMAIN

        M = imaplib.IMAP4_SSL(IMAP_SERVER)
        M.login(email_account, PASSWORD)
        rv, data = M.select(EMAIL_FOLDER)
        if rv == 'OK':
            print "Processing mailbox: ", EMAIL_FOLDER
            process_mailbox(M, account)
            M.close()
        else:
            print "ERROR: Unable to open mailbox ", rv
        M.logout()

if __name__ == "__main__":
    main()
