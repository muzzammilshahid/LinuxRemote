import socket

from zeroconf import IPVersion, ServiceInfo, Zeroconf


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


class Discovery:
    def __init__(self, port) -> None:
        super().__init__()
        ip_version = IPVersion.V4Only
        desc = {'path': '/~muzzammil-Y11C/'}
        self.info = ServiceInfo(
            "_http._tcp.local.",
            f"{socket.gethostname()}._http._tcp.local.",
            addresses=[socket.inet_aton(get_ip())],
            port=port,
            properties=desc,
            server="ash-2.local.",
        )
        self.zeroconf = Zeroconf(ip_version=ip_version)

    def publish(self):
        print("Registration of a service")
        self.zeroconf.register_service(self.info)

    def unpublish(self):
        self.zeroconf.unregister_service(self.info)
        self.zeroconf.close()
