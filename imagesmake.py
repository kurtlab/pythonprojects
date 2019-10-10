#!/usr/bin/env python3# -*- coding: utf-8 -*-

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


class SearchFrame(BasicFrame):
    """docstring for SearchFrame"""

    def __init__(self, root=None, **args):
        super(SearchFrame, self).__init__(root=root, **args)
        self.entry = tk.StringVar()
        self.cnt = 0
        self.num = tk.StringVar()
        self.num.set(300)
        self.name = 0
        self.flag = False

        row = 0

        tk.Label(self.root, text='----搜索下载图片区域---').grid(row=row, column=1)

        row += 1
        tk.Label(self.root,width=10, justify='right' ,text='关键词').grid(row=row, column=0)
        tk.Entry(self.root, textvariable=self.entry, width=24).grid(row=row, column=1)
        tk.Button(self.root, width=9,text='下载图片', command=self.serach).grid(row=row, column=2)
        tk.Label(self.root, width=30, justify='right' , text='直接输入关键词，调用百度图片').grid(row=row, column=3)

        row += 1
        tk.Label(self.root, width=9, justify='right' , text='爬取量').grid(row=row, column=0)
        self.button = tk.Entry(self.root, textvariable=self.num, width=24).grid(row=row, column=1)

        row += 1

        tk.Label(self.root,   text='---生成图片设置区域---').grid(row=row, column=1)



    @thread_run
    def serach(self):
        _input = self.entry.get().replace(' ', '')
        try:
            num = int(self.num.get())
        except Exception as e:
            num = 0
            print(e)

        if self.flag:
            messagebox.showinfo("警告", "尚有后台下载任务进行中")
        elif _input == '' or num == 0:
            messagebox.showinfo("警告", "关键词或爬取量不能为空")
        else:
            self.entry.set('')
            self.prepare(_input)

    def prepare(self, keywords):
        self.flag = True
        self.keywords = keywords
        self.base_url = 'http://image.baidu.com/search/flip?tn=baiduimage&ie=utf-8&word=' + self.keywords + '&pn='

        path = "%s\\%s" % (os.path.abspath('.'), keywords)
        if not os.path.exists(path):
            os.mkdir(path)

        t = 0
        self.cnt = 0
        fail = 0
        while True:
            if fail > 10:
                if self.flag:
                    self.flag = False
                    messagebox.showinfo("提示", "下载完成，但该词条下无足够数量图片!!!")
                return

            if (self.cnt >= int(self.num.get())):
                if self.flag:
                    self.flag = False
                    messagebox.showinfo("提示", "下载完成")
                return
            try:
                url = self.base_url + str(t)
                result = requests.get(url, timeout=10)
                pic_url = re.findall('"objURL":"(.*?)",', result.text, re.S)
                if len(pic_url) == 0:
                    fail += 1
                else:
                    self.downloadPic(pic_url, path)
            except Exception as e:
                print(e)
                time.sleep(3)
            finally:
                t += 60
                time.sleep(1)

        # print("图片下载完成")

    def downloadPic(self, urls, path):

        # 每过三秒检查一次当前正在运行的线程数，超标则沉睡等待线程结束
        while threading.activeCount() > 200:
            print("线程超标---%s" % threading.activeCount())
            time.sleep(3)

        for url in urls:
            if url:
                self.download(url, path)

    @thread_run
    def download(self, url, path):
        try:
            if lock.acquire():
                if (self.cnt >= int(self.num.get())):
                    lock.release()
                    return
                self.cnt += 1
                self.name += 1
                filename = "%s\\%s_%s.%s" % (path, self.keywords, self.name, url.split('.')[-1])
                lock.release()

                res = requests.get(url, timeout=10)
                with open(filename, 'wb') as f:
                    f.write(res.content)
            # 下载完后检查是否完成下载
            if lock.acquire():
                if (self.cnt >= int(self.num.get())):
                    lock.release()
                    if self.flag:
                        self.flag = False
                        messagebox.showinfo("提示", "下载完成")
                else:
                    lock.release()
        except Exception as e:
            print(e)
            if lock.acquire():
                self.cnt -= 1
                lock.release()


