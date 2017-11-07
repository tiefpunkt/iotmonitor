import urllib.request
import json
from datetime import datetime, timedelta
from dateutil import parser
from dateutil.tz import tzutc


class Device(object):
    def __init__(self, name):
        self.name = name

    def getState(self):
        pass


class JSONDevice(Device):
    def getData(self):
            with urllib.request.urlopen(self._url) as url:
                data = json.loads(url.read().decode())
            return data

    def getState(self):
        data = self.getData()
        return self.check(data)

    def check(self, data):
        if self._check:
            return self._check(data)
        return False


class AirRohr(JSONDevice):
    def __init__(self, name, id):
        super().__init__(name)
        self._url = "http://api.luftdaten.info/v1/sensor/%s/" % id
        self._check = lambda data: len(data) > 0


class FreifunkMuc(JSONDevice):
    _url = "https://map.ffmuc.net/data/nodes.json"
    max_age = timedelta(seconds=30)

    cache = None
    cache_fetch_time = datetime.fromtimestamp(0)

    def __init__(self, name, id):
        super().__init__(name)
        self._id = id

    def getData(self):
        if not FreifunkMuc.cache or datetime.now() - FreifunkMuc.cache_fetch_time > FreifunkMuc.max_age:
            FreifunkMuc.cache = super(FreifunkMuc, self).getData()
            FreifunkMuc.cache_fetch_time = datetime.now()
        return self.cache

    def check(self, data):
        nodedata = list(filter(lambda node: node["nodeinfo"]["node_id"] == self._id, data["nodes"]))
        if len(nodedata) == 1:
            return nodedata[0]["flags"]["online"]
        return False


class ThingsNetworkGateway(JSONDevice):
    def __init__(self, name, id):
        super().__init__(name)
        self._url = "http://noc.thethingsnetwork.org:8085/api/v2/gateways/%s" % id
        self._check = lambda data: len(data) > 0

    def check(self, data):
        last_ping = parser.parse(data['timestamp'])
        now = datetime.now(tzutc())
        delta = now - last_ping

        return delta.days == 0 and delta.seconds < 300


class OpenSenseMap(JSONDevice):
    def __init__(self, name, id):
        super().__init__(name)
        self._url = "https://api.opensensemap.org/boxes/%s" % id
        self._check = lambda data: len(data) > 0

    def check(self, data):
        last_ping = parser.parse(data['updatedAt'])
        now = datetime.now(tzutc())
        delta = now - last_ping

        return delta.days == 0 and delta.seconds < 600
