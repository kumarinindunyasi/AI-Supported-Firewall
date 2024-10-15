import sys
import time
from scapy.all import Ether, IP, TCP, sendp

hedef_ip = "192.168.145.133"  # Hedef IP adresi ile değiştirin
arayuz= "eth0"  # Ağ arayüzünüz ile değiştirin
paket_sayisi = 100
sure = 5

def paket_gonder(hedef_ip, arayuz, paket_sayisi, sure):
    paket = Ether() / IP(dst=hedef_ip) / TCP()
    bitis_zamani = time.time() + sure
    gonderilen_paket_sayisi = 0

    while time.time() < bitis_zamani and gonderilen_paket_sayisi < paket_sayisi:
        sendp(paket, iface=arayuz)
        gonderilen_paket_sayisi += 1

if __name__ == "__main__":
    if sys.version_info[0] < 3:
        print("Bu betik Python 3 gerektirir.")
        sys.exit(1)

    paket_gonder(hedef_ip, arayuz, paket_sayisi, sure)
