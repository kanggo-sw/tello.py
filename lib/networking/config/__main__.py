import sys

from lib.networking.setup_ap import setup_ap

if __name__ == '__main__':
    if len(sys.argv) < 1:
        print("Setup access point for tello device")
        print("Usage: python -m lib.networking.config SSID PASSWORD")
        sys.exit(1)

    ssid = sys.argv[1]
    pw = sys.argv[2]

    setup_ap(ssid=ssid, password=pw)
    print("Completed.")
