import csv
import smtplib
from email.mime.text import MIMEText
import time
import re

DEBUG = True
user_account = ""
user_password = ""  # autherization code if using 163, qq, etc.
user_smtp_server = ""
user_smtp_port = ""
file_to_open = ""  # currently only support csv file parsing
sent_list_file = ""
waiting_list, sent_list = {}, {}
subject = ""
content = ""
sleep = False

def send(mail, name, id, score):
    msg = MIMEText(content.format(name, id, score), 'html')
    msg['From'] = user_account
    msg['Subject'] = subject
    if DEBUG:
        msg['To'] = user_account
    else:
        msg['To'] = mail
    server.send_message(msg)

def connect(user_smtp_server, user_smtp_port, user_account, user_password):
    head = user_smtp_server.split('.')
    if head[0] == "mail":
        server = smtplib.SMTP(user_smtp_server)
    else:
        if len(user_smtp_port) != 0:
            user_smtp_port = eval(user_smtp_port)
            server = smtplib.SMTP(user_smtp_server, user_smtp_port)
            sleep = True
        else:
            user_smtp_server = user_smtp_server.replace("smtp", "mail", 1)
            server = smtplib.SMTP(user_smtp_server)        
    reply = server.ehlo()
    if reply[0] == 250:
        print('Conneted to {}!'.format(user_smtp_server), flush = True)
    else:
        print('Failed to connect to {}!'.format(user_smtp_server), flush = True)
        exit(1)
    server.starttls()
    reply = server.login(user_account, user_password)
    if reply[0] == 235:
        print('Logged in as {}!'.format(user_account), flush = True)
    else:
        server.quit()
        print('Failed to login as {}!'.format(user_account), flush = True)
        exit(1)
    return server

def read_waiting_list(file_to_open, waiting_list):
    sent_list= {}
    with open(file_to_open, newline='',encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for i, row in enumerate(reader):
            entries = row[0].split(',')
            id = entries[0]
            name = entries[1]
            email = entries[3]
            score = entries[4]
            waiting_list[i] = (id, name, email, score)
            sent_list[i] = False
    return waiting_list, sent_list
#         print(name, email, score, sent_list[i])

def write_sent_list(waiting_list, sent_list):
    with open("sent_list.txt", "w", encoding='utf8') as output:
        for i in range(len(waiting_list)):
            record = (', '.join(waiting_list[i]))+ ', ' + str(sent_list[i]) + '\n'
            print(record)
            output.write(record)
    
def read_sent_list(file_to_open, sent_list):
    with open(file_to_open, newline='', encoding='utf-8') as verify:
        reader = verify.readlines()
        for i, row in enumerate(reader):
            record = [x for x in re.split('[,\s]+', row) if x != '']
            sent_list[i] = eval(record[5].title())
        return sent_list
    
def print_list(waiting_list, sent_list):
    for i in range(len(waiting_list)):
        id, name, email, score = waiting_list[i]
        print(name, email, score, sent_list[i])

def initiate(file_to_open = file_to_open, 
             waiting_list = waiting_list, 
             preview = False):
    waiting_list, sent_list = read_waiting_list(file_to_open, waiting_list)
    try:
        sent_list = read_sent_list(sent_list_file, sent_list)
    except:
        write_sent_list(waiting_list, sent_list)
    if preview:
        print_list(gs.waiting_list, gs.sent_list)
    return waiting_list, sent_list

def send_score(waiting_list, sent_list):
    print('Total waiting: {}'.format(len(waiting_list)))
    for i in range(len(waiting_list)):
        print(len(sent_list))
        if sent_list[i]:
            print("Already sent to {}".format((waiting_list[i])[1]))
            continue
        if i % 25 == 0:
            print('Inline waiting: {}'.format(len(waiting_list)-i))
        if i == 0:
            server = connect(user_smtp_server, user_smtp_port, user_account, user_password)
        d = waiting_list[i]
        while not sent_list[i]:
            try:
                print('Sending: {} ... '.format(d[2]), end = '', flush = True)
                send(d[2], d[1], d[0], d[3])
                print('Success!', flush = True)
            except smtplib.SMTPSenderRefused:
                print('Failed!', flush = True)
                print('Waiting for additional timeout ... ', end = '', flush = True)
                time.sleep(65)
                server = connect(user_smtp_server, user_smtp_port, user_account, user_password)
                print('Done.', flush = True)
            except smtplib.SMTPServerDisconnected:
                print('Failed: login expired!', flush = True)
                connect(user_smtp_server, user_smtp_port, user_account, user_password)
                print('reconnected!', flush = True)
            else:
                sent_list[i] = True
                break
        if sleep & (i % 5 == 4):
            print('Waiting for regular timeout ... ', end = '', flush = True)
            time.sleep(65)
            print('Done.', flush = True)
            server = connect(user_smtp_server, user_smtp_port, user_account, user_password)
    print('')
    print('All sent.')        
    server.quit()
    