import os
import sys
import time
import joblib
from collections import defaultdict
from scapy.all import sniff, IP, TCP
import numpy as np
from tensorflow.keras.models import load_model

# Modeli ve LabelEncoder'ları yükle
model = load_model('model_test.h5')
label_encoders = joblib.load('label_encoders.joblib')



# Read IPs from a file
def read_ip_file(filename):
    with open(filename, "r") as file:
        ips = [line.strip() for line in file]
    return set(ips)

# Check for Nimda worm signature
def is_nimda_worm(packet):
    if packet.haslayer(TCP) and packet[TCP].dport == 80:
        payload = packet[TCP].payload
        return "GET /scripts/root.exe" in str(payload)
    return False

# Log events to a file
def log_event(message):
    log_folder = "logs"
    os.makedirs(log_folder, exist_ok=True)
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    log_file = os.path.join(log_folder, f"log_{timestamp}.txt")
    
    with open(log_file, "a") as file:
        file.write(f"{message}\n")

def packet_callback(packet):
    src_ip = packet[IP].src    	
    proto = packet[IP].proto    
    
    if packet.haslayer(TCP):
        src_port = packet[TCP].sport
       # print(f"Source IP: {src_ip}, Source Port: {src_port}, Source Protocol: {proto}")
    

    # Check if IP is in the whitelist
    if src_ip in whitelist_ips:
        return

    # Check if IP is in the blacklist
    if src_ip in blacklist_ips:
        os.system(f"iptables -A INPUT -s {src_ip} -j DROP")
        log_event(f"Blocking blacklisted IP: {src_ip}")
        return
    
    # Check for Nimda worm signature
    if is_nimda_worm(packet):
        print(f"Blocking Nimda source IP: {src_ip}")
        os.system(f"iptables -A INPUT -s {src_ip} -j DROP")
        log_event(f"Blocking Nimda source IP: {src_ip}")
        return

    packet_count[src_ip] += 1

    current_time = time.time()
    time_interval = current_time - start_time[0]

    if time_interval >= 1:
        for ip, count in packet_count.items():
            packet_rate = count / time_interval

            # Yapay zeka tarafından karar verme
            X = np.array([[proto, packet_rate]])
            prediction = ( model.predict ( X , verbose=0 ) > 0.5 ).astype("int32")
            prediction = prediction[0][0]
            
            if prediction == 1 and ip not in blocked_ips:
                print(f"Blocking IP: {ip}, packet rate: {packet_rate}")
                os.system(f"iptables -A INPUT -s {ip} -j DROP")
                log_event(f"Blocking IP: {ip}, packet rate: {packet_rate}")
                blocked_ips.add(ip)
                
                # Append the blocked IP to the blacklist file
                with open("blacklist.txt", "a") as blacklist_file:
                    blacklist_file.write(f"{ip}\n")

        packet_count.clear()
        start_time[0] = current_time

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("This script requires root privileges.")
        sys.exit(1)

    # Import whitelist and blacklist IPs
    whitelist_ips = read_ip_file("whitelist.txt")
    blacklist_ips = read_ip_file("blacklist.txt")

    packet_count = defaultdict(int)
    start_time = [time.time()]
    blocked_ips = set()

    print("Monitoring network traffic...")
    sniff(filter="ip", prn=packet_callback)
