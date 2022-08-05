from audioop import add
import Crypto
from sm4 import SM4Key
from PySide2.QtWidgets import *
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile,QThread
from Crypto.Cipher import AES
import hashlib
#import tkinter.filedialog
import os,sys
#import time,_thread
# 添加ui文件,main window
def md5(a_Str):
    a=hashlib.md5()
    a.update(a_Str.encode())
    return a.digest()
#加密使用的线程
class encryThread(QThread):
    def __init__(self):
        super().__init__()
    def run(self):
        click_Toencry_Thread()
def encry_thread():
    #启动加密的线程的函数
    aa=encryThread()
    aa.run()
class decryThread(QThread):
    def __init__(self):
        super().__init__()
    def run(self):
        click_Todecry_Thread()
def decry_thread():
    #启动解密的线程的函数
    aa=decryThread()
    aa.run()
class Mw():
    def __init__(self):
        qfile = QFile("./ui/main.ui")
        qfile.open(QFile.ReadOnly)
        qfile.close()
        self.window = QUiLoader().load(qfile)
        self.window.progressBar.setMinimum(0)
        self.window.progressBar.setMaximum(100)#默认100吧
        self.window.progressBar.setValue(0)
        def empty_Text():
            #清空消息
            self.window.progressBar.setValue(0)
            self.window.text_show.clear()
        def click_Exit():
            sys.exit()
        self.window.encry_button.clicked.connect(encry_thread)#加密
        self.window.decry_button.clicked.connect(decry_thread)#解密
        self.window.exit_button.clicked.connect(click_Exit)#退出
        self.window.empty_button.clicked.connect(empty_Text)#清空消息
    #Qt窗口的接口
    def get_input_text(self):
        #获取设置文件名的接口
        return self.window.setting.text()
    def get_Password(self):
        #获取写入的密码
        return self.window.password_input.text()
    def set_ProgressBar_value(self,num):
        self.window.progressBar.setValue(num)
    def show_Text(self,message):
        #展示输出函数
        self.window.text_show.insertPlainText(message+'\n')
    def set_ProgressBar_Max(self,max):
        #设定进度条最大值接口，max是整数
        self.window.progressBar.setMaximum(max)
    def get_AES_Checked(self):
        return self.window.AES_Check.isChecked()

app = QApplication([])
a=Mw()
a.window.show()
#加密的线程
def click_Toencry_Thread(**args):
        #读取16，加密，然后write
        AES_Checked=a.get_AES_Checked()
        password=a.get_Password()#获取输入的密码
        if(len(password)==0):
            a.show_Text("请先输入密码")
            return -1
        password=md5(password)
        input=QFileDialog.getOpenFileName()[0]
        if(input==''):#用户取消
            return 0
        #获取文件的名字
        filenamesplit=os.path.split(input)
        filename=filenamesplit[1]
        #获取/设定输出文件的名字
        outputFileName = a.get_input_text()
        if outputFileName!='':
            outputFileName=a.get_input_text()+".encry"
        else:
            outputFileName=filename+".encry"
        save_file=open(filenamesplit[0]+"/"+outputFileName,"wb")#保存文件的路径
        if(AES_Checked):
            cipher=AES.new(password,AES.MODE_ECB)#ECB不需要向量
        else:
            cipher=SM4Key(password)#SM4默认ECB模式,这里不使用ECB模式
        spliteSize=1024*1024#文件分片大小，默认1024*1024,最大1MB,最后一个设定16bytes
        #读取文件16进制
        encring_file=open(input,'rb')
        filesize=os.path.getsize(input)#获取文件长度，bytes
        ite_1MB=filesize//spliteSize#获得1024*1024分片的迭代次数
        ite_16bytes=(filesize%spliteSize)//16#获得16分片的迭代次数
        sum_ite=ite_16bytes+ite_1MB#总的迭代次数，用于显示进度条
        a.set_ProgressBar_Max(sum_ite+1)#设定进度条最大值

        addDataLeng=16-(filesize%16)
        #addData=(16-(filesize%16))*b'\0'#要添加到后面的数据
        #addDataLeng=len(addData) #这里使用PKCS5 padding 后面添加N个N
        if(addDataLeng==16):
            addData=16*b'\f'
        else:
            addData=hex(addDataLeng)[2:] #去掉0x
            addData='0'+addData
            addData=bytes.fromhex(addData)
            addData=addData*addDataLeng #这里使用PKCS5 padding 后面添加N个N
        #print(addData)

        progressBarValue=0
        #先迭代前面的数据，大于1MB的数据
        for i in range(0,ite_1MB):
            one_encry_chars=encring_file.read(spliteSize)#一次加密读取的数据
            encrypted_content=cipher.encrypt(one_encry_chars)
            save_file.write(encrypted_content)#写入一次的数据
            a.set_ProgressBar_value(progressBarValue)
            progressBarValue+=1
        for i in range(0,ite_16bytes):
            one_encry_chars=encring_file.read(16)#一次加密读取的数据
            encrypted_content=cipher.encrypt(one_encry_chars)
            save_file.write(encrypted_content)#写入一次的数据
            progressBarValue+=1
            a.set_ProgressBar_value(progressBarValue)
        one_encry_chars=encring_file.read(16)#最后一次读取，可能是0，但仍加addData
        one_encry_chars+=addData
        encrypted_content=cipher.encrypt(one_encry_chars)
        save_file.write(encrypted_content)#写入最后一次的数据
        a.set_ProgressBar_value(progressBarValue+1)#进度条100%
        a.show_Text("加密成功，文件保存在"+filenamesplit[0]+"/"+outputFileName)  

#解密的线程
def click_Todecry_Thread(**args):
        AES_Checked=a.get_AES_Checked()
        #一边读取，解密，然后write
        password=a.get_Password()#获取输入的密码
        if(len(password)==0):
            a.show_Text("请先输入密码")
            return -1
        password=md5(password)
        #input=tkinter.filedialog.askopenfilename()#完整的路径
        input=QFileDialog.getOpenFileName()[0]
        if(input==''):
            #用户取消
            return 0
        print(input)
        #获取文件的名字
        filenamesplit=os.path.split(input)
        filename=filenamesplit[1]
        #获取/设定输出文件的名字
        outputFileName=filename[:-6]
        save_file=open(filenamesplit[0]+"/decriedfile_"+outputFileName,"wb")#保存文件的路径
        if(AES_Checked):
            cipher=AES.new(password,AES.MODE_ECB)#ECB不需要向量
        else:
            cipher=SM4Key(password)
        spliteSize=1024*1024#文件分片大小，默认1024*1024
        #读取文件16进制
        decring_file=open(input,'rb')
        filesize=os.path.getsize(input)#获取文件长度，bytes

        ite_1MB=filesize//spliteSize#获得1024*1024分片的迭代次数
        if(ite_1MB>0):
            #当1MB迭代次数大于1时,减去一个，防止加密时padding之后刚好为1MB的倍数。
            ite_1MB-=1

        ite_16bytes=(filesize%spliteSize)//16#获得16分片的迭代次数
        sum_ite=ite_16bytes+ite_1MB#总的迭代次数，用于显示进度条
        a.set_ProgressBar_Max(sum_ite+1)#设定进度条最大值
        progressBarValue=0
        #先迭代前面的数据，大于1MB的数据
        for i in range(0,ite_1MB):
            one_encry_chars=decring_file.read(spliteSize)#一次加密读取的数据
            encrypted_content=cipher.decrypt(one_encry_chars)
            save_file.write(encrypted_content)#写入一次的数据
            a.set_ProgressBar_value(progressBarValue)
            progressBarValue+=1
        
        for i in range(0,ite_16bytes-1):
            #这个循环必进
            one_encry_chars=decring_file.read(16)#一次加密读取的数据
            encrypted_content=cipher.decrypt(one_encry_chars)
            save_file.write(encrypted_content)#写入一次的数据
            progressBarValue+=1
            a.set_ProgressBar_value(progressBarValue)
        #对最后一行进行特殊处理，因为这里有padding
        one_encry_chars=decring_file.read(16)#一次加密读取的数据
        encrypted_content=cipher.decrypt(one_encry_chars)
        subdataLeng=encrypted_content[15] #要减去的字节个数，看最后一个字节是什么（PKCS5 padding）
        encrypted_content=encrypted_content[:16-subdataLeng]
        save_file.write(encrypted_content)#写入一次的数据
        progressBarValue+=1
        a.set_ProgressBar_value(progressBarValue)
        a.set_ProgressBar_value(progressBarValue+1)#进度条100%
        a.show_Text("解密成功，文件保存在"+filenamesplit[0]+"/decriedfile_"+outputFileName)


app.exec_() #暂停
