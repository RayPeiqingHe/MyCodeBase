# ConnInfo.py

from ConfigParser import SafeConfigParser


class ConnInfo:
    """
    Wrapper class for connection info

    Attributes
    ==========
    db_host : string
        the host name of the SQL server
    db_name : string
         the data base name to connect
    db_user : string
         the user name
    db_pass : string
         the encryted password
    """

    def __init__(self, config_file):
        parser = SafeConfigParser()
        parser.read(config_file)

        # Connect to the MySQL instance
        self.db_host = parser.get('log_in', 'host')
        self.db_name = parser.get('log_in', 'db')
        self.db_user = parser.get('log_in', 'username')
        self.db_pass = parser.get('log_in', 'password')
        self.db_query = parser.get('log_in', 'security_master_query')
