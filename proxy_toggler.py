import socket
import psutil
import winreg as wrg
import ctypes
import requests
import base64
import time
import threading
import getpass
import configparser
import sys
import os

status_lock = threading.Lock()
proxy_status = 0

url = "http://ironport3.iiita.ac.in/B0001D0000N0000N0000F0000S0000R0004/"
uname = ''
pwd = ''

def get_ip():
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    for name, addr_list in addrs.items():
        if name in stats and stats[name].isup and "WSL" not in name and "Virtual" not in name and "VirtualBox" not in name:
            for addr in addr_list:
                if addr.family == socket.AF_INET:
                    if addr.address.startswith('172'):
                        return addr.address 
    return None

def auth():
    global proxy_status, url, uname, pwd
    while True:
        ip = get_ip()
        with status_lock:
            if proxy_status == 1 and ip:
                b64_encoded = base64.b64encode(f"{uname}:{pwd}".encode("utf-8")).decode("utf-8")
                headers = {
                    "User-Agent": "Mozilla/5.0",
                    "Authorization": f"Basic {b64_encoded}",
                    "Accept": "*/*",
                    "Connection": "keep-alive",
                }

                session = requests.Session()
                session.headers.update(headers)

                try:
                    res = session.get(f"{url}{ip}/http://fixwifi.it/", timeout=5, allow_redirects=True)
                    print("Final URL:", res.url)
                    print("Status code:", res.status_code)
                    if res.status_code == 200:
                        print("AUTH OK\n")
                    else:
                        print("Not authenticated\n")
                except Exception as e:
                    print("Exception during auth:", e)
        time.sleep(300)

def enable_proxy(ip):
    key = wrg.OpenKey(
        wrg.HKEY_CURRENT_USER, 
        r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
        0,
        wrg.KEY_ALL_ACCESS
    )
    wrg.SetValueEx(key, "ProxyEnable", 0, wrg.REG_DWORD, 1)
    wrg.SetValueEx(key, "ProxyServer", 0, wrg.REG_SZ, "172.31.2.3:8080")
    wrg.CloseKey(key)
    ctypes.windll.Wininet.InternetSetOptionW(0, 39, 0, 0)
    ctypes.windll.Wininet.InternetSetOptionW(0, 37, 0, 0)
    ip = get_ip()
    with status_lock:
        if ip:
            b64_encoded = base64.b64encode(f"{uname}:{pwd}".encode("utf-8")).decode("utf-8")
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Authorization": f"Basic {b64_encoded}",
                "Accept": "*/*",
                "Connection": "keep-alive",
            }

            session = requests.Session()
            session.headers.update(headers)

            try:
                res = session.get(f"{url}{ip}/http://fixwifi.it/", timeout=5, allow_redirects=True)
                print("Final URL:", res.url)
                print("Status code:", res.status_code)
                if res.status_code == 200:
                    print("AUTH OK\n")
                else:
                    print("Not authenticated\n")
            except Exception as e:
                print("Exception during auth:", e)

def disable_proxy():
    key = wrg.OpenKey(
        wrg.HKEY_CURRENT_USER, 
        r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
        0,
        wrg.KEY_ALL_ACCESS
    )
    wrg.SetValueEx(key, "ProxyEnable", 0, wrg.REG_DWORD, 0)
    wrg.CloseKey(key)
    ctypes.windll.Wininet.InternetSetOptionW(0, 39, 0, 0)
    ctypes.windll.Wininet.InternetSetOptionW(0, 37, 0, 0)

def theyCallMeSuperman():
    global proxy_status, url, uname, pwd
    ip = get_ip()
    if ip:
        enable_proxy(ip)
        with status_lock:
            proxy_status = 1
    else:
        disable_proxy()
        proxy_status = 0
        print("Proxy deactivated!")

def add_to_startup():
    exe_path = os.path.realpath(sys.argv[0])
    reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = wrg.OpenKey(wrg.HKEY_CURRENT_USER, reg_path, 0, wrg.KEY_SET_VALUE)
        wrg.SetValueEx(key, "ProxyToggler", 0, wrg.REG_SZ, exe_path)
        wrg.CloseKey(key)
        print("Added to startup!")
    except Exception as e:
        print("Failed to add to startup:", e)

def is_in_startup():
    exe_path = os.path.realpath(sys.argv[0])
    reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = wrg.OpenKey(wrg.HKEY_CURRENT_USER, reg_path, 0, wrg.KEY_READ)
        val, _ = wrg.QueryValueEx(key, "ProxyToggler")
        wrg.CloseKey(key)
        return val == exe_path
    except:
        return False

if __name__ == "__main__":
    config = configparser.ConfigParser()

    try:
        config.read(r'C:\ProxyToggler\config.ini')
        uname = config["creds"]['uname']
        pwd = config["creds"]['pwd']

        if not uname or not pwd:
            sys.exit(1)
    except:
        uname = input('Enrolment No.: ')
        pwd = getpass.getpass('Password: ')

        if not uname or not pwd:
            sys.exit(1)

        config['creds'] = {
            "uname": uname,
            "pwd": pwd
        }

        folder = r"C:\ProxyToggler"
        config_file = os.path.join(folder, "config.ini")

        if not os.path.exists(folder):
            os.makedirs(folder)

        with open(config_file, 'w') as configfile:
            config.write(configfile)

    if not is_in_startup():
        add_to_startup()

    prev_ip = get_ip()
    print(f"IP: {prev_ip}")
    theyCallMeSuperman()

    auth_thread = threading.Thread(target=auth, daemon=True)
    auth_thread.start()

    while True:
        ip = get_ip()
        if prev_ip != ip:
            print(f"IP Changed: {ip}")
            theyCallMeSuperman()
            prev_ip = ip
        time.sleep(3)