class GenerateFrame(BasicFrame):
    """docstring for GenerateFrame"""

    def __init__(self, root=None, **args):
        super(GenerateFrame, self).__init__(root=root, **args)
        self.path = tk.StringVar()  # 用于保存输入源目录
        # self.path = path  # 用于保存输入源目录
        self.output = tk.StringVar()  # 用于保存输出对象路径
        self.resources = []
        self.orign = None
        self.outim = None
        self.busy = False
        self.load = False

        self.width = tk.StringVar()
        self.row = tk.StringVar()
        self.column = tk.StringVar()
        self.images = []

        self.row.set('60')
        self.column.set('60')
        self.width.set('30')

        row = 0
        tk.Label(self.root,width=10, justify='right' , text='输入源路径').grid(row=row, column=0)
        tk.Entry(self.root, textvariable=self.path, width=24).grid(row=row, column=1)
        tk.Button(self.root, text='载入输入源', command=self.setResource).grid(row=row, column=2)
        tk.Label(self.root,  width=30, justify='right' , text='选择图片来源文件夹').grid(row=row, column=3)


        row += 1
        tk.Label(self.root, width=10, justify='right' ,text='输出源路径').grid(row=row, column=0)
        tk.Entry(self.root, textvariable=self.output, width=24).grid(row=row, column=1)
        tk.Button(self.root, text='选择输出源', command=self.setOrign).grid(row=row, column=2)
        tk.Label(self.root, text='选择要生成的图片源').grid(row=row, column=3)

        row += 1
        tk.Label(self.root, width=10, justify='right' ,text='图片宽度').grid(row=row, column=0)
        tk.Entry(self.root, textvariable=self.width, width=24).grid(row=row, column=1)
        tk.Button(self.root, text='生成图片', command=self.generate).grid(row=row, column=2)
        tk.Label(self.root, text='填充的图片的宽度').grid(row=row, column=3)
        row += 1
        tk.Label(self.root, width=10, justify='right' ,text='图片行数').grid(row=row, column=0)
        tk.Entry(self.root, textvariable=self.row, width=24).grid(row=row, column=1)
        # tk.Button(self.root, text = '保存图片', command = self.saveImg).grid(row=row, column=2)

        row += 1
        tk.Label(self.root, width=10, justify='right' ,text='图片列数').grid(row=row, column=0)
        tk.Entry(self.root, textvariable=self.column, width=24).grid(row=row, column=1)

    @thread_run
    def setResource(self, ):
        try:
            self.load = True
            self.resources = []
            self.path.set(askdirectory(title="载入输入源"))
            self.images = self.getImages(self.path.get())
            for img in self.images:
                self.resources.append(ImageManager(img))
        except Exception as e:
            pass
        finally:
            self.load = False

    @thread_run
    def setOrign(self):
        orign = askopenfilename(title='选择输出源', filetypes=[('jpg', '*.jpg'), ('jpeg', '*.jpeg'), ('png', '*.png')])

        self.output.set(orign)

        self.orign = ImageManager(orign)

    @thread_run
    def generate(self, ):
        if self.load:
            messagebox.showinfo("警告", "图片源加载尚未完成，请等待...")
            return
        if self.busy:
            messagebox.showinfo("警告", "上一个合成任务仍在进行中...")
            return
        try:
            self.busy = True
            width = int(self.column.get())
            height = int(self.row.get())
            length = int(self.width.get())

            self.outim = self.orign.resize((width * length, height * length))
            for i in range(height):
                for j in range(width):
                    manager = ImageManager(
                        im=self.outim.crop((i * length, j * length, (i + 1) * length, (j + 1) * length)))
                    rgion = self.getMin(manager, self.resources)
                    box = (i * length, j * length, (i + 1) * length, (j + 1) * length)
                    self.outim.paste(rgion.resize((length, length)), box)

            self.saveImg()
            messagebox.showinfo("提示", "生成图片成功！！！")

        except Exception as e:
            messagebox.showinfo("提示", "生成图片失败，请重试...")
            print(e)
        finally:
            self.busy = False

    def saveImg(self, ):
        if self.outim:
            self.outim.save('%s.png' % int(time.time()), quality=95)

    def getImages(self, path):
        tmp = []
        for root, dirs, files in os.walk(path):
            if files and len(files) > 0:
                for file in files:
                    if 'jpg' in file or 'jpeg' in file or 'png' in file:
                        tmp.append(root + '/' + file)
            if dirs and len(dirs) > 0:
                for _dir in dirs:
                    tmp += self.getImages(root + '/' + _dir)

        return tmp

    def getMin(self, point, points):
        _min = points[0]
        _mean = point.getMean()
        _dis = math.fabs(_min.getMean() - _mean)
        for p in points:
            if math.fabs(p.getMean() - _mean) < _dis:
                _min = p
                _dis = math.fabs(p.getMean() - _mean)

        return _min


if __name__ == '__main__':
    lock = threading.Lock()
    root = tk.Tk()
    root.title("图片生成器 -- 正则兮")
    root.geometry('640x280+600+200')
    root.resizable(False, False)

    serach = SearchFrame(root)
    serach.grid(0, 0)

    generate = GenerateFrame(root)
    generate.grid(1, 0)

    tk.Label(text="created BY 正则兮").grid(row=2, column=0)

    root.mainloop()