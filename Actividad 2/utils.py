from dnslib import DNSRecord
from dnslib.dns import CLASS, QTYPE
import dnslib

def parse_dns_message(message):
    return DNSRecord.parse(message)

def 