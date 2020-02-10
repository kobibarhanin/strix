# import os
# import pymongo
#
# db_host = os.environ['DB_CTX'] if 'DB_CTX' in os.environ else 'bitz_db'
# agents = pymongo.MongoClient(f'mongodb://{db_host}:27017/')['agentsDb']['agent']
# logs_stream = pymongo.MongoClient(f'mongodb://{db_host}:27017/')['agentsDb']['logs_stream']