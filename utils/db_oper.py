import sqlalchemy as sa
import sqlite3 as sql
import json



def insert_dict_to_table(tblname, dict, cursor):
    q = 'insert into {table_name} values {data}'
    q = q.replace('{table_name}', tblname)
    dict
    return
