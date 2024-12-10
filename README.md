# IOS-Parser
Python script to parse config tables to ios config files

## Features

- Parses router tiers and interface details from a Markdown file.

- Processes router loopbacks from a separate Markdown file.

- Generates IPv4 and IPv6 configurations for each router interface and loopback.

- Outputs configurations sorted by router number.

## Usage

### Prerequisites
- Python 3.x
- Pandas library

### Running the Script
To run the script, provide the markdown files for configuration and loopbacks as inputs, along with an optional output filename.

Example:
```bash
python ios_parser.py ios.md loopbacks.md -o configs.txt
```

### Input Files
1. `ios.md`:
   This file contains topology information organized in markdown tables.

2. `loopbacks.md`:
   This file contains the loopback configurations for each router.

### Output
The script outputs a configuration file (e.g., `configs.txt`) with configurations for all routers in the network.

## Example Files
- `ios.md`: Example markdown input with tiered network configurations.
- `loopbacks.md`: Example markdown input with loopback details.
- `configs.txt`: Example generated output.

## Examples

### Input Files

#### ios.md
```
# Tiers

---

## Tier 1A
| Ligação | 1 IPv6 | 2 IPv6 | 1 Link-Local | 2 Link-Local | 1 IPv4 | 2 IPv4 |
| --- | --- | --- | --- | --- | --- | --- |
| R1-R4 f1/0 | XXXX:XXXX:XXXX:XXXX::X::1/64 | XXXX:XXXX:XXXX:XXXX::X::2/64 | FE80::1 | FE80::4 | X.X.X.X/30 | X.X.X.X/30 |
| R2-R6 f1/0 | XXXX:XXXX:XXXX:XXXX::X::1/64 | XXXX:XXXX:XXXX:XXXX::X::2/64 | FE80::2 | FE80::6 | X.X.X.X/30 | X.X.X.X/30 |
| R4-R6 f0/0 | XXXX:XXXX:XXXX:XXXX::X::1/64 | XXXX:XXXX:XXXX:XXXX::X::2/64 | FE80::4 | FE80::6 | X.X.X.X/30...
```

#### loopbacks.md
```
## Loopbacks
| Router | IPv6/128 | IPv4/32 |
| --- | --- | --- |
| R1 | XXXX:XXXX:XXXX:XXXX::X::1 | X.X.X.X |
| R2 | XXXX:XXXX:XXXX:XXXX::X::2 | X.X.X.X |
| R3 | XXXX:XXXX:XXXX:XXXX::X::3 | X.X.X.X |
| R4 | XXXX:XXXX:XXXX:XXXX::X::4 | X.X.X.X |
| R5 | XXXX:XXXX:XXXX:XXXX::X::5 | X.X.X.X |
| R6 | XXXX:XXXX:XXXX:XXXX::X::6 | X.X.X.X |
| R7 | XXXX:XXXX:XXXX:XXXX::X::7 | X.X.X.X |
| R8 | XXXX:XXXX:XXXX:XXXX::X::8 | X.X.X.X |
| R9 | XXXX:XXXX:XXXX:XXXX::X::9 | X.X.X.X |
| R10 | XXXX:XXXX:XXXX:XXXX::X...
```

### Output File

#### configs.txt
```
Configurations for R1:
----------------------------------------

interface f1/0
 description Link to R4
 ipv6 address XXXX:XXXX:XXXX:XXXX::X::1/64 
 ipv6 address FE80::1  link-local
 ip address X.X.X.X X.X.X.X
 no shutdown

interface Loopback0
 description Loopback interface for R1
 ipv6 address XXXX:XXXX:XXXX:XXXX::X::1/128
 ipv6 address FE80::1 link-local
 ip address X.X.X.X X.X.X.X

Configurations for R2:
----------------------------------------

interface f1/0
 description Link to R6
 ipv6 a...
```

## License
This project is licensed under the GNU General Public License v2.0.
