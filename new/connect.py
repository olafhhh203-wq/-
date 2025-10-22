from mysql.connector import MySQLConnection, Error

from read_config import read_db_config


def connect():
    """ Connect to MySQL database """

    #db_config = read_db_config()
    db_config = read_db_config(filename='d:/anaconda/Anaconda/envs/dachuang/project_self/config.ini')
    conn = None
    try:
        print('Connecting to MySQL database...')
        conn = MySQLConnection(**db_config)

        if conn.is_connected():
            print('Connection established.')
        else:
            print('Connection failed.')

    except Error as error:
        print(error)

    finally:
        if conn is not None and conn.is_connected():
            conn.close()
            print('Connection closed.')


if __name__ == '__main__':
    connect()
