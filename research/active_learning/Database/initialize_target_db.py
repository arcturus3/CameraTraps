'''
initialize_target_db.py

Creates a PostgreSQL database of camera trap images for use in active learning for classification.

'''

import argparse, glob, json, os, psycopg2
from datetime import datetime
from peewee import *
from DB_models import *


parser = argparse.ArgumentParser(description='Initialize a PostgreSQL database for a dataset of camera trap images to use for active learning for classification.')
parser.add_argument('--db_name', default='missouricameratraps', type=str,
                    help='Name of the output Postgres DB.')
parser.add_argument('--db_user', default='new_user', type=str,
                    help='Name of the user accessing the Postgres DB.')
parser.add_argument('--db_password', default='new_user_password', type=str,
                    help='Password of the user accessing the Postgres DB.')
parser.add_argument('--source', metavar='DIR',
                    help='Path to dataset directory containing all images')
parser.add_argument('--coco_json', metavar='DIR',
                    help='Path to COCO Camera Traps json file if available', default=None)

args = parser.parse_args()

# Database connection credentials
DB_NAME = args.db_name
USER = args.db_user
PASSWORD = args.db_password
#HOST = 'localhost'
#PORT = 5432

# Options for getting dataset image data
COCO_CAMERA_TRAPS_JSON = args.coco_json # if image data is available in Coco Camera Traps JSON format
coco_json = None


# DATABASE INITIALIZATION CODE
# Connect to postgres database owned by superuser postgres
conn = psycopg2.connect(dbname='postgres', user='postgres', password='postgres', host='localhost')
conn.autocommit = True # this is needed to create database if it does not exist
cursor = conn.cursor()

# Check if the user USER with password PASSWORD exists
query = "SELECT 1 FROM pg_roles WHERE rolname='%s'"%(USER)
cursor.execute(query)
qresult = cursor.fetchone()
if qresult is None: # if not then create this user
    query = "CREATE USER %s PASSWORD '%s';"%(USER, PASSWORD)
    cursor.execute(query)
else:
    query = "ALTER USER %s WITH PASSWORD '%s'"%(USER, PASSWORD) # update the password in case it doesn't match, need to fix this later
    cursor.execute(query)


# Check if the database DB_NAME already exists
query = "SELECT 1 FROM pg_catalog.pg_database WHERE datname = '%s'"%(DB_NAME)
cursor.execute(query)
qresult = cursor.fetchone()
if qresult is None: # if not then create the database
    query = "CREATE DATABASE %s"%(DB_NAME)
    cursor.execute(query)
    
# Grant USER access to DB_NAME
query = "GRANT ALL PRIVILEGES ON DATABASE %s TO %s;"%(DB_NAME, USER)
cursor.execute(query)

# Close connection
conn.close()


# SET UP TABLES
# Try to connect as USER to database DB_NAME through peewee
db = PostgresqlDatabase(DB_NAME, user=USER, password=PASSWORD, host='localhost')
db_proxy.initialize(db)
db.create_tables([Info])

if COCO_CAMERA_TRAPS_JSON:
    coco_json = json.load(open(COCO_CAMERA_TRAPS_JSON, 'r'))
    coco_json_info = coco_json['info']
    v = eval(coco_json_info['version'])
    y = coco_json_info['year']
    d = datetime.strptime(coco_json_info['date_created'], '%Y-%m-%d').date()
    info = Info.create(name=DB_NAME, description=coco_json_info['description'], contributor= coco_json_info['contributor'], 
                    version=v, year=y, date_created=d)
else:
    info = Info.create(name=DB_NAME, description='', contributor=USER, 
                    version=0.0, year=2019, date_created=datetime.today().date())
info.save()



# img_paths = glob.glob(os.path.join(args.source, '**/*.JPG'), recursive=True)
# coco_json = json.load(open(COCO_JSON, 'r'))
# print(coco_json.keys())
# print(coco_json['info'])




# RECYCLING
# db.connect()
# # Define some tables
# class Person(Model):
#     name = CharField()
#     birthday = DateField()
#     class Meta:
#         database = db

# class Pet(Model):
#     owner = ForeignKeyField(Person, backref='pets')
#     name = CharField()
#     animal_type = CharField()
#     class Meta:
#         database = db
# db.create_tables([Person, Pet])
# uncle_bob = Person(name='Bob', birthday=date(1960, 1, 15))
# uncle_bob.save()



# db = PostgresqlDatabase(
#     'active_learning_classification',
#     user='postgres',
#     password='postgres',
#     host='localhost',
#     port=5432
# )

# # db.connect()

# for person in Person.select():
#     print(person.name)
