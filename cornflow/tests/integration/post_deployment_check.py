from cornflow.tests.integration.test_cornflowclient import TestInstances
import os
import logging as log


class RemoteServerTest(TestInstances):

    def __call__(self, result=None):
        self.server = os.environ.get('TEST_SERVER', 'http://localhost:5000')
        super().__call__()

    def _spawn_live_server(self):
        pass

    def _terminate_live_server(self):
        pass

    def get_server_url(self):
        return self.server

    def setUp(self, server_url=''):
        log.root.setLevel(log.DEBUG)
        super().setUp(create_all=False)