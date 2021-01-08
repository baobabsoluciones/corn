from flaskr.app import create_app
from flaskr.models import db
from flask_testing import TestCase
from flaskr.models.user import UserModel

import json


class TestLogIn(TestCase):
    def create_app(self):
        app = create_app('testing')

        return app

    def setUp(self):
        db.create_all()
        data = {'name': 'testname', 'email': 'test@test.com', 'password': 'testpassword'}
        user = UserModel(data=data)
        user.save()
        db.session.commit()
        self.data = {
            'name': 'testname',
            'email': 'test@test.com',
            'password': 'testpassword'
        }

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_successful_log_in(self):
        payload = self.data

        response = self.client.post('/login/', data=json.dumps(payload), follow_redirects=True,
                                    headers={"Content-Type": "application/json"})

        self.assertEqual(200, response.status_code)
        self.assertEqual(str, type(response.json['token']))

    def test_validation_error(self):
        payload = self.data
        payload['email'] = 'test'

        response = self.client.post('/login/', data=json.dumps(payload), follow_redirects=True,
                                    headers={"Content-Type": "application/json"})

        self.assertEqual(400, response.status_code)
        self.assertEqual(dict, type(response.json['error']))
        self.assertEqual('Not a valid email address.', response.json['error']['email'][0])

    def test_missing_email(self):
        payload = self.data
        payload.pop('email', None)
        response = self.client.post('/login/', data=json.dumps(payload), follow_redirects=True,
                                    headers={"Content-Type": "application/json"})

        self.assertEqual(400, response.status_code)
        self.assertEqual(str, type(response.json['error']))
        self.assertEqual('You need email and password to sign in.', response.json['error'])

    def test_missing_password(self):
        payload = self.data
        payload.pop('password', None)
        response = self.client.post('/login/', data=json.dumps(payload), follow_redirects=True,
                                    headers={"Content-Type": "application/json"})

        self.assertEqual(400, response.status_code)
        self.assertEqual(str, type(response.json['error']))
        self.assertEqual('You need email and password to sign in.', response.json['error'])

    def test_invalid_email(self):
        payload = self.data
        payload['email'] = 'test@test.org'

        response = self.client.post('/login/', data=json.dumps(payload), follow_redirects=True,
                                    headers={"Content-Type": "application/json"})

        self.assertEqual(400, response.status_code)
        self.assertEqual(str, type(response.json['error']))
        self.assertEqual('Invalid credentials.', response.json['error'])

    def test_invalid_password(self):
        payload = self.data
        payload['password'] = 'testpassword_2'

        response = self.client.post('/login/', data=json.dumps(payload), follow_redirects=True,
                                    headers={"Content-Type": "application/json"})

        self.assertEqual(400, response.status_code)
        self.assertEqual(str, type(response.json['error']))
        self.assertEqual('Invalid credentials.', response.json['error'])

    def test_token(self):
        # TODO: implement to check correct token creation
        pass
