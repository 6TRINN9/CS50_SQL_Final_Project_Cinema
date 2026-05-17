import os

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "cinema"
DB_USER = "postgres"
DB_PASSWORD = "postgres"

REDIS_HOST = "localhost"
REDIS_PORT =  6379
REDIS_DB =  0

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"