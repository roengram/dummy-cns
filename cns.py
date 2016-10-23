#!/usr/bin/python

from docker import Client
import pprint
import os
import signal

pp = pprint.PrettyPrinter(indent=4)

def apply_dns(dnsdb):
    dnsfile = os.getenv("DNSMASQ_HOSTFILE", "/etc/dnsmasq.d/static_hosts")
    # render
    with open(dnsfile, "w+") as f:
        for contdns in dnsdb.values():
            for e in contdns:
                f.write("%s\n" % e)

    # reload
    pid = os.environ.get("DNSMASQ_PID")
    if pid != None:
        os.kill(pid, signal.SIGHUP)

def loop():
    docker_endpoint = os.getenv("DOCKER_ENDPOINT", "unix://var/run/docker.sock")
    docker_version = os.getenv("DOCKER_VERSION", "auto")
    base_domain = os.getenv("DOMAIN", "neptune.org")
    dnsdb = {}

    client = Client(base_url=docker_endpoint, version=docker_version)
    events = client.events(filters={"event": ["start", "die"]}, decode=True)
    for evt in events:
        if evt["status"] == "start":
#            print "started: %s" % (evt["id"])
            cid = evt["id"]
            detail = client.inspect_container(cid)
#            pp.pprint(detail)
            labels = detail["Config"]["Labels"]
            newdns = []
            networks = detail["NetworkSettings"]["Networks"]

            if labels.has_key("triton.cns.services"):
                dc = labels.get("dc", "UNKNOWNDC")
                services = labels["triton.cns.services"]
                service_list = services.split(',')
                for s in service_list: 
                    fqdn = "%s.svc.%s.%s" % (s, dc, base_domain)
                    for n in networks.values():
                        ip = n["IPAddress"]
                        newdns.append("%s %s" %(ip, fqdn))

            if labels.has_key("neptune.cns.services"):
                services = labels["neptune.cns.services"]
                service_list = services.split(',')
                for s in service_list: 
                    fqdn = "%s.svc.%s" % (s, base_domain)
                    for n in networks.values():
                        ip = n["IPAddress"]
                        newdns.append("%s %s" %(ip, fqdn))
            dnsdb[cid] = newdns
#            pp.pprint(dnsdb)

        elif evt["status"] == "die":
#            print "died: %s" % (evt["id"])
            cid = evt["id"]
            del dnsdb[cid]
#            pp.pprint(dnsdb)
#            pp.pprint(detail)

        # apply dns
        apply_dns(dnsdb)
        

if __name__ == "__main__":
    loop()
