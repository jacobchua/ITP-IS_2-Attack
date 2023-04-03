# ITP-IS_2-Attack

## Description
This github repository consist of files that is used for the exploits of the Smart Meter Network for the ITP IS 2 Hacking a Smart Meter Network. Python is the main language used for the development of the exploits. All the python scripts are compiled into executable files for easy usage. The ReconScript is developed for the purpose of gaining intial information of the Smart Meter PC for the development of exploits and the AttackScript is the exploits used for the Smart Meter PC.

## Installation

These files are developed to be run on the Smart Meter PC. Please use the .exe files that are the compiled files of the python script to execute the attacks. To specify the path of where files are being deleted and copied from, edit line 21. To specify the path of where to copy the files to, edit line 20.

## Usage
Simply double-click or execute ReconScript.exe to run the script to retrieve system information on the Smart Meter PC.

For the execution of AttackScript.exe, parameters are required to specify the attack that the user wishes to run. The list of attack options include:
1. Delete Files
2. Copy Files
3. Disable Firewall
4. Disable SSH
5. Disable KEPServer
6. Interrupt Modbus Reading
7. Disable COMPORT
8. Encrypt Files
9. Change Meter 25 ID to 26
10. Clear Energy Reading
11. Revert with options (-h for list)
12. Bruteforce KEPServer Password

AttackScript.exe also includes options to revert certain attacks that are executed by this script. The list of reverting options include:
1. Enable Firewall
2. Re-Enable SSH
3. Re-Enable KEPServer
4. Re-Enable COM Port
5. Decrypt Encrypted Files
6. Revert Meter 25 ID
7. Stop Modbus interrupt
8. Remove Shared Folder and Scheduled Task
9. Revert All
10. Re-Enable SSHD Service
