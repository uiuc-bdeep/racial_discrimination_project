import sys
import os
import imaplib
import getpass
import pandas as pd
import json

PROJ_ROOT = os.environ['PROJ_ROOT']
with open(PROJ_ROOT + 'parameters.json') as parameter_json:
    params = json.load(parameter_json)

IMAP_SERVER = 'imap.gmail.com'
EMAIL_FOLDERS= [params['EMAIL_PREFIX']+folder for folder in ['-Response','-Nonresponse']]
EMAIL_DOMAIN ='@gmail.com'
PASSWORD = 'BdeepTrulia'
print(EMAIL_FOLDERS)

EMAIL_DIR = params['EMAIL_DIR']
print(EMAIL_DIR)

ACCOUNT_LIST = params['ACCOUNT_LIST']
print(ACCOUNT_LIST)

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
    if not os.path.exists(EMAIL_DIR):
        os.makedirs(EMAIL_DIR)
    for folder in EMAIL_FOLDERS:
        if folder in os.listdir(EMAIL_DIR):
            print("Found "+folder+" in data directory")
        else:
            print("Making folder " + folder)
            os.mkdir(EMAIL_DIR+folder)

    os.chdir(EMAIL_DIR)
    print(os.getcwd())

    for account in ACCOUNT_LIST:
        print(account)
        email_account = account + EMAIL_DOMAIN

         M = imaplib.IMAP4_SSL(IMAP_SERVER)
         M.login(email_account, PASSWORD)

        for folder in EMAIL_FOLDERS:
            os.chdir(EMAIL_DIR+folder)
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

