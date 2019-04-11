import os
import time
import subprocess

def check(file):
    f = open(file,'a+')
    f.close()
    f_pid = open('pid.txt','a')

    init_time = os.path.getmtime(file)
    cmd = r"python C:\Users\Houking\Desktop\downloader\dblp\downloader.py"
    sub = subprocess.Popen(cmd)
    f_pid.write('%d\n' % sub.pid)
    f_pid.flush()

    while True:
        start_time = os.path.getmtime(file)
        if sub.stdout:
            print(sub.stdout.readlines())
        timeout = 60
        while timeout>0:
            time.sleep(1)
            timeout-=1
        if os.path.getmtime(file)==start_time:
            if os.path.getmtime(file)-init_time>1800:
                print("All have been downloaded!")
                sub.kill()
                break

            print("########## restart downloading #########")
            init_time = os.path.getmtime(file)
            sub.kill()
            sub = subprocess.Popen(cmd)
            f_pid.write('%d\n' % sub.pid)
            f_pid.flush()
    f_pid.close()

if __name__=="__main__":
    check('pdf.txt')