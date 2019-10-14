import pymssql
import socket
from multiprocessing.pool import Pool
import json
import sys
import getopt


class Server:
    def __init__(self, host, user, password, databasename, tablename):
        self.host = host
        self.databasename = databasename
        self.user = user
        self.password = password
        self.tablename = tablename
        self.pool = Pool(processes=4)

    def listen(self):
        self.socket = socket.socket()
        self.socket.bind(('localhost', 23456))
        self.socket.listen(10)
        while True:
            newsocket, addr = self.socket.accept()
            print(addr)
            self.pool.apply_async(self.connect, (newsocket,))

    def connect(self, socket):
        conn, cursor = self.create_conn()
        while True:
            try:
                msg = socket.recv(1024)
                msg = json.loads(msg.decode())
                result = {'code': 0, 'result': {}}
                dateall = msg['date']
                field = msg['field']
                for date in dateall:
                    result['result'][date] = {}
                    sql = self.set_sql(date, field)
                    cursor.execute(sql)
                    receive = cursor.fetchone()
                    for i in range(len(field)):
                        result['result'][date][field[i]] = receive[i]
                result = json.dumps(result)
                socket.sendall(result.encode('UTF-8'))
            except Exception as e:
                print(e)
                cursor.close()
                conn.close()
                self.close()
                return

    def create_conn(self):
        try:
            conn = pymssql.connect(host=self.host, user=self.user, password=self.password,
                                 database=self.databasename, charset='utf8')
            cursor = conn.cursor()
            return conn, cursor
        except Exception as e:
            raise e

    def set_sql(self, date, args):
        field = ''
        for i in args:
            field += i
            field += ','
        field = field[:-1]
        sql = 'select {} from {} where 日期 = \'{}\''.format(field, self.tablename, date)
        print(sql)
        return sql

    def close(self):
        try:
            self.socket.close()
        except:
            return

    def __getstate__(self):
        self_dict = self.__dict__.copy()
        del self_dict['pool']
        return self_dict

    def __setstate__(self, state):
        self.__dict__.update(state)


if __name__ == '__main__':
    host = 'localhost'
    port = 2345
    user = 'sa'
    password = '123456'
    databasename = 'EDUC'
    tablename = 'data'
    try:
        options, args = getopt.getopt(sys.argv[1:], "u:P:p:", ['user=', 'password='])
    except:
        options = None
        exit(1)
    for n, v in options:
        if n in ('-u', '--user'):
            user = v
        elif n in ('-p', '--password'):
            password = v
    print('Finish creating the server!')
    server = Server(host, user, password, databasename, tablename)
    server.listen()

