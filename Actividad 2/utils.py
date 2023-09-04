from dnslib import DNSRecord
from dnslib.dns import CLASS, QTYPE
import dnslib

def parse_dns_message(message):
    parsed_messsage = DNSRecord.parse(message)

    q = {}

    print(parsed_messsage)
