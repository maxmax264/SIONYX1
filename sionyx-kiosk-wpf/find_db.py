import subprocess
result = subprocess.run(['python', '-c', '''
import sqlite3, os, glob
paths = glob.glob(r"C:\Users\*\AppData\Local\SionyxKiosk\*.db")
for p in paths:
    print(p)
'''], capture_output=True, text=True)
print(result.stdout)
