import psycopg2
from psycopg2 import Error

try:
    # Connecting to a database
    connection = psycopg2.connect(user='postgres',
                                  password='password',
                                  host='127.0.0.1',
                                  port='5432',
                                  database='sql_demo')

    connection.autocommit = True
    cursor = connection.cursor()

    # Creating a new table
    create_table_query = ''' CREATE TABLE ppcomplete
                (TUI                VARCHAR   PRIMARY KEY   NOT NULL,
                PRICE               INT,
                DATE_OF_TRANSFER    DATE,
                POSTCODE            VARCHAR,
                PROPERTY_TYPE       CHAR,
                OLD_OR_NEW          CHAR,
                DURATION            CHAR,
                PAON                VARCHAR,
                SAON                VARCHAR,
                STREET              VARCHAR,
                LOCALITY            VARCHAR,
                TOWN_OR_CITY        VARCHAR,
                DISTRICT            VARCHAR,
                COUNTY              VARCHAR,
                PPD_CATEGORY_TYPE   CHAR,
                RECORD_STATUS       CHAR); '''

    cursor.execute(create_table_query)
    print('\nTABLE CREATED SUCCESSFULLY\n')
    print('IMPORTING FILE...\n')

    # Importing data into the table
    import_query = ''' COPY ppcomplete FROM 'D:\Python\Projects\csv_file_filter\pp-complete.csv' WITH (FORMAT csv); '''

    cursor.execute(import_query)
    print('IMPORTED SUCCESSFULLY\n')
    print('EXPORTING FILE...\n')

    # Exporting duplicated data from the table as a new .csv file
    export_query = ''' COPY (SELECT * FROM
                (SELECT *, COUNT(*) OVER
                (PARTITION BY PAON, SAON, STREET, LOCALITY, TOWN_OR_CITY, DISTRICT, COUNTY) AS COUNT FROM ppcomplete) tableWithCount
                WHERE tableWithCount.count > 1) TO 'D:\Python\Projects\csv_file_filter\pp-complete-duplicates.csv' WITH (FORMAT csv); '''

    cursor.execute(export_query)
    print('EXPORTED SUCCESSFULLY\n')

except (Exception, Error) as error:
    print('Error while connecting to PostgreSQL', error)
finally:
    if connection:
        cursor.close()
        connection.close()
        print('PostgreSQL connection is closed')