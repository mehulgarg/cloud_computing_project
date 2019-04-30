import urllib.request
import threading
 
def run_check():
    threading.Timer(5.0, run_check).start()
    
    print("HTTP Request sent.")
 
run_check()
print('Hello world')