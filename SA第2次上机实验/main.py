import Connection
from Layer import Layer

from multiprocessing import Queue

if __name__ == '__main__':
    sender = Queue()
    recevier = Queue()
    conn = Connection.Connection(('localhost', 23456), recevier, sender)
    if not conn.test_connect():
        exit(1)
    conn.start_connect()
    layer = Layer(('localhost', 23456), recevier, sender)
    conn.close_connect()