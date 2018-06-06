import sys
import os
import imaplib
import getpass
import pandas as pd

IMAP_SERVER = 'imap.gmail.com'
EMAIL_FOLDERS = ['LA-Response', 'LA-Nonresponse', 'INBOX', 'UNREAD']
EMAIL_DOMAIN ='@gmail.com'
PASSWORD = 'BdeepTrulia'

PROJ_ROOT = '/Users/Chris/Research/trulia_project/test_folder/'
DATA_DIR = '/Users/Chris/Research/trulia_project/test_folder/losangeles_data'

FILE_SEPARATOR = '/'
NAMES_FILE = 'project_files/names_market.csv'
TRIAL_NAME= 'losangeles'

names = pd.read_csv(PROJ_ROOT+NAMES_FILE)
# ACCOUNT_LIST = names['email'].values
## Can subset accounts here
ACCOUNT_LIST = ['jramirez7561','woodleslie542','shanicethomas086']

def main():
    mailbox_counts_list = []
    mailbox_df = pd.DataFrame(columns=EMAIL_FOLDERS)
    for account in ACCOUNT_LIST:
        mailbox_dict = {}
        print("============")
        print("ACCOUNT: " + account)
        email_account = account + EMAIL_DOMAIN

        M = imaplib.IMAP4_SSL(IMAP_SERVER)
        M.login(email_account, PASSWORD)

        account_folders = M.list()
        print("ALL_FOLDERS: ")
        print(account_folders)

        for folder in EMAIL_FOLDERS:

            mailbox_counts = 0
            rv, data = M.select(folder, readonly=True)

            if rv == 'OK':
                print("Selected folder: " + folder)
                rv_search, data_search = M.search(None,"ALL")
                if rv_search == 'OK':
                    mailbox_counts = len(data_search[0].split())
                    print (str(mailbox_counts) + " messages in folder " + folder)
                else:
                    print("ERROR: searching for folders in " + folder)
                    print("rv: "+str(rv_search))
            else:
                print("ERROR: selecting folder: "+folder)
                print("rv: "+str(rv))
            #M.close()
            mailbox_dict[folder]=mailbox_counts
        mailbox_counts_list.append(mailbox_dict)

        M.logout()
    mailbox_df = pd.DataFrame(mailbox_counts_list, index=ACCOUNT_LIST)
    os.chdir(DATA_DIR)
    mailbox_df.to_csv("mailbox_counts.csv")

if __name__ == "__main__":
    main()
