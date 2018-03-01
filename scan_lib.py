import os, sys, time

path = '/mnt/c/Users/Emil_Penchev/Downloads/Books'
# path = 'C:\\Users\\Emil_Penchev\\Downloads\\Books'

out_files = list()
for root, dirs, files in os.walk(path):
    for f in files:
        print(f)
        time.sleep(1)
    break
print('bye')
sys.stdout.flush()

while True:
    time.sleep(10)
