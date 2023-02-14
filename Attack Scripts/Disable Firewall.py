from subprocess import run

testpath = "" # Put Original directory (Documents folder)
copiedpath = "" # Put shared directory

#Disable firewall
def disable_firewall():
    run('netsh advfirewall set allprofiles state off', shell=True)

if __name__ == '__main__':
    disable_firewall()