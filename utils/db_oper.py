import sqlalchemy as sa
import sqlite3
import pandas as pd
from pandas.io import sql


def csv_to_sql(csvfilename, db_path, sql_tblname, encoding='gbk', if_exists='append'):
	cnx = sqlite3.connect(db_path)
	df = pd.read_csv(csvfilename, encoding=encoding)
	sql.to_sql(df, name=sql_tblname, con=cnx, index=False, if_exists=if_exists)
	cnx.commit()
	cnx.close()
	print('Finishing dump data from {} to {}.{}'.format(csvfilename, db_path, sql_tblname))