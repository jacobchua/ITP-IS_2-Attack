import os
import time

testpath = "" #Add ur own directory to test


#Delete file in specific folder
def delete_files(folder_path):
    while True:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                os.remove(os.path.join(root, file))
        time.sleep(60)


if __name__ == '__main__':
    delete_files(testpath)