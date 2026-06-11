# VTP Attack Tool - Matricula: 2023-0316 | ITLA

## Objetivo del Laboratorio
Demostrar el ataque VTP Spoofing para agregar y borrar VLANs en switches Cisco.

## Requisitos
- Linux (Kali Linux)
- - Python 3.8+
  - - `pip install scapy`
    - - Privilegios root/sudo
      - - Interfaz en modo trunk
       
        - ## Uso
        - ```bash
          # Agregar VLANs
          sudo python3 vtp_attack.py -i eth0 -d LAB-2023-0316 -r 127 -a agregar --vlans 100:VLAN-ATAQUE

          # Borrar VLANs
          sudo python3 vtp_attack.py -i eth0 -d LAB-2023-0316 -r 127 -a borrar
          ```

          ## Topologia (Matricula: 2023-0316)
          ```
          Red: 20.23.3.0/24
          Atacante: 20.23.3.16 (Kali Linux)
          SW-CORE:  20.23.3.1 (VTP Server)
          SW-ACC-1: 20.23.3.2 (VTP Client)
          SW-ACC-2: 20.23.3.3 (VTP Client)

          VLAN 10 - Administracion  20.23.3.0/27
          VLAN 20 - Usuarios        20.23.3.32/27
          VLAN 30 - Servidores      20.23.3.64/27
          VLAN 99 - Management      20.23.3.96/28
          ```

          ## Contramediadas
          1. `vtp mode transparent` - Mas efectivo
          2. 2. `vtp password <secreto> secret` - Autenticacion
             3. 3. VTP Version 3 con Primary Server
                4. 4. Port Security en interfaces de acceso
                  
                   5. ## Ver documentacion completa en el archivo README_COMPLETO.md
