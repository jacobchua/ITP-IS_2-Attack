import platform #For system info but might change
import subprocess #For running commands
import os #For Files


filename = r"C:\Windows\temp\Smartmeter\smartmeterinfo.txt" #Add ur own directory to test
folder_path = r'C:\Windows\temp\Smartmeter'

#Return list of system info
def get_system_info():
    systeminfo = ["[SYSTEM INFORMATION]" + "\n"]
    systeminfo.append("System: " + platform.system() + "\n")
    systeminfo.append("Node Name: " + platform.node() + "\n")
    systeminfo.append("Release: " + platform.release() + "\n")
    systeminfo.append("Version: " + platform.version() + "\n")
    systeminfo.append("Machine: " + platform.machine() + "\n")
    systeminfo.append("Processor: " + platform.processor() + "\n")
    return systeminfo

#Return list of network information
def get_network_info():
    networkinterfaces = ["[NETWORK INFORMATION]" + "\n"]
    data = subprocess.check_output(['ipconfig','/all']).decode('utf-8').split('\n')
    for item in data:
        networkinterfaces.append(str(item.split('\r')[:-1]).replace("[","").replace("]","").replace("'","") + "\n")
    return networkinterfaces

#Store running services in given file
def store_running_services(path):
    command = "wmic service where state='running' get name, displayname, startmode, state"
    output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
    with open(path, "a") as f:
        f.write("[RUNNING SERVICES]" + "\n")
        f.write(output.decode())

#Store shared foldes in given file
def store_shared_folders(path):
    command = "net share"
    output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
    with open(path, "a") as f:
        f.write(output.decode())
        
#Run specific command
def run_command(command):
    print("Running command: ", command)
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        print("Output: ", output.decode())
        return output.decode()
    except subprocess.CalledProcessError as e:
        print("Command failed with error code: ", e.returncode)

#Create file with path if does not exist
def create_file(path):
    if(not os.path.exists(path)):
        file = open(path , "x")
        file.close
    return 0

#Write into a file with a list
def write_file(path, infolist):
    file = open(path, "a")
    for x in infolist:
        file.write(x)
    file.close()

def read_file(path):
    f = open(path, 'r')
    file_contents = f.read()
    print(file_contents)
    f.close

if __name__ == '__main__':
    try:
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        create_file(filename)
        write_file(filename, get_system_info())
        write_file(filename, get_network_info())
        store_running_services(filename)
        store_shared_folders(filename)
        print("Recon Done.\nOk.")
    except Exception as e:
        print("Recon Fail.\nFail.")
