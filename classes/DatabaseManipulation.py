"""Class to connect and manipulate different databases.

accepts: mongodb
todo: accept other databases
methods:
    " >>> insert_one(database_name, collection_name, data)
    " >>> insert_many(database_name, collection_name, data_list)
    " >>> find_all(database_name, collection_name):
    " >>> find_by_object(database_name, collection_name, obj)
    " >>> count_records(database_name, collection_name)

"""

from pymongo import MongoClient

mongo_config = {
    'local':  {'url': 'localhost', 'port': 27017},
    'prod': {'url': 'URL', 'port': 'PORT'}
}


class DatabaseManipulation(object):
    def __init__(
            self,
            db_name,
            env):
        """Client for database instances.
        Set/store the connection and chosen database.
        :param db_name:
        :param env (if optional 'local' is defined):
        """

        self.db_name = db_name
        self.connection = self._create_client(env or 'local')
        self.connection_database = None

    def _create_client(self, env):
        """Create database client.
        Set database instance according to database option and environment.
        :param env:
        :return DBClient / Exception:
        """

        if self.db_name == 'mongo' and env in mongo_config:
            return MongoClient(mongo_config[env]['url'], mongo_config[env]['port'])
        else:
            raise Exception("Database or environment not accepted. Configure it first!")

    def get_client(self):
        """Get database client connection.

        :return DBClientConnection:
        """
        return self.connection

    def _get_collection(self, name):
        """Get database table/collection instance if exists.

        :param name:
        :return DBClientCollection:
        """
        if self.connection is None:
            raise Exception("Database not connected!")
        else:
            if self.db_name == 'mongo':
                return self.connection[name]
            else:
                raise Exception("Database not accepted. Configure it first!")

    def insert_one(self, database_name, collection_name, data):
        """Insert one row into database table.

        :param database_name:
        :param collection_name:
        :param data:
        :return inserted_id:
        """
        if self.connection is None:
            raise Exception("Database not connected!")
        else:
            if self.db_name == 'mongo':
                return self.connection[database_name][collection_name].insert_one(data).inserted_id
            else:
                raise Exception("Database not accepted. Configure it first!")

    def insert_many(self, database_name, collection_name, data_list):
        """Insert many rows to database table.

        :param database_name:
        :param collection_name:
        :param data_list:
        :return inserted_id_list:
        """

        if self.connection is None:
            raise Exception("Database not connected!")
        else:
            if self.db_name == 'mongo':
                return self.connection[database_name][collection_name].insert_many(data_list)
            else:
                raise Exception("Database not accepted. Configure it first!")

    def find_all(self, database_name, collection_name):
        """Find all rows from specific table name.

        :param database_name:
        :param collection_name:
        :return rows_list:
        """
        if self.connection is None:
            raise Exception("Database not connected!")
        else:
            if self.db_name == 'mongo':
                return self.connection[database_name][collection_name].find()
            else:
                raise Exception("Database not accepted. Configure it first!")

    def find_by_object(self, database_name, collection_name, obj):
        """ Search row by object filter in database table.

        :param database_name:
        :param collection_name:
        :param obj:
        :return row_searched:
        """
        if self.connection is None:
            raise Exception("Database not connected!")
        else:
            if self.db_name == 'mongo':
                return self.connection[database_name][collection_name].find(obj)
            else:
                raise Exception("Database not accepted. Configure it first!")

    def count_records(self, database_name, collection_name):
        """Count records from specific table.

        :param database_name:
        :param collection_name:
        :return rows_qty:
        """
        if self.connection is None:
            raise Exception("Database not connected!")
        else:
            if self.db_name == 'mongo':
                return self.connection[database_name][collection_name].count()
            else:
                raise Exception("Database not accepted. Configure it first!")