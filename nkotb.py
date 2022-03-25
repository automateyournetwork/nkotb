import logging
import json
import datetime as d
import hashlib as h
import uuid
from pathlib import Path
from pyats.topology import Testbed, Device
from genie import testbed
from jinja2 import Environment, FileSystemLoader

class NetworkToBlockchain(object):
    def __init__(self, hostname, username, password, ip):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.ip = ip

    # Create Testbed
    def connect_device(self):
        try:
            first_testbed = Testbed('dynamicallyCreatedTestbed')
            testbed_device = Device(self.hostname,
                        alias = self.hostname,
                        type = 'switch',
                        os = 'nxos',
                        credentials = {
                            'default': {
                                'username': self.username,
                                'password': self.password,
                            }
                        },
                        connections = {
                            'cli': {
                                'protocol': 'ssh',
                                'ip': self.ip,
                                'port': 22,
                                'arguements': {
                                    'connection_timeout': 360
                                }
                            }
                        })
            testbed_device.testbed = first_testbed
            new_testbed = testbed.load(first_testbed)
        except Exception as e:
            logging.exception(e)
        return(new_testbed)

    def capture_state(self):
        # ---------------------------------------
        # Loop over devices
        # ---------------------------------------
        for device in self.connect_device():
            device.alias
            device.connect()
        # Learn Interace to JSON
            try:
                learn_platform = device.learn("platform").to_dict()
            except:
                learn_platform = f"{ hostname } has no Interface to Learn"
        
        return(learn_platform)

    def template_output(self):
        template_dir = Path(__file__).resolve().parent
        env = Environment(loader=FileSystemLoader(template_dir))
        device_template = env.get_template('template.j2')
        captured_info = self.capture_state()
        return(captured_info)

class Block(object):
    def __init__(self,NetworkToBlockchain,index,timestamp,data,prevhash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.prevhash = prevhash
        self.hash = self.hashblock()

    def hashblock(self):
        block_encryption = h.sha256()
        block_encryption.update(str(self.index).encode('utf-8')+str(self.timestamp).encode('utf-8')+str(self.data).encode('utf-8')+str(self.prevhash).encode('utf-8'))
        return block_encryption.hexdigest()

    @staticmethod
    def genesisblock():
        random_prevhash = uuid.uuid4().hex
        return Block("",0,d.datetime.now(),"genesis block transaction",random_prevhash)

    @staticmethod
    def newblock(prevblock,device):
        index = prevblock.index + 1
        timestamp = d.datetime.now()
        hashblock = prevblock.hash
        data = device.template_output()
        return Block(device,index,timestamp,data,hashblock)


device=NetworkToBlockchain("dist-sw01","cisco","cisco","10.10.20.177")
blockchain = [Block.genesisblock()]
prevblock = blockchain[0]

print (f"Block ID: { prevblock.index }")
print (f"Timestamp: {prevblock.timestamp}")
print (f"Hash of the block: { prevblock.hash }")
print (f"Previous Block Hash: { prevblock.prevhash }")
print (f"Data: { prevblock.data } \n")

addblock = Block.newblock(prevblock,device)
blockchain.append(addblock)
prevblock = addblock

print (f"Block ID # { addblock.index }")
print (f"Block Timestamp: { addblock.timestamp }")
print (f"Hash of the Block: { addblock.hash }")
print (f"Previous Block Hash: { addblock.prevhash }")
print (f"Block Data: { addblock.data } \n")

print ("Example of querying the blockchain")
print (f"Hostname is { addblock.data['virtual_device']['1']['vd_name'] }")
print (f"Serial Number is { addblock.data['chassis_sn'] }")