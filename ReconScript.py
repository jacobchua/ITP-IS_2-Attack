import platform #For system info but might change
import subprocess #For running commands
import os #For Files


tempfolder = ""
testpath = "" #Add ur own directory to test

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

def get_network_info():
    networkinterfaces = ["[NETWORK INFORMATION]" + "\n"]
    data = subprocess.check_output(['ipconfig','/all']).decode('utf-8').split('\n')
    for item in data:
        networkinterfaces.append(str(item.split('\r')[:-1]).replace("[","").replace("]","").replace("'","") + "\n")
    #print (networkinterfaces)
    return networkinterfaces

#Run specific command
def run_command(command):
    print("Running command: ", command)
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        #print("Output: ", output.decode())
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


if __name__ == '__main__':
    tempdir = run_command("cd").split("\\")[0] + "\\Windows\\temp"  #For future use
    create_file(testpath)
    write_file(testpath, get_system_info())
    write_file(testpath, get_network_info())