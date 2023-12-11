import mysql.connector


def get_db_connection():
    connection = mysql.connector.connect(
        host='tier-database.cfkhwouy9rnk.us-east-2.rds.amazonaws.com',
        user='admin',
        password='HolaTier',
        database='main'
    )
    return connection
