# encoding: utf-8
import boto3
import tkinter as tk
import time
from threading import Thread


def create(QueueName):
    sqs = boto3.resource('sqs')
    try:
        sqs.create_queue(QueueName=QueueName,
                         Attributes={'FifoQueue': 'true', 'ContentBasedDeduplication': 'true'})
    except Exception as e:
        print(e)


def delete(QueueName):
    sqs = boto3.resource('sqs')
    try:
        queue = sqs.get_queue_by_name(QueueName=QueueName)
        queue.delete()
    except Exception as e:
        print(e)


class Sender:

    def __init__(self):
        self.draw()
        self.initconnection()
        self.window.mainloop()

    def initconnection(self):
        self.statu = '0'
        self.msgBox.insert('end', 'Loading For Link.\n', 'red')
        self.conn = SendConnect()
        result = self.conn.init("MyQueue1.fifo")
        if result == 0:
            self.msgBox.insert('end', 'Link Success!\n\n', 'red')
        else:
            self.msgBox.insert('end', 'Link Fail!\n', 'red')

    def draw(self):
        self.window=tk.Tk()
        self.window.resizable(width=False, height=False)
        self.window.title("MyQSender")
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        frame_top = tk.Frame(self.window, width=500, height=300, bg='white')
        frame_center = tk.Frame(self.window, width=500, height=100, bg='white')
        frame_bottom = tk.Frame(self.window, width=500, height=30)
        self.msgBox = tk.Text(frame_top)
        self.sendBox = tk.Text(frame_center)
        self.sendButton = tk.Button(frame_bottom, text="发送", command=self.send)
        self.changeButton = tk.Button(frame_bottom, text="切换消息群组", command=self.changeSender)
        self.channelLabel = tk.Label(frame_bottom, text="消息群组0")
        self.closeButton = tk.Button(frame_bottom, text="退出", command=self.close)
        vbar = tk.Scrollbar(frame_top, orient=tk.VERTICAL)
        self.msgBox['yscrollcommand'] = vbar.set
        vbar['command'] = self.msgBox.yview
        frame_top.grid(row=0, column=0, padx=2, pady=5)
        frame_center.grid(row=1, column=0, padx=2, pady=5)
        frame_bottom.grid(row=2, column=0, padx=2, pady=5)
        frame_top.grid_propagate(0)
        frame_center.grid_propagate(0)
        frame_bottom.grid_propagate(0)
        self.msgBox.tag_config("green", foreground='green')
        self.msgBox.tag_config("red", foreground='red')
        self.msgBox.place(x=0, width=480, height=300)
        self.sendBox.grid()
        self.sendButton.grid(row=2, column=0, padx=20)
        self.changeButton.grid(row=2, column=1, padx=20)
        self.channelLabel.grid(row=2, column=2, padx=20)
        self.closeButton.grid(row=2, column=3, padx=20)
        vbar.place(x=480, width=20, height=300)

    def close(self):
        self.window.destroy()

    def send(self):
        msg = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\n '
        self.msgBox.insert("end", 'Sender{}:'.format(self.statu), "green")
        self.msgBox.insert("end", msg, "green")
        self.msgBox.insert("end", self.sendBox.get('0.0', "end"))
        msg += self.sendBox.get('0.0', "end")
        self.sendBox.delete('0.0', "end")
        self.conn.send(msg, self.statu)

    def changeSender(self):
        self.statu = str((int(self.statu) + 1) % 3)
        self.channelLabel.config(text='消息群组' + self.statu)


class SendConnect:

    def init(self, QueueName):
        try:
            self.sqs = boto3.resource('sqs')
            self.queue = self.sqs.get_queue_by_name(QueueName=QueueName)
            return 0
        except Exception as e:
            print(e)
            return 2

    def send(self, msg, chan):
        t = Thread(target=self.connect, args=(msg, chan,))
        t.start()

    def connect(self, msg, chan):
        attributes = {
             'Channel': {
                'StringValue': chan,
                'DataType': 'String'
             }
        }
        self.queue.send_message(MessageBody=msg, MessageAttributes=attributes, MessageGroupId=chan)


if __name__ == '__main__':
    create("MyQueue1.fifo")
    sender = Sender()
    delete("MyQueue1.fifo")