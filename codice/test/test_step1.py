import unittest
from config import *
import socket
import sys

class message(object):
    def encode(self,data):
        return base64.b64encode(json.dumps(data))+"\n\r"

    def decode(self,data):
        return json.loads(base64.b64decode(data))


class TestStep1(unittest.TestCase):
    def setUp(self):
        self.csocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.csocket.connect(((SERVER_HOST,SERVER_PORT)))

    def tearDown(self):
        self.payload = {"cmd":"exit","data":{"usr":"user1"}}
        self.csocket.send(message().encode(self.payload))
        self.csocket.close()

    def test_P1(self):
        self.payload = {"cmd":"login","data":{"usr":"user1","psw":"pass"}}
        self.csocket.send(message().encode(self.payload))
        data = self.csocket.recv(1024)
        data = message().decode(data)
        self.assertEqual("ok", data['response'])

        self.payload = {"cmd":"login","data":{"usr":"user1","psw":"pass"}}
        self.csocket.send(message().encode(self.payload))
        data = self.csocket.recv(1024)
        data = message().decode(data)
        self.assertEqual("alreadylogged", data['response'])

    def test_P2(self):
        self.payload = {"cmd":"login","data":{"usr":"user1","psw":"pass"}}
        self.csocket.send(message().encode(self.payload))
        data = self.csocket.recv(1024)
        data = message().decode(data)
        self.assertEqual("ok", data['response'])

        self.payload = {"cmd":"play","data":{"usr":"user1"}}
        self.csocket.send(message().encode(self.payload))
        data = self.csocket.recv(1024)
        data = message().decode(data)
        self.assertEqual("waiting", data['response'])

if __name__=="__main__":
    part = sys.argv[1:]
    if len(part)==0:
        unittest.main()
    else:
        suite = unittest.TestSuite()
        for t in part:
            testName = 'test_{}'.format(t)
            print "Adding test: {}\n".format(testName)
            suite.addTest(TestStep1(testName))
        unittest.TextTestRunner(verbosity=2).run(suite)
