import tkinter as tk
from threading import Thread


class Layer:
    def __init__(self, addr, recevie_queue, send_queue):
        self.addr = addr
        self.recevie_queue = recevie_queue
        self.send_queue = send_queue
        self.initial()
        self.start_show()
        self.window.mainloop()

    def initial(self):
        self.window = tk.Tk()
        self.window.resizable(width=False, height=False)
        self.window.title('业务数据分析系统')
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        frame_msg = tk.Frame(self.window, width=380, height=270, bg='white')
        frame_data = tk.Frame(self.window, width=380, height=80, bg='white')
        self.msgBox = tk.Text(frame_msg)
        self.fieldBox = tk.Text(frame_data)
        self.dateBox = tk.Text(frame_data)
        self.fieldLabel = tk.Label(frame_data, text="查询项")
        self.dateLabel = tk.Label(frame_data, text="日期")
        self.sendButton = tk.Button(frame_data, text='查询', command=self.search)
        vbar = tk.Scrollbar(frame_msg, orient=tk.VERTICAL)
        self.msgBox['yscrollcommand'] = vbar.set
        vbar['command'] = self.msgBox.yview
        frame_msg.grid(row=1, column=0, padx=2, pady=5)
        frame_data.grid(row=0, column=0, padx=2, pady=5)
        frame_msg.grid_propagate(0)
        frame_data.grid_propagate(0)
        self.msgBox.place(x=0, width=360, height=270)
        vbar.place(x=360, width=20, height=270)
        self.fieldLabel.place(x=10, y=10, width=50, height=20)
        self.fieldBox.place(x=70, y=10, width=300, height=20)
        self.dateLabel.place(x=10, y=50, width=50, height=20)
        self.dateBox.place(x=70, y=50, width=150, height=20)
        self.sendButton.place(x=250, y=50, width=40, height=20)

    def close(self):
        self.window.destroy()

    def search(self):
        try:
            request = {}
            request['field'] = self.fieldBox.get('0.0', 'end')
            request['date'] = self.dateBox.get('0.0', 'end')
            self.send_queue.put(request)
            self.fieldBox.delete('0.0', 'end')
            self.dateBox.delete('0.0', 'end')
        except Exception as e:
            print(e)

    def start_show(self):
        self.show_proc = Thread(target=self.show)
        self.show_proc.setDaemon(True)
        self.show_proc.start()

    def show(self):
        try:
            while True:
                msg = self.recevie_queue.get()
                self.msgBox.insert('end', msg)
        except Exception as e:
            print(e)