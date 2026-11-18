#!/usr/bin/python
"""Validate TLS using the system trust store and inspect certificate expiry."""
import socket
import ssl
import time


def main():
    from ansible.module_utils.basic import AnsibleModule
    m=AnsibleModule(argument_spec={'host':{'type':'str','required':True},'port':{'type':'int','default':443},
                                  'minimum_days':{'type':'int','default':14}},supports_check_mode=True)
    try:
        context=ssl.create_default_context()
        with socket.create_connection((m.params['host'],m.params['port']),timeout=10) as raw:
            with context.wrap_socket(raw,server_hostname=m.params['host']) as stream:
                cert=stream.getpeercert()
        days=(ssl.cert_time_to_seconds(cert['notAfter'])-time.time())/86400
        if days<m.params['minimum_days']: m.fail_json(msg='Certificate expiry threshold reached',days_remaining=round(days,2))
        m.exit_json(changed=False,verified=True,days_remaining=round(days,2),expires=cert['notAfter'])
    except (OSError,ValueError,KeyError) as exc: m.fail_json(msg='TLS verification failed: '+str(exc))


if __name__=='__main__': main()
