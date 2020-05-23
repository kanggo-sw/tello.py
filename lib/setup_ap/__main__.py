import sys

from lib.networking.setup_ap import setup_ap

if __name__ == '__main__':
    ssid = sys.argv[1]
    pw = sys.argv[2]

    setup_ap(ssid=ssid, password=pw)
    print("Completed.")
