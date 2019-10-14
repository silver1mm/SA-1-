import socket
import json
from multiprocessing import Process
import re


class Connection:
    def __init__(self, addr, recevie_queue, send_queue):
        self.addr = addr
        self.socket = socket.socket()
        self.recevie_queue = recevie_queue
        self.send_queue = send_queue

    def start_connect(self):
        self.start_recevie()
        self.start_send()

    def start_recevie(self):
        t = Process(target=self.recevie)
        t.daemon = True
        t.start()

    def start_send(self):
        t = Process(target=self.send)
        t.daemon = True
        t.start()

    def recevie(self):
        try:
            while True:
                data = self.socket.recv(1024).decode()
                data = json.loads(data)
                print(data)
                if data['code'] == 1:
                    self.recevie_queue.put(data['msg']+'\n')
                else:
                    result = data['result']
                    for date, res in result.items():
                        msg = '...........................\n' + date + ':\n'
                        for field, value in res.items():
                            msg = msg + field + ': ' + str(value) + '\n'
                            self.recevie_queue.put(msg)
        except Exception as e:
            print(e)
            return

    def send(self):
        try:
            while True:
                msg = self.send_queue.get()
                date = re.findall(r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})', msg['date'])
                field = re.split(r'[\s:;]+', msg['field'])[:-1]
                msg = {'date': date, 'field': field}
                msg = json.dumps(msg)
                print(msg)
                self.socket.sendall(msg.encode('UTF-8'))
        except Exception as e:
            print(e)
            return

    def close_connect(self):
        try:
            self.socket.close()
            self.socket = None
        except Exception as e:
            print(e)

    def test_connect(self):
        try:
            self.socket.connect(self.addr)
        except Exception as e:
            print(e)
            self.recevie_queue.put('Failed connection\n')
            return False
        self.recevie_queue.put('Successful connection\n')
        print('Connection completed')
        return True
