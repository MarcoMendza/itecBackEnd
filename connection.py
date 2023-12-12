import mysql.connector


def get_db_connection():
    connection = mysql.connector.connect(
        host='tier-database.cfkhwouy9rnk.us-east-2.rds.amazonaws.com',
        user='admin',
        password='HolaTier',
        database='tier1',
        port=3306
    )
    return connection
