# encoding: utf-8
import boto3
from threading import Thread
import tkinter as tk


class Receiver:
    def __init__(self):
        self.draw()
        self.initconnection()
        self.register_timer()
        self.window.mainloop()

    def initconnection(self):
        self.statu = '0'
        self.msgBox.insert('end', 'Loading For Link.\n', 'red')
        self.conn = ReceiveConn()
        result = self.conn.init("MyQueue1.fifo")
        if result == 0:
            self.msgBox.insert('end', 'Link Success!\n\n', 'red')
        else:
            self.msgBox.insert('end', 'Link Fail!\n', 'red')

    def draw(self):
        self.window = tk.Tk()
        self.window.resizable(width=False, height=False)
        self.window.title("MyQReceiver")
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        frame_top = tk.Frame(self.window, width=500, height=400, bg='white')
        frame_bottom = tk.Frame(self.window, width=500, height=30)
        self.msgBox = tk.Text(frame_top)
        self.changeButton = tk.Button(frame_bottom, text="切换消息群组", command=self.change_send)
        self.closeButton = tk.Button(frame_bottom, text="退出", command=self.close)
        self.channelLabel = tk.Label(frame_bottom, text="消息群组0")
        vbar = tk.Scrollbar(frame_top, orient=tk.VERTICAL)
        self.msgBox['yscrollcommand'] = vbar.set
        vbar['command'] = self.msgBox.yview
        frame_top.grid(row=0, column=0, padx=2, pady=5)
        frame_bottom.grid(row=2, column=0, padx=2, pady=5)
        frame_top.grid_propagate(0)
        frame_bottom.grid_propagate(0)
        self.msgBox.tag_config("green", foreground="green")
        self.msgBox.tag_config("red", foreground="red")
        self.msgBox.place(x=0,width=480,height=400)
        self.changeButton.grid(row=2, column=0, padx=20)
        self.closeButton.grid(row=2, column=2, padx=20)
        self.channelLabel.grid(row=2, column=1, padx=20)
        vbar.place(x = 480, width=20, height=400)

    def close(self):
        self.window.destroy()

    def change_send(self):
        self.statu = str((int(self.statu)+1)%3)
        self.channelLabel.config(text="消息群组"+ self.statu)

    def register_timer(self):
        self.conn.Receive(self.statu, self.msgBox)
        self.window.after(1000, self.register_timer)


class ReceiveConn:
    def init(self, QueueName):
        try:
            self.sqs = boto3.resource('sqs')
            self.queue = self.sqs.get_queue_by_name(QueueName=QueueName)
            return 0
        except Exception as e:
            print(e)
            return 1

    def Receive(self, chan, box):
        t = Thread(target=self.conn, args=(chan, box,))
        t.start()

    def conn(self, chan, box):
        for msg in self.queue.receive_messages(MessageAttributeNames=['Channel']):
            if msg.message_attributes is not None:
                chan_id = msg.message_attributes.get('Channel').get('StringValue')
                if chan_id == chan:
                    msgbody = msg.body.split('\n')
                    box.insert('end', 'Receiver{}:'.format(chan), 'green')
                    box.insert('end', msgbody[0]+'\n', 'green')
                    for i in range(1, len(msgbody)):
                        box.insert('end', msgbody[i]+'\n')

                    msg.delete()


if __name__ == '__main__':
    receiver = Receiver()