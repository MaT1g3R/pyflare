#!/usr/bin/env python3
import json

from requests import session


class Cloudflare:
    def __init__(self):
        with open('config.json') as json_data_file:
            config = json.load(json_data_file)
        email = config['email']
        key = config['key']
        self.zone = config['zone']
        self.records = config['records']

        self.endpoint = "https://api.cloudflare.com/client/v4"
        self.headers = {'X-Auth-Email': email, 'X-Auth-Key': key, 'Content-Type': 'application/json'}

        self.session = session()

        self.ip = self.get_ip()
        self.session.headers.update(self.headers)

    def user(self):
        r = self.session.get(self.endpoint + "/user", headers=self.headers)
        return r.json()

    def zones(self):
        payload = {'name': self.zone}
        r = self.session.get(self.endpoint + "/zones", headers=self.headers, params=payload)
        return r.json()

    def dns_records(self, zone_id, record):
        payload = {'name': record}
        r = self.session.get(self.endpoint + "/zones/" + zone_id + "/dns_records", headers=self.headers, params=payload)
        return r.json()

    def update_record(self, zone_id, record_id, record):
        payload = {'type': 'A', 'name': record, 'content': self.ip}
        r = self.session.put(self.endpoint + "/zones/" + zone_id + "/dns_records/" + record_id, headers=self.headers, data=json.dumps(payload))
        return r.json()

    def get_ip(self):
        r = self.session.get("https://httpbin.org/get")
        r.raise_for_status()
        return r.json()['origin']

    def __call__(self):
        with self.session:
            zone_id = self.zones()['result'][0]['id']
            for record in self.records:
                record_id = self.dns_records(zone_id, record).get('result', [{}])[0].get('id')
                if not record_id:
                    print('Cannot find record id for {}, skipping'.format(record))
                    continue
                print(self.update_record(zone_id, record_id, record))


if __name__ == '__main__':
    cf = Cloudflare()
    cf()
