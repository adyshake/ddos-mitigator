import os
from pox.core import core
from pox.lib.recoco import Timer
from pox.openflow.of_json import *
import pox.openflow.libopenflow_01 as of

# Global Constants
RATE_LIMIT = 50
TCP_PORT = 80
TCP_PROTOCOL = 6
IPV4_PACKET = 0x800
DESTINATION_SUBNET = '10.0.0.0/24'

# Global dictionaries
blocked_ips = []

# Send flow stats request to all connected switches connected to the controller
def get_flow_stats():
  for connection in list(core.openflow._connections.values()):
    connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))

# Process flow stats received from connected switches 
def handle_flow_stats(event):
  ip_packet_count = {}
  stats = flow_stats_to_list(event.stats)
  for f in event.stats:
    if f.match.tp_dst == TCP_PORT:
      src_ip = str(f.match.nw_src)
      prev_packet_count = 0
      if src_ip in ip_packet_count:
        prev_packet_count = ip_packet_count[src_ip]
      ip_packet_count[src_ip] = prev_packet_count + f.packet_count
      if src_ip not in blocked_ips:
        if ip_packet_count[src_ip] > RATE_LIMIT:
          block_ip(src_ip)

def block_ip(ip):
  global blocked_ips
  # Add flow to block IP
  for connection in list(core.openflow._connections.values()):
    # By not speficying ofp_flow_mod's 'actions' parameter, it defaults the
    # action to drop packets
    # Source: https://opennetworking.org/wp-content/uploads/2014/10/openflow-spec-v1.3.2.pdf
    # Page 23
    connection.send(of.ofp_flow_mod(match=of.ofp_match(nw_proto=TCP_PROTOCOL,
                                                       dl_type=IPV4_PACKET,
                                                       nw_src=ip,
                                                       nw_dst=DESTINATION_SUBNET,
                                                       tp_dst=TCP_PORT)))
  blocked_ips.append(ip)
  print('Host ' + ip + ' has exceeded the packet rate and has been blocked')

core.openflow.addListenerByName('FlowStatsReceived', handle_flow_stats) 

Timer(.1, get_flow_stats, recurring=True)
