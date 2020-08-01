from concurrent.futures import ThreadPoolExecutor, wait
from threading import Lock
from threading import Thread
from requests import get, head
import time
from tkinter import *
import tkinter.messagebox
import tkinter.filedialog
lock = Lock()

class Downloader():
    def __init__(self, url, nums, file):
        self.url = url
        self.num = nums
        self.name = file
        r = head(self.url)
        # 若资源显示302,则迭代找寻源文件
        while r.status_code == 302:
            self.url = r.headers['Location']
            print("该url已重定向至{}".format(self.url))
            r = head(self.url)
        self.size = int(r.headers['Content-Length'])
        print('该文件大小为：{} bytes'.format(self.size))

    def down(self, start, end):
        headers = {'Range': 'bytes={}-{}'.format(start, end)}
        # stream = True 下载的数据不会保存在内存中
        r = get(self.url, headers=headers, stream=True)
        # 写入文件对应位置,加入文件锁
        lock.acquire()
        with open(self.name, "rb+") as fp:
            fp.seek(start)
            fp.write(r.content)
            lock.release()
            # 释放锁

    def run(self):
        # 创建一个和要下载文件一样大小的文件
        fp = open(self.name, "wb")
        fp.truncate(self.size)
        fp.close()
        # 启动多线程写文件
        part = self.size // self.num
        pool = ThreadPoolExecutor(max_workers=self.num)
        futures = []
        #print("正在分配块中---")
        #labe1_3.config(text='正在分配块中---', font=('微软雅黑', 20), fg='blue', bg="#FAFAFA")
        for i in range(self.num):
            start = part * i
            # 最后一块
            if i == self.num - 1:
                end = self.size
                # print('{}->{}'.format(start, end))
                #labe1_3.config(text='{}->{}'.format(start, end), font=('微软雅黑', 20), fg='blue', bg="#FAFAFA")
            else:
                end = start + part - 1
                #print('{}->{}'.format(start, end))
                #labe1_3.config(text='{}->{}'.format(start, end), font=('微软雅黑', 20), fg='blue', bg="#FAFAFA")
            futures.append(pool.submit(self.down, start, end))

        #print(futures)
        # print("正在下载，请稍等")
        labe1_3.config(text='正在下载，请稍等', font=('微软雅黑', 20), fg='blue', bg="#FAFAFA")
        begin=time.time()
        wait(futures)
        final = time.time()
        total=final-begin
        # print('{}下载完成,花时{}s'.format(self.name,total))
        labe1_3.config(text='下载完成,花时{}s'.format(total), font=('微软雅黑', 20), fg='blue', bg="#FAFAFA")


def thread_it(func):
    '''将函数打包进线程'''
    # 创建
    t = Thread(target=func)
    # 守护 !!!
    t.setDaemon(True)
    # 启动
    t.start()
    # 阻塞--卡死界面！
    # t.join()
def download():
    url = str(entry_1.get())
    filename = url.rpartition('/')[-1]
    name = entry_2.get() + r"\\" + filename
    s=Downloader(url,6,name)
    s.run()
def get_wen():
    # 使用文件对话框选择文件
    # filedialog.askopenfilenames可以返回多个文件名
    data_1 = tkinter.filedialog.askdirectory(title="选择文件路径")
    data = data_1.replace('/' , r'\\')
    entry_2.delete(0, END)
    entry_2.insert(0, data)


# 布置界面
window = Tk()
window.title("下载软件")
window.geometry("600x265+490+250")
window.config(bg="#FAFAFA")
# 设置窗口是否可以变化长宽,默认可变
window.resizable(width=False, height=False)

labe1_1 = Label(window, text='下载文件: ', font=('微软雅黑', 20), fg='blue', bg="#FAFAFA")
labe1_1.place(x=20, y=20)

labe1_2 = Label(window, text="安装目录:", font=('微软雅黑', 20), fg='blue', bg="#FAFAFA")
labe1_2.place(x=20, y=72)

labe1_3 = Label(window, text="", font=('微软雅黑', 20), fg='blue', bg="#FAFAFA")
labe1_3.place(x=20, y=122)


entry_1 = Entry(window, font=('微软雅黑', 18), width=30, bg='white')
entry_1.place(x=150, y=30)

entry_2 = Entry(window, font=('微软雅黑', 18), width=30, bg='white')
entry_2.place(x=150, y=80)

button_1 = Button(window, text="下载", font=("隶书", 20), bg='Snow', activeforeground='gold', activebackground='green',
                  fg="black", command=lambda :thread_it(download))
button_1.place(x=20, y=200, width=120)

button_2 = Button(window, text="退出", font=("隶书", 20), bg='Snow', activeforeground='gold', activebackground='green',
                  fg="black", command=window.quit)
button_2.place(x=450, y=200, width=120)

button_3 = Button(window, text="...", font=("隶书", 15), bg='Snow', activeforeground='gold', activebackground='green',
                  fg="black", command=get_wen)
button_3.place(x=535, y=80, width=40)


window.mainloop()
