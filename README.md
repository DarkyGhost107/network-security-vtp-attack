# VTP Attack Tool — Matricula: 2023-0316 | ITLA

## Topologia (comun a los 3 ataques)

```
Internet (8.8.8.8)
    |
Router Fa0/0: 20.23.3.1 (GW) --- Fa0/1
    |
SW-L2  Gig0/0: router
       Gig0/1: Kali 20.23.3.16 [ATACANTE]
       Gig0/2: Victima 20.23.3.50
       Gig0/3: SW-CORE 20.23.3.2 [VTP Server]
                   |
             Gig0/1  Gig0/2
               |        |
          SW-ACC-1  SW-ACC-2
          20.23.3.3  20.23.3.4
          VLAN20     VLAN30
```

### Interfaces SW-L2
| Puerto | Modo | Conectado a |
|---|---|---|
| Gig0/0 | access | Router Fa0/1 |
| Gig0/1 | access | Kali eth0 (20.23.3.16) |
| Gig0/2 | access | PC-Victima (20.23.3.50) |
| Gig0/3 | trunk  | SW-CORE Gig0/0 |

### Interfaces SW-CORE (VTP Server)
| Puerto | Modo | Conectado a |
|---|---|---|
| Gig0/0 | trunk | SW-L2 Gig0/3 |
| Gig0/1 | trunk | SW-ACC-1 Gig0/0 |
| Gig0/2 | trunk | SW-ACC-2 Gig0/0 |

### VLANs
| VLAN | Nombre | Red |
|---|---|---|
| 10 | Administracion | 20.23.3.0/28 |
| 20 | Usuarios | 20.23.3.16/28 |
| 30 | Servidores | 20.23.3.32/28 |
| 99 | Management | 20.23.3.48/28 |

---

## Objetivo del Script

vtp_attack.py construye tramas VTP (LLC/SNAP + Summary + Subset) enviadas a 01:00:0C:CC:CC:CC. Con revision mayor al dominio, todos los switches aceptan la nueva DB.

Ruta: Kali eth0 → SW-L2 Gig0/1 → SW-L2 Gig0/3 → SW-CORE → SW-ACC-1/2

---

## Requisitos

```bash
pip install scapy
sudo / root
Kali conectada a SW-L2 Gig0/1
```

---

## Parametros

| Parametro | Default | Descripcion |
|---|---|---|
| -i | eth0 | Interfaz |
| -d | LAB-2023-0316 | Dominio VTP |
| -r | 127 | Numero revision |
| -a | requerido | agregar o borrar |
| --vlans | 100:VLAN-HACK | VLANs a inyectar |

---

## Uso

```bash
# Agregar VLANs
sudo python3 vtp_attack.py -a agregar --vlans 100:VLAN-HACK 200:VLAN-INTRUSO

# Borrar todas las VLANs (interrupcion total)
sudo python3 vtp_attack.py -a borrar
```

---

## Configuracion Cisco — SW-CORE (VTP Server)

```
hostname SW-CORE
vtp domain LAB-2023-0316
vtp mode server
vtp version 2
vlan 10
 name Administracion
vlan 20
 name Usuarios
vlan 30
 name Servidores
interface GigabitEthernet0/0
 switchport trunk encapsulation dot1q
 switchport mode trunk
 no shutdown
interface GigabitEthernet0/1
 switchport trunk encapsulation dot1q
 switchport mode trunk
 no shutdown
interface GigabitEthernet0/2
 switchport trunk encapsulation dot1q
 switchport mode trunk
 no shutdown
interface Vlan10
 ip address 20.23.3.2 255.255.255.240
 no shutdown
```

## Configuracion Cisco — SW-ACC-1 (VTP Client)

```
hostname SW-ACC-1
vtp domain LAB-2023-0316
vtp mode client
interface GigabitEthernet0/0
 switchport trunk encapsulation dot1q
 switchport mode trunk
 no shutdown
interface GigabitEthernet0/1
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast
 no shutdown
interface Vlan10
 ip address 20.23.3.3 255.255.255.240
 no shutdown
```

## Configuracion Cisco — SW-ACC-2 (VTP Client)

```
hostname SW-ACC-2
vtp domain LAB-2023-0316
vtp mode client
interface GigabitEthernet0/0
 switchport trunk encapsulation dot1q
 switchport mode trunk
 no shutdown
interface GigabitEthernet0/1
 switchport mode access
 switchport access vlan 30
 spanning-tree portfast
 no shutdown
interface Vlan10
 ip address 20.23.3.4 255.255.255.240
 no shutdown
```

---

## Verificacion

```cisco
show vtp status
show vlan brief
show interfaces trunk
```

---

## Contramediadas

| Medida | Comando | Efectividad |
|---|---|---|
| VTP Transparent | vtp mode transparent | Alta |
| VTP Off | vtp mode off | Alta |
| Contrasena | vtp password <pass> secret | Media |
| VTPv3 Primary | vtp version 3 + vtp primary vlan | Alta |

---
*Laboratorio academico | ITLA | Matricula: 2023-0316*
