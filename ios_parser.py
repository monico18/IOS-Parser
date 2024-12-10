import pandas as pd
import re
from io import StringIO


def parse_markdown_table(md_file):
    """
    Parse the markdown tables into dataframes.
    """
    with open(md_file, "r") as file:
        content = file.read()

    # Split the content into sections using a clear delimiter
    sections = re.split(r"\n---+\n", content)
    parsed_tables = {}

    for section in sections:
        # Get the title of the section
        title_match = re.search(r"## (.+)", section)
        if not title_match:
            continue  # Skip if no title

        tier_name = title_match.group(1).strip()
        print(f"Parsing section: {tier_name}") 

        # Extract the table lines
        table_lines = [
            line for line in section.split("\n") if "|" in line and "---" not in line
        ]

        if not table_lines:
            print(f"No table found in section: {tier_name}") 
            continue

        # Recreate table content
        table_content = "\n".join(table_lines)
        try:
            # Read the table into a DataFrame
            table_data = pd.read_csv(
                StringIO(table_content), sep="|", skipinitialspace=True
            ).dropna(axis=1, how="all")
            table_data.columns = table_data.columns.str.strip() 
            parsed_tables[tier_name] = table_data
        except Exception as e:
            print(f"Error parsing table in section {tier_name}: {e}") 

    return parsed_tables



def generate_interface_config(router, interface, ipv6, link_local, ipv4):
    """
    Generate interface configuration.
    """
    ipv4_mask = "255.255.255.252" if "/30" in ipv4 else ipv4.split()[1]
    ipv4_address = ipv4.split("/")[0]
    return f"""
interface {interface}
 description Link to {router}
 ipv6 address {ipv6}
 ipv6 address {link_local} link-local
 ip address {ipv4_address} {ipv4_mask}
 no shutdown
"""


def generate_loopback_config(router, ipv6, ipv4):
    """
    Generate loopback configuration.
    """
    router_number = int(re.sub(r"\D", "", router))
    ipv4_address = ipv4.split("/")[0]
    return f"""
interface Loopback0
 description Loopback interface for {router}
 ipv6 address {ipv6}/128
 ipv6 address FE80::{router_number} link-local
 ip address {ipv4_address} 255.255.255.255
"""

def add_loopback_configs(configs, loopbacks_file):
    """
    Parse loopbacks file and add loopback configurations to existing router configs.
    """
    # Parse the file and retrieve the loopbacks table
    tables = parse_markdown_table(loopbacks_file)
    loopbacks_table = tables.get("Loopbacks")

    if loopbacks_table is None:
        print("No Loopbacks table found in the provided file.") 
        return

    # Sanitize columns to ensure compatibility
    loopbacks_table.columns = loopbacks_table.columns.str.strip()

    for _, row in loopbacks_table.iterrows():
        try:
            # Validate that essential fields are not placeholders like '---'
            router = row["Router"].strip()
            ipv6 = row["IPv6/128"].strip()
            ipv4 = row["IPv4/32"].strip()

            if router == "---" or not router:
                print(f"Skipping invalid router entry: {row}") 
                continue

            if router not in configs:
                configs[router] = ""
            configs[router] += generate_loopback_config(router, ipv6, ipv4)
        except KeyError as e:
            print(f"KeyError in loopback table: {e}")

def generate_configs_from_tables(tables):
    """
    Generate configurations based on parsed markdown tables.
    """
    configs = {}

    for tier, df in tables.items():
        print(f"Processing tier: {tier}")
        if "Ligação" in df.columns:
            for _, row in df.iterrows():
                try:
                    routers = row["Ligação"].split(" ")[0].split("-")
                    interface = row["Ligação"].split(" ")[1]
                    router_1, router_2 = routers[0], routers[1]

                    if router_1 not in configs:
                        configs[router_1] = ""
                    if router_2 not in configs:
                        configs[router_2] = ""

                    configs[router_1] += generate_interface_config(
                        router_2, interface, row["1 IPv6"], row["1 Link-Local"], row["1 IPv4"]
                    )
                    configs[router_2] += generate_interface_config(
                        router_1, interface, row["2 IPv6"], row["2 Link-Local"], row["2 IPv4"]
                    )
                except KeyError as e:
                    print(f"KeyError in tier {tier}: {e}")

    return configs


def save_configs_to_file(configs, output_file):
    """
    Save all configurations to a single output file, sorted by router number.
    """
    # Sort the routers numerically by extracting the numeric part of the router name
    sorted_configs = dict(sorted(configs.items(), key=lambda x: int(re.sub(r"\D", "", x[0]))))

    with open(output_file, "w") as file:
        for router, config in sorted_configs.items():
            file.write(f"Configurations for {router}:\n{'-'*40}\n{config}\n")




def main(md_file, loopbacks_file, output_file):
    # Parse the markdown file for tiers
    tables = parse_markdown_table(md_file)
    if not tables:
        print("No tables parsed. Check the Markdown file formatting.")
        return

    # Generate the configurations
    configs = generate_configs_from_tables(tables)

    # Add loopback configurations from the separate loopbacks file
    add_loopback_configs(configs, loopbacks_file)

    if not configs:
        print("No configurations generated. Check the table content.")
        return

    # Save configurations to a single file
    save_configs_to_file(configs, output_file)
    print(f"Configurations saved to {output_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate Cisco IOS configs from a markdown file.")
    parser.add_argument("md_file", help="Path to the markdown file containing the tiers tables.")
    parser.add_argument("loopbacks_file", help="Path to the markdown file containing the loopbacks table.")
    parser.add_argument("-o", "--output_file", default="configs.txt", help="Output file to save all configs.")
    args = parser.parse_args()

    main(args.md_file, args.loopbacks_file, args.output_file)
