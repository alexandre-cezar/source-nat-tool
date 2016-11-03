# source-nat-tool
Tool to automate the creation of source NAT rules using FQDN objects

The tool requires Juniper PYEZ to work.

Work way

Just configure the nat_parameter file with the required information and run the nat_tool_v2 script.

The script will resolve the FQDN into ip addresses, create the proper source nat rules, connect to the device and push the new configuration.
