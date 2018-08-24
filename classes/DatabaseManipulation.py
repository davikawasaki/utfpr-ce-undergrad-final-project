from pymongo import MongoClient

mongo_config = {'url': 'localhost', 'port': 27017}

class DatabaseManipulation(object):
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = self._create_client()
        self.connection_database = None

    def _create_client(self):
        if self.db_name == 'mongo':
            return MongoClient(mongo_config['url'], mongo_config['port'])
        else:
            raise Exception("Database not accepted. Configure it first!")

    def get_client(self):
        return self.connection

    def get_client_database(self, database):
        return self.connection[database]

    def get_database(self, name):
        if self.connection is None:
            raise Exception("Database not connected!")
        else:
            if self.db_name == 'mongo':
                return self.connection[name]
            else:
                raise Exception("Database not accepted. Configure it first!")

    def _get_collection(self, name):
        if self.connection is None:
            raise Exception("Database not connected!")
        else:
            if self.db_name == 'mongo':
                return self.connection[name]
            else:
                raise Exception("Database not accepted. Configure it first!")

    def insert_one(self, database_name, collection_name, data):
        if self.connection is None:
            raise Exception("Database not connected!")
        else:
            if self.db_name == 'mongo':
                return self.connection[database_name][collection_name].insert_one(data).inserted_id
            else:
                raise Exception("Database not accepted. Configure it first!")

    def insert_many(self, database_name, collection_name, data_list):
        if self.connection is None:
            raise Exception("Database not connected!")
        else:
            if self.db_name == 'mongo':
                return self.connection[database_name][collection_name].insert_many(data_list)
            else:
                raise Exception("Database not accepted. Configure it first!")

    def find_all(self, database_name, collection_name):
        if self.connection is None:
            raise Exception("Database not connected!")
        else:
            if self.db_name == 'mongo':
                return self.connection[database_name][collection_name].find()
            else:
                raise Exception("Database not accepted. Configure it first!")

    def find_by_object(self, database_name, collection_name, obj):
        if self.connection is None:
            raise Exception("Database not connected!")
        else:
            if self.db_name == 'mongo':
                return self.connection[database_name][collection_name].find(obj)
            else:
                raise Exception("Database not accepted. Configure it first!")

    def count_records(self, database_name, collection_name):
        if self.connection is None:
            raise Exception("Database not connected!")
        else:
            if self.db_name == 'mongo':
                return self.connection[database_name][collection_name].count()
            else:
                raise Exception("Database not accepted. Configure it first!")