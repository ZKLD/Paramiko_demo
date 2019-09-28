#!/usr/bin/python
# -*- coding: utf-8 -*-
import paramiko, getpass, sys, time, os
def mkdir(path):
    isExist = os.path.exists(path)
    if isExist:
        print(path + "已存在！")
    else:
        os.mkdir(path)
        print(path + "已创建成功！")
def ssh_connect(ip,username,passwd,cmdlist):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #print time.time()
        ssh.connect(ip, '22', username, passwd, timeout=5)
        for cmd in cmdlist:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            #stdin.write("nihao")
            outputfile = open("c:/Users/Luke/Desktop/sshlog/%sresult.log"%ip, "a")
            out = stdout.read()
            #for o in out:
            print(time.time())
            print(out)
            print >> outputfile, "the command(%s) result is:"%cmd
            print >> outputfile, out
            outputfile.close()
            #print "接下来将会延时5s执行下一条command"
            #设置延时为了让上一条command执行完成后机器将需要的处理时间。
            #time.sleep(5)
            #sys.stdout = outputfile
        #print '%s\tOK\n' % ip
        ssh.close()
    except:
        print('%s\tError' % (ip))
        print(time.time(), '\n')

#执行程序
def main():
    #cmdlist = ['ifconfig', 'echo hello!', 'df']
    username = "root"
    passwd = "lk5115823"
    #iplist = ["192.168.230.128", "192.168.230.143"]
    print("开始连接。。。")
    path = "c:/Users/Luke/Desktop/sshlog/"
    mkdir(path)
    #处理文本中使用readlines出现换行符的情况的两种方法
    #方法一直接使用open('c:/Users/Luke/Desktop/ips.txt', 'r').read().splitlines()的splitlines方法
    cmdfile = open('c:/Users/Luke/Desktop/cmdlist.txt', 'r')
    ipfile = open('c:/Users/Luke/Desktop/ips.txt', 'r')
    cmdlist = cmdfile.read().splitlines()
    iplist = ipfile.read().splitlines()
    #print iplist
    #方法二利用list中的strip('str')方法,strip是去掉列表中首尾的str
    #iplist = open('c:/Users/Luke/Desktop/ips.txt', 'r').readlines()
    #for i in range(len(iplist)):
    #    print i
    #    iplist[i] = iplist[i].strip()
    print(iplist)
    #询问在每个ip中需要执行cmdlist中cmd的次数
    init_num = input("你想要执行cmdlist里面的cmd多少次？请输入次数:")
    #也可以直接在程序中直接定义需要执行多少次
    #init_num = 5 #执行5次
    init_count = 1
    for ip in iplist:
        print(ip)
        #ip_outputlog = open("c:/Users/Luke/Desktop/sshlog/%sresult.log"%ip, "a")
        #询问在每个ip中需要执行的次数
        #init_num = raw_input("你想要在%s中执行cmdlist里面的cmd多少次？请输入次数:"%ip)
        #count = 1
        num = int(init_num)
        count = init_count
        while num > 0:
            outputfile = open(path+"%sresult.log" % ip, "a")
            print >> outputfile, "第%s次的cmdlist:" % (count)
            print >> outputfile, cmdlist
            print >> outputfile, "第%s次cmd结果:" % (count)
            outputfile.close()
            ssh_connect(ip, username, passwd, cmdlist)
            num = num - 1
            count = count + 1
        #ip_outputlog.close()
    cmdfile.close()
    ipfile.close()
    #print "Can not connect %s" % ip

if __name__ == '__main__':
    main()