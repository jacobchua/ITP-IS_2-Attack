#import os
from os import walk, path, remove
#import time
from time import sleep
import threading
from shutil import copyfile

testpath = "" # Put Original directory (Documents folder)
copiedpath = "" # Put shared directory

#Delet file in specific folder
def delete_files(folder_path):
    while True:
        for root, dirs, files in walk(folder_path):
            for file in files:
                og = path.join(root, file)
                dest = path.join(copiedpath, file)
                remove(og)
        sleep(5)


if __name__ == '__main__':
    delete_files(testpath)