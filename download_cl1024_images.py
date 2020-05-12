#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askdirectory, askopenfilename
import threading, time, re, os, requests, math
from PIL import Image, ImageStat

def thread_run(func):
    def wraper(*args, **kwargs):
        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()

    return wraper


class ImageManager():
    def __init__(self, file=None, io=None, im=None):
        self.mean = None
        self.im = None
        self.path = None

        if file:
            if not os.path.exists(file):
                raise Exception("文件不存在的!")

            self.path = file
            self.im = Image.open(file)
        if im:
            self.im = im

    def getMean(self):
        if not self.mean:
            self.mean = ImageStat.Stat(self.im.convert('L')).mean[0]

        return self.mean

    def resize(self, size=(1, 1)):
        return self.im.resize(size, Image.ANTIALIAS)
        # return self.im.resize(size)


class BasicFrame(object):
    """Frame基类，实现grid方法"""

    def __init__(self, root=None, **args):
        super(BasicFrame, self).__init__()
        self.root = None
        if root:
            self.root = tk.Frame(root)
        if args and 'root' in args.keys:
            self.root = tk.Frame(args.root)

        if not self.root:
            raise Exception("no root")

    def grid(self, row='default', column='default', **args):
        if row == 'default' or column == 'default':
            if args:
                self.root.grid(**args)
        else:
            self.root.grid(row=row, column=column)


class DownloadFrame(BasicFrame):
    """docstring for SearchFrame"""

    def __init__(self, root=None, **args):
        super(DownloadFrame, self).__init__(root=root, **args)
        self.entry = tk.StringVar()
        self.cnt = 0
        self.num = tk.StringVar()
        self.num.set(300)
        self.name = 0
        self.flag = False

        row = 0

        tk.Label(self.root, text='----请输入要下载的免翻地址---').grid(row=row, column=1)

        row += 1
        tk.Label(self.root,width=10, justify='right' ,text='地址').grid(row=row, column=0)
        tk.Entry(self.root, textvariable=self.entry, width=24).grid(row=row, column=1)
        tk.Button(self.root, width=9,text='下载图片', command=self.downloadnow).grid(row=row, column=2)


        row += 1

        tk.Label(self.root,   text='---代理功能更新中---').grid(row=row, column=1)



    @thread_run
    def downloadnow(self):
        _input = self.entry.get().replace(' ', '')

        if self.flag:
            messagebox.showinfo("警告", "尚有后台下载任务进行中")
        elif _input == ''  :
            messagebox.showinfo("警告", "链接不能为空")
        else:
            self.entry.set('')
            self.prepare(_input)

    def prepare(self, downloadlinks):
        self.flag = True
        self.downloadlinks = downloadlinks
        self.base_url =   self.downloadlinks

        fail = 0

        try:
            url = self.base_url
            result = requests.get(url, timeout=10)
            result.encoding = 'gbk'
            # pic_url = re.findall('"objURL":"(.*?)",', result.text, re.S)
            pic_url = re.findall("data-src='(.*?)'", result.text, re.S)

            if pic_url:
                pic_url
                print(pic_url)
            else:
                pic_url = re.findall("ess-data='(.*?)'", result.text, re.S)
                print(pic_url)
            titles = re.findall('<h4>(.+)</h4>',  result.text)
            print(titles)
            title = titles[0]
            print(title)
            path = "%s\\%s" % (os.path.abspath('.'), title)
            if not os.path.exists(path):
                os.mkdir(path)

            if len(pic_url) == 0:
                fail += 1
            else:
                self.downloadPic(pic_url, path)
        except Exception as e:
            print(e)
            time.sleep(3)


        # print("图片下载完成")

    def downloadPic(self, urls, path):

        # 每过三秒检查一次当前正在运行的线程数，超标则沉睡等待线程结束
        while threading.activeCount() > 5:
            print("线程超标---%s" % threading.activeCount())
            time.sleep(3)

        for url in urls:
            if url:
                print(url)
                self.download(url, path)


    @thread_run
    def download(self, url, path):
        try:
            if lock.acquire():
                self.name += 1
                filename = "%s\\%s.%s" % (path, self.name, url.split('.')[-1])
                lock.release()
                header = {
                            "accept-ranges":"bytes",
                            "age":"8585",
                            "cache-control":"public, max-age=31536000",
                            "cf-cache-status":"HIT",
                            "content-length":"729911",
                            "content-type":"image/jpeg",
                            "server":"cloudflare",
                            "status":"200",
                            "vary":"Accept-Encoding"}
                print('start down load images')
                print(url)
                print(filename)
                # res = requests.get(url,  headers=header  )
                res = requests.get(url  )
                with open(filename, 'wb') as f:
                    f.write(res.content)
            # 下载完后检查是否完成下载
            if lock.acquire():
                  if self.flag:
                    self.flag = False
                    messagebox.showinfo("提示", "下载完成")

        except Exception as e:
            print(e)
            if lock.acquire():
                self.cnt -= 1
                lock.release()



if __name__ == '__main__':
    lock = threading.Lock()
    root = tk.Tk()
    root.title("社区图片下载器[社区定制] -- 正则兮")
    root.geometry('440x150+600+200')
    root.resizable(False, False)

    downloadnow = DownloadFrame(root)
    downloadnow.grid(0, 0)


    tk.Label(text="created BY 正则兮").grid(row=2, column=0)

    root.mainloop()