import psycopg2 as pg

class postgresDb:
    def __init__(self):
        self.conn = pg.connect(host='localhost',dbname='Summary_Db',user='postgres',password='Cyber9600',port=5432)
        self.cur = self.conn.cursor()


    def disconnect(self):
        self.cur.close()
        self.conn.close()

    def showData(self,query,val=None):
        try:
            self.cur.execute(query,val)
            result = self.cur.fetchall()
            return result
        except Exception as e:
            return {"data":e,'status code':400}

    
    def create(self,query):
        try:
            self.cur.execute(query)
            self.conn.commit()
            return {"data":'Table created successfully',"status code":200}
            
        except Exception as e:
            self.conn.rollback()
            return {"data":'Table not created successfully','error':e}


    def insertData(self,query,val=None):
        try:
            if val:
                self.cur.execute(query,val)
            else:
                self.cur.execute(query)
            
            self.conn.commit()
            return {"data":'insert data successfully',"status code":200}
            
        except Exception as e:
            self.conn.rollback()
            return {"data":'insert data not successfully','error':e}

    def deleteData(self,query):
        try:
            self.cur.execute(query)
            self.conn.commit()
            return {"data":'delete data successfully',"status code":200}
            
        except Exception as e:
            self.conn.rollback()
            return {"data":'delete data not successfully','error':e}


    def updateData(self,query):
        try:
            self.cur.execute(query)
            self.conn.commit()
            return {"data":'update data successfully',"status code":200}
            
        except Exception as e:
            self.conn.rollback()
            return {"data":'update data not successfully','error':e}



# pg=postgresDb()

# query1=pg.create("""CREATE EXTENSION IF NOT EXISTS "uuid-ossp";""")

# query2=pg.create("""
#         Create Table if not exists UserBio(
#         user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
#         name varchar(255),
#         email varchar(125),
#         password varchar(125))
# """)
