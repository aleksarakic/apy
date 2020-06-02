from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from unittest import TestCase as Base
import json
import pdb
import requests
from requests.auth import _basic_auth_str
from application import db
from application.models import Calculation, User
from flask import g

from application.auth import authbp as auth_blueprint
# from application.main import mainbp as main_blueprint


db = SQLAlchemy()

def create_app(config=None):
	app = Flask(__name__)
	app.config.from_object(config)
	app.register_blueprint(auth_blueprint)
	# app.register_blueprint(main_blueprint)
	db.init_app(app)
	return app


class MyConfig(object):
	SQLALCHEMY_DATABASE_URI = "postgresql:///apy_dev"
	TESTING = True


class TestCase(Base):
	@classmethod
	def setUpClass(cls):
		cls.app = create_app(MyConfig())
		cls.client = cls.app.test_client()
		cls._ctx = cls.app.test_request_context()
		cls._ctx.push()
		db.create_all()

	@classmethod
	def tearDownClass(cls):
		db.session.remove()
		db.drop_all()   

	def setUp(self):
		self._ctx = self.app.test_request_context()
		self._ctx.push()
		db.session.begin(subtransactions=True)

	def tearDown(self):
		db.session.rollback()
		db.session.close()
		self._ctx.pop()


class TestModel(TestCase):

	def get_token(self, username='user', password='user'):
		with self.app.test_client() as client:
			res = requests.post("http://127.0.0.1:6767/token", headers={'Authorization': _basic_auth_str(username, password)})
			return res.json()['token']


	def test_add_takes_array_as_param(self):
		token = self.get_token()
		params = {"integer": [2,3]}
		res = requests.post("http://127.0.0.1:6767/add", headers={'Content-Type': 'application/json', 'Authorization': _basic_auth_str(token,'whatever')}, json=params)
		self.assertEqual(res.status_code, 200)


	def test_add_takes_integer_as_param(self):
		token = self.get_token()
		params = {"integer": 2}
		res = requests.post("http://127.0.0.1:6767/add", headers={'Content-Type': 'application/json', 'Authorization': _basic_auth_str(token,'whatever')}, json=params)
		self.assertEqual(res.status_code, 200)


	def test_reset_creates_calculation(self):
		token = self.get_token()
		pre_calculation_count = db.session.query(Calculation).count()
		res = requests.post("http://127.0.0.1:6767/reset", headers={'Content-Type': 'application/json', 'Authorization': _basic_auth_str(token,'whatever')})
		post_calculation_count = db.session.query(Calculation).count()
		self.assertEqual(post_calculation_count - 1, pre_calculation_count)


	def test_history_returns_all_calculations_when_user_is_admin(self):
	    token = self.get_token('admin', 'admin')
	    res = requests.get("http://127.0.0.1:6767/history", headers={'Content-Type': 'application/json', 'Authorization': _basic_auth_str(token,'whatever')})
	    all_calculations = db.session.query(Calculation).count()
	    res_count = len(res.json())
	    self.assertEqual(res_count, all_calculations)


	def test_history_finds_calculation_by_id(self):
	    token = self.get_token()
	    # get user which has more than one Calculation
	    user = db.session.query(User).filter(User.username == 'user').first()
	    calc_ids = user.calculation_ids
	    res = requests.get("http://127.0.0.1:6767/history", headers={'Content-Type': 'application/json', 'Authorization': _basic_auth_str(token,'whatever')}, json={'id': calc_ids[-1]})
	    count = len(res.json()) # returned just one calculation
	    count == 1 and calc_ids[-1] == res.json()[0]['id']

 
	def test_workflow(self):		
		token = self.get_token()
		# add 16
		requests.post("http://127.0.0.1:6767/add",
		                         headers={'Content-Type': 'application/json', 'Authorization': _basic_auth_str(token,'whatever')},
		                         json={"integer": 16})
		# add 20
		requests.post("http://127.0.0.1:6767/add",
		                         headers={'Content-Type': 'application/json', 'Authorization': _basic_auth_str(token,'whatever')},
		                         json={"integer": 20})
		# calculate
		requests.get("http://127.0.0.1:6767/calculate",
		                         headers={'Content-Type': 'application/json', 'Authorization': _basic_auth_str(token,'whatever')})
		# add [4, 10]
		requests.post("http://127.0.0.1:6767/add",
		                         headers={'Content-Type': 'application/json', 'Authorization': _basic_auth_str(token,'whatever')},
		                         json={"integer": [4, 10]})
		# calculate
		requests.get("http://127.0.0.1:6767/calculate",
		                         headers={'Content-Type': 'application/json', 'Authorization': _basic_auth_str(token,'whatever')})
		# reset
		requests.post("http://127.0.0.1:6767/reset",
		                         headers={'Content-Type': 'application/json', 'Authorization': _basic_auth_str(token,'whatever')})
		# history
		res = requests.get("http://127.0.0.1:6767/history", 
			                     headers={'Content-Type': 'application/json', 'Authorization': _basic_auth_str(token,'whatever')})
		# assert result
		calculation = res.json()[-1] # last calculation
		expected = {"array": [16, 20, 4, 10], "calculations": [36, 50], "id": calculation['id']}
		self.assertEqual(calculation, expected)


if __name__ == "__main__":
	import unittest
	unittest.main()
