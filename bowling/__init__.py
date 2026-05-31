import pymysql

# Register PyMySQL as MySQLdb so Django can use the mysql backend.
pymysql.install_as_MySQLdb()
