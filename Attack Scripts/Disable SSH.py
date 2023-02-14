from subprocess import run

testpath = "" # Put Original directory (Documents folder)
copiedpath = "" # Put shared directory

def disable_ssh():
    run('netsh advfirewall firewall add rule name="QRadar Test" dir=in action=block protocol=TCP localport=22')
    run('netsh advfirewall firewall add rule name="QRadar Test2" dir=in action=block protocol=UDP localport=22')

if __name__ == '__main__':
    disable_ssh()