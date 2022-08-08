from psycopg2 import Error
import request_data
from request_data import connection, cursor

try:
    def set_assignee():
        request_data.get_all()
        request_data.select_request()

    set_assignee()

except (Exception, Error) as error:
    print('Error while connecting to PostgreSQL:', error)
finally:
    if connection:
        cursor.close()
        connection.close()
        print('\nPostgreSQL connection is closed')