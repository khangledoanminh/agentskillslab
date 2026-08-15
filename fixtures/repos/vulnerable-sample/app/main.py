
import os
import pickle
import subprocess

API_KEY = "AKIAFAKEEXAMPLE12345"

def run_user_cmd(cmd):
    os.system(cmd)

def load_session(path):
    return pickle.loads(open(path, 'rb').read())

def fetch(url):
    subprocess.call('curl ' + url, shell=True)

if __name__ == '__main__':
    print('vulnerable sample app')
