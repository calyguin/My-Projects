import psycopg2
from tabulate import tabulate
import sys

# Connecting to a database
connection = psycopg2.connect(user='postgres',
                                  password='password',
                                  host='127.0.0.1',
                                  port='5432',
                                  database='sql_demo')
connection.autocommit = True
cursor = connection.cursor()

col_names = ['Request Num', 'Request ID', 'Date of Request', 'Request Message',
             'Assignee Login', 'Request Respond', 'Request Status']

login = input('\nPLEASE ENTER YOUR LOGIN: ')

def get_all():

    # Displaying all incoming requests
    all_requests_query = ''' SELECT * FROM techsupport_requests ORDER BY request_num; '''
    cursor.execute(all_requests_query)
    print('\nALL INCOMING REQUESTS: \n')
    print(tabulate(cursor.fetchall(), headers=col_names, tablefmt='fancy_grid'))

def select_request():

    # Selecting a request to respond to
    request = input('\nPLEASE SELECT THE REQUEST NUMBER YOU WOULD LIKE TO RESPOND TO: ')
    print()
    one_row_query = ''' SELECT * FROM techsupport_requests WHERE request_num = '{0}'; '''.format(request)
    set_inprogress_query = ''' UPDATE techsupport_requests SET request_status = 'IN-PROGRESS' 
                               WHERE request_num = '{0}'; '''.format(request)
    cursor.execute(one_row_query)
    request_row = cursor.fetchall()

    # Checking if selected request is not closed or in-progress
    check_status_query = ''' SELECT request_status FROM techsupport_requests 
                             WHERE request_num = '{0}'; '''.format(request)
    cursor.execute(check_status_query)
    check_status = cursor.fetchone()
    if check_status in closed_or_inprogress():
        warning = input('\nTHIS REQUEST IS ALREADY CLOSED OR CURRENTLY IN-PROGRESS, '
                        'ARE YOU SURE YOU WANT TO INTERACT WITH IT? (YES/NO): ')
        print()
        if warning in 'YES, Yes, yes':
            cursor.execute(set_inprogress_query)
            print(tabulate(request_row, headers=col_names, tablefmt='fancy_grid'))
        elif warning in 'NO, No, no':
            get_all()
            select_request()
        else:
            sys.exit('Unknown respond, please restart the program')
    else:
        cursor.execute(set_inprogress_query)
        print(tabulate(request_row, headers=col_names, tablefmt='fancy_grid'))

    # Responding to the request
    request_query = ''' SELECT request_message FROM techsupport_requests WHERE request_num = '{0}'; '''.format(request)
    cursor.execute(request_query)
    print('\nREQUEST MESSAGE: ', tabulate(cursor.fetchall(), tablefmt='plain'))
    respond = input('\nYOUR RESPOND TO THE REQUEST: ')
    update_respond_query = ''' UPDATE techsupport_requests SET request_respond = '{0}' 
                               WHERE request_num = '{1}'; '''.format(respond, request)
    cursor.execute(update_respond_query)

    # Setting the assignee's login in the request
    login_query = ''' UPDATE techsupport_requests SET assignee_login = '{0}' WHERE request_num = '{1}' 
                      AND request_respond != ''; '''.format(login, request)
    cursor.execute(login_query)
    set_queries()

def set_queries():

    # Setting appropriate statuses to all requests, removing logins from requests with no respond
    # and displaying all requests once again
    set_closed_query = ''' UPDATE techsupport_requests SET request_status = 'CLOSED' WHERE request_respond != ''; '''
    set_opened_query = ''' UPDATE techsupport_requests SET request_status = 'OPENED' WHERE request_respond = ''; '''
    login_clear_query = ''' UPDATE techsupport_requests SET assignee_login = '' WHERE request_respond = ''; '''
    cursor.execute(set_closed_query), cursor.execute(set_opened_query), cursor.execute(login_clear_query),
    get_all()

def closed_or_inprogress():

    # Checking all requests with 'closed' or 'in-progress' statuses to turn up the if statement
    check_closed_status_query = ''' SELECT request_status FROM techsupport_requests WHERE request_status = 'CLOSED' 
                             OR request_status = 'IN-PROGRESS'; '''
    cursor.execute(check_closed_status_query)
    closed_and_inprogress = cursor.fetchall()
    return closed_and_inprogress