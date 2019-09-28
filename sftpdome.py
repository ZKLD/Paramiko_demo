# -*- coding: utf-8 -*-
from stat import S_ISDIR
import os
from time import time

import paramiko
class FTP(object):
    def __init__(self, ip, username, passwd):#, localpath, removepath, upfilename=None, downfilename=None):
        self.ip = ip
        self.username = username
        self.passwd = passwd
        # self.localpath = localpath
        # self.removepath = removepath
        # self.upfilename = upfilename
        # self.downfilename = downfilename

    #获取文件的大小
    def get_file_size(self, file_path, flag=None):
        file_size = float(os.path.getsize(file_path))
        #将以B,KB,MB,GB的显示方式存储在字典中
        save_file_size = {
            "B": file_size,
            "KB": file_size/1024,
            "MB": file_size/1024/1024,
            "GB": file_size/1024/1024/1024
        }
        return save_file_size[flag]

    def ssh_connect(self, cmdlist):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.ip, 22, username=self.username, password=self.passwd)
        for cmd in cmdlist:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            # output = stdout.read()
            # print output
        ssh.close()

    # localpath,removepath处理,使之变为绝对路径
    def path_replace(self, localpath, removepath):
        if localpath[-1] != '/':
            localpath = localpath.replace('\\', '/') + '/'

        if removepath[-1] != '/':
            removepath = removepath.replace('\\', '/') + '/'

        return localpath, removepath

    def up_dir(self, localpath, removepath):
        localpath, removepath = self.path_replace(localpath, removepath)
        # print("localpath is %s" % localpath)
        all_up_file_dir = {
            "all_dir": list(),
            "all_file": list()
        }
        all_dir_info = os.listdir(localpath)
        for path in all_dir_info:
            newlocalpath = localpath + path
            if os.path.isdir(newlocalpath):
                newremovepath = removepath + path
                #在远程创建对应的文件夹
                # cmd = "mkdir %s" % newremovepath
                # self.ssh_connect(cmdlist=cmd)
                all_up_file_dir['all_dir'].append(newremovepath)
                all_up_file_dir['all_dir'].extend(self.up_dir(localpath=newlocalpath, removepath=newremovepath)['all_dir'])
                all_up_file_dir['all_file'].extend(self.up_dir(localpath=newlocalpath, removepath=newremovepath)['all_file'])
            else:
                all_up_file_dir['all_file'].append(newlocalpath)
        return all_up_file_dir

    def ftp_up(self, localpath, removepath, upfilename=None):
        localpath, removepath = self.path_replace(localpath, removepath)
        cmdlist = self.up_dir(localpath, removepath)['all_dir']
        # print(cmdlist)
        newcmdlist = list()
        for cmd in cmdlist:
            cmd = "mkdir %s" % cmd
            newcmdlist.append(cmd)
        # print(newcmdlist)
        self.ssh_connect(cmdlist=newcmdlist)
        transport = paramiko.Transport((self.ip, 22))
        transport.connect(username=self.username, password=self.passwd)
        sftp = paramiko.SFTPClient.from_transport(transport)
        # print("开始上传")
        if upfilename != None:
            print("开始上传文件")
            # sftp.put(localpath+upfilename, removepath+upfilename)
        else:
            print("开始上传文件夹里的所有文件")
            all_file_dir = self.up_dir(localpath, removepath)
            # print(all_file_dir)
            count = 1
            for file in all_file_dir['all_file']:
                flag = 1
                file_name = file.split('/')[-1]
                # print(file)
                for dir in all_file_dir['all_dir']:
                    if dir.split('/')[-1] == file.split('/')[-2]:
                        upload_file = dir + '/' + file_name
                        print("%s:开始上传%s" % (count, file))
                        sftp.put(file, upload_file)
                        print("%s上传成功" % file)
                        flag = 0
                if flag == 1:
                    print("%s:开始上传%s" % (count, file))
                    sftp.put(file, removepath + file_name)
                    print("%s上传成功" % file)
                count = count + 1
        print("上传成功")
        transport.close()

    def down_dir(self, sftp, removepath, localpath):
        #存放所有文件,和目录信息的字典
        all_file_dir ={
            "all_file": list(),
            "all_dir": list()
        }
        #判断文件夹路径是否以'/'结尾
        localpath, removepath = self.path_replace(localpath, removepath)
        # print(removepath)
        #列出给定路劲removepath中的所有文件的属性和名字
        files = sftp.listdir_attr(removepath)
        #遍历文件夹中的文件
        for i in files:
            filename = removepath + i.filename
            #判读是否为文件夹 需要引入stat模块中的S_ISDIR
            if S_ISDIR(i.st_mode):
                #追加文件到all_file列表中,并在下载的桌面创建对应的文件夹
                newlocalpath = localpath + i.filename
                if os.path.exists(newlocalpath):
                    #print(newlocalpath+u"已存在！")
                    pass
                else:
                    os.mkdir(newlocalpath)
                all_file_dir["all_dir"].append(newlocalpath)
                all_file_dir["all_file"].extend(self.down_dir(sftp, filename, newlocalpath)["all_file"])
                all_file_dir["all_dir"].extend(self.down_dir(sftp, filename, newlocalpath)["all_dir"])
            else:
                all_file_dir["all_file"].append(filename)
        return all_file_dir

    def ftp_down(self, localpath, removepath, downfilename=None):
        dir_size = 0
        localpath, removepath = self.path_replace(localpath, removepath)
        transport = paramiko.Transport((self.ip, 22))
        transport.connect(username=self.username, password=self.passwd)
        sftp = paramiko.SFTPClient.from_transport(transport)
       # print("开始下载")
        if downfilename != None:
            try:
                print("准备下载文件")
                start_time = time()
                sftp.get(removepath+downfilename, localpath+downfilename)
                end_time = time()
                spend_time = end_time - start_time
                print(u"文件%s下载成功" % downfilename)
                print(u"总共%.2fs!" % spend_time)
            except:
                print(u"下载失败！！在%s目录下没有找到文件%s" % (removepath, downfilename))
        else:
            print("准备下载文件夹%s中的文件" % removepath)
            start_time = time()
            allfiles = self.down_dir(sftp, removepath, localpath)
            for i in allfiles["all_file"]:
                try:
                    flag = 1
                    downfilename = i.split('/')[-1]
                    for j in allfiles["all_dir"]:
                        if j.split('/')[-1] == i.split('/')[-2]:
                            downfilename = j + '/' + downfilename
                            sftp.get(i, downfilename)
                            size = self.get_file_size(downfilename, "KB")
                            print(u"文件下载到%s成功,该文件大小为%.3fKB" % (downfilename,size))
                            flag = 0
                            dir_size = dir_size + size
                    if flag == 1:
                        downfilename = localpath + downfilename
                        sftp.get(i, downfilename)
                        size = self.get_file_size(downfilename, "KB")
                        print(u"文件下载到%s成功,该文件大小为%.3fKB" % (downfilename, size))
                        dir_size = dir_size + size
                except:
                    print(u"下载%s失败" % downfilename)
            end_time = time()
            spend_time = end_time - start_time
            print(u"文件夹%s所有文件下载成功,总大小为%.3fKB" % (removepath, dir_size))
            print(u"总共%.2fs!" % spend_time)
        #将sftp.txt下载到本机桌面
        transport.close()

def main():
    username = "root"
    passwd = "lk5115823"
    ip = "192.168.230.132"
    cmdlist = ["ifconfig", "ls /root/Desktop/linuxtest/"]
    #localpath = 'C:\Users\Luke\Desktop\wintest\\test'
    localpath = r"C:\Users\Luke\Desktop\wintest\new"
    removepath = "/root/Desktop/new1"
    #upfilename ="4235"
    #downfilename = "*"
    host = FTP(ip, username, passwd)
   # print "%.3f"%host.get_file_size("G:\CentOS7_6\CentOS-7-x86_64-DVD-1810.iso", "MB")
    # print host.path_replace(localpath, removepath)
    #host.ftp_up(localpath, removepath, upfilename)
    # host.ftp_down(localpath, removepath)#, upfilename)
    host.ftp_up(localpath, removepath)
    # host.ssh_connect(cmdlist)
    # host.up_dir(localpath,removepath)

if __name__ == '__main__':
    main()
