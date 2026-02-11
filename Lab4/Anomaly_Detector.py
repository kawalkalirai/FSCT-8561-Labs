from scapy.all import *

# Scans PCAP and defines the metric we are using to detect for floods

pcap_file = "botnet-capture-20110812-rbot.pcap"
print("Reading file: " + pcap_file)
print("Looking for floods (>20 packets in 5 seconds)...")

# Summary of protocols
tcp_count = 0
udp_count = 0

# Looks at packet times for IPs
ip_window = {}

# Looks at suspicous IPs for no spam
detected_ips = []

# Reads packet
for pkt in PcapReader(pcap_file):
    
    # Compares IP packets
    if IP in pkt:
        src = pkt[IP].src
        now = pkt.time
        
        # Counts TCP/UDP protocol in packets
        if TCP in pkt:
            tcp_count += 1
        elif UDP in pkt:
            udp_count += 1
            
        # Current time window
        if src not in ip_window:
            ip_window[src] = []
        ip_window[src].append(now)
        
        # 5 second sliding window
        time_limit = now - 5
        ip_window[src] = [t for t in ip_window[src] if t > time_limit]
        
        # Alert for more than 20 packets in this 5-second
        if len(ip_window[src]) > 20:
            if src not in detected_ips:
                print(f"ALERT: {src} is flooding! (Sent more than 20 packets in 5s)")
                detected_ips.append(src)

# Final Summary Output
print("\n Scan Finished")
print(f"Total TCP: {tcp_count}")
print(f"Total UDP: {udp_count}")
print(f"Suspicious IPs Found: {len(detected_ips)}")
