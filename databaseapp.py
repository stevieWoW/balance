import logging
import configparser
import pandas.io.sql as psql
import MySQLdb


class databaseapp:
	#create database access
	def DatabaseAccess():
		DB=None
		if DB is None:
			config = configparser.ConfigParser()
			if not config.read('/var/www/html/Dash/assets/config.ini'):
				logging.critical('could not open config file')
				exit(1)
			else:
				try:
					logging.info('try to establish a DB connection')
					DB = MySQLdb.connect(host=config['DATABASE'].get('SERVER'),user=config['DATABASE'].get('USERNAME'),passwd=config['DATABASE'].get('PASSWORD'),db=config['DATABASE'].get('DATABASE'))
					logging.info('Database Connection established')
					return DB
				except configparser.Error as es:
					logging.Error('Error occured: ' + es)
					return 1

    ##################################################
	def ExecuteQuery(query,name,string):
		#execute query and return dataframe
		w = "where"
		rows = query[0]["rows"]
		table = query[0]["table"]
		if "where" in query[0]:
			where = query[0]["where"]
			#build where clause
			for i in where:
		
				for key, value in i.items():
					if key != "Operator":
						if value != "":
							w = w + " " + i["Operator"] + " " + key  + value
		else:
			w=""


		#check if groupby was set
		if  "groupby" in query[0]:
			groupby = " group by " + query[0]["groupby"]
		else:
			groupby = ""

		#create query
		query = rows + table + " " + w + groupby + ";"
		logging.debug("ExecuteQuery-{0}: {1}".format(name,query))
		
		if string == True:
			#return as a string
			df = psql.read_sql(query,databaseapp.DatabaseAccess())
			logging.debug('df-{0}: {1}'.format(name,df.to_string(header=False,index=False)))

			return df.to_string(header=False,index=False)
		elif string == False:
			#return as a dataframe
			df = psql.read_sql(query,databaseapp.DatabaseAccess())
			logging.debug('df-{0}: {1}'.format(name,df))

			return df
