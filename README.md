# VTP Attack — Agregar y Borrar VLANs
**Diego Marte | Matrícula: 2023-0316 | ITLA — Seguridad de Redes**

## Objetivo del Laboratorio
Demostrar cómo un atacante puede manipular la base de datos de VLANs de toda una red Cisco inyectando tramas VTP falsas con número de revisión superior al dominio objetivo. Permite agregar VLANs no autorizadas o borrar todas las VLANs existentes, causando interrupción total del tráfico.

## Topología
```
Internet
    |
Router (Fa0/0: 20.23.3.1)
    |
SW-L2  Gig0/0 -> Router
       Gig0/1 -> Kali Linux 20.23.3.16  [ATACANTE]
       Gig0/2 -> PC-Victima 20.23.3.50
       Gig0/3 -> SW-CORE 20.23.3.2    [VTP Server]
           SW-CORE Gig0/1 -> SW-ACC-1 20.23.3.3  [VTP Client]
           SW-CORE Gig0/2 -> SW-ACC-2 20.23.3.4  [VTP Client]
```

## Uso
```bash
# Agregar VLANs
sudo python3 vtp_attack.py -a agregar --vlans 100:VLAN-HACK 200:VLAN-INTRUSO

# Borrar todas las VLANs
sudo python3 vtp_attack.py -a borrar
```

## Parámetros
| Parámetro | Default | Descripción |
|---|---|---|
| -i | eth0 | Interfaz de red |
| -d | LAB-2023-0316 | Dominio VTP |
| -r | 127 | Número de revisión |
| -a | requerido | agregar \| borrar |
| --vlans | 100:VLAN-ATAQUE | VLANs a inyectar (ID:NOMBRE) |

## Requisitos
```bash
pip install scapy
sudo python3 vtp_attack.py [opciones]
```

## Contra-medidas
| Medida | Comando Cisco |
|---|---|
| VTP Transparent | `vtp mode transparent` |
| VTP Off | `vtp mode off` |
| Contraseña VTP | `vtp password Secreto secret` |
| VTP v3 | `vtp version 3` |

---
*Laboratorio académico | ITLA | Matrícula: 2023-0316*
