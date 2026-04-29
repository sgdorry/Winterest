"""
Manager of security protocols.
Each protocol has a unique name.
Attempts to add a name a second time will fail with a ValueError.
"""
from copy import deepcopy
from functools import wraps
import os

from . import api_key as apik

BAD_TYPE = 'Bad type for: '

CREATE = 'create'
READ = 'read'
UPDATE = 'update'
DELETE = 'delete'
VALID_ACTIONS = [CREATE, READ, UPDATE, DELETE]

VALIDATOR = 'validator'
IN_EFFECT = 'in_effect'

API_KEY = 'api_key'
API_KEYS = 'api_keys'
AUTH_KEY = 'auth_key'
PASSWORD = 'password'
PROT_NM = 'protocol_name'
SEC_COLLECT = 'security_protocols'
USERS = 'users'
VALIDATE_USER = 'validateUser'
PASS_PHRASE = 'pass_phrase'
IP_ADDRESS = 'ipAddress'
CODES = 'codes'
LOGS = 'logs'

protocols = {}


def needs_protocols(fn):
	"""
	Should be used to decorate any function that directly uses the protocols.
	Functions that call functions that use the protocols don't need this
	decorator.
	"""
	@wraps(fn)
	def wrapper(*args, **kwargs):
		if not protocols:
			fetch_all()
		return fn(*args, **kwargs)
	return wrapper


def is_valid_action(action: str):
	return action in VALID_ACTIONS


class ActionChecks(object):
	"""
	The defaults will mean no checks.
	"""
	def __init__(self,
				 auth_key=False,
				 api_key=False,
				 valid_api_keys=[],
				 ip_address=None,
				 pass_phrase=False,
				 valid_users=None,
				 codes=None,
				 this_phrase=''):
		self.phrase = None
		if not isinstance(auth_key, bool):
			raise TypeError(f'{BAD_TYPE}{type(auth_key)=}')
		if not isinstance(api_key, bool):
			raise TypeError(f'{BAD_TYPE}{type(api_key)=}')
		if not isinstance(pass_phrase, bool):
			raise TypeError(f'{BAD_TYPE}{type(pass_phrase)=}')
		elif pass_phrase:
			self.phrase = this_phrase
		if valid_users:
			if not isinstance(valid_users, list):
				raise TypeError(f'{BAD_TYPE}{type(valid_users)=}')
			for user in valid_users:
				if not isinstance(user, str):
					raise TypeError(f'{BAD_TYPE}{type(user)=}')
		if valid_api_keys:
			if not isinstance(valid_api_keys, list):
				raise TypeError(f'{BAD_TYPE}{type(valid_api_keys)=}')
			for api_key_val in valid_api_keys:
				if not isinstance(api_key_val, str):
					raise TypeError(f'{BAD_TYPE}{type(api_key_val)=}')
		if ip_address and not isinstance(ip_address, str):
			raise TypeError(f'{BAD_TYPE}{type(ip_address)=}')
		self.checks = {
			VALIDATE_USER: {
				IN_EFFECT: valid_users is not None,
				VALIDATOR: self.is_valid_user,
			},
			API_KEY: {
				IN_EFFECT: api_key,
				VALIDATOR: self.is_valid_api_key,
			},
			AUTH_KEY: {
				IN_EFFECT: auth_key,
				VALIDATOR: self.is_valid_auth_key,
			},
			PASS_PHRASE: {
				IN_EFFECT: pass_phrase,
				VALIDATOR: self.is_valid_pass_phrase,
			},
			CODES: {
				IN_EFFECT: codes is not None,
				VALIDATOR: self.is_valid_code,
			},
			# IP_ADDRESS: to be developed!
		}
		self.valid_users = valid_users
		self.valid_api_keys = valid_api_keys
		self.codes = codes

	def __str__(self):
		return str(self.checks)

	def to_json(self):
		json_checks = deepcopy(self.checks)
		for check in json_checks:
			json_checks[check] = json_checks[check][IN_EFFECT]
		if self.valid_users:
			json_checks[USERS] = self.valid_users
		if self.valid_api_keys:
			json_checks[API_KEYS] = self.valid_api_keys
		if self.phrase:
			json_checks[PASSWORD] = self.phrase
		if self.codes:
			json_checks[CODES] = self.codes
		else:
			del json_checks[CODES]
		return json_checks

	def is_valid_auth_key(self, user_id: str, auth_key: str) -> bool:
		return False

	def is_valid_api_key(self, user_id: str, api_key: str) -> bool:
		if self.valid_api_keys:
			return api_key in self.valid_api_keys
		return apik.exists(api_key)

	def is_valid_pass_phrase(self, user_id: str, pass_phrase: str) -> bool:
		return pass_phrase == self.phrase

	def is_valid_user(self, user_id: str, user):
		valid = True
		if self.valid_users:
			valid = user in self.valid_users
		return valid

	def is_valid_code(self, user_id: str, code: str):
		valid = True
		if self.codes:
			valid = code in self.codes.values()
		return valid

	def is_permitted(self, user_id: str, check_vals: dict) -> bool:
		for check, val in self.checks.items():
			if val[IN_EFFECT]:
				if check not in check_vals:
					raise ValueError(f'Value missing for {check}')
				if not self.checks[check][VALIDATOR](user_id,
													 check_vals[check]):
					return False
		return True

	def has_validate_user(self) -> bool:
		return self.checks[VALIDATE_USER][IN_EFFECT]


class SecProtocol(object):
	"""
	The defaults will mean no checks for anything.
	"""
	def __init__(self,
				 name,
				 create=ActionChecks(),
				 read=ActionChecks(),
				 update=ActionChecks(),
				 delete=ActionChecks()):
		if not isinstance(name, str):
			raise TypeError(f'{BAD_TYPE}{type(name)=}')
		self.name = name
		if not isinstance(create, ActionChecks):
			raise TypeError(f'{BAD_TYPE}{type(create)=}')
		self.create = create
		if not isinstance(read, ActionChecks):
			raise TypeError(f'{BAD_TYPE}{type(read)=}')
		self.read = read
		if not isinstance(update, ActionChecks):
			raise TypeError(f'{BAD_TYPE}{type(update)=}')
		self.update = update
		if not isinstance(delete, ActionChecks):
			raise TypeError(f'{BAD_TYPE}{type(delete)=}')
		self.delete = delete

	def to_json(self):
		prot = {
			PROT_NM: self.name,
			CREATE: self.create.to_json(),
			READ: self.read.to_json(),
			UPDATE: self.update.to_json(),
			DELETE: self.delete.to_json(),
		}
		return prot

	def get_name(self):
		return self.name

	def is_permitted(self,
					 action: str,
					 user_id: str,
					 check_vals: dict,
					 ) -> bool:
		valid = True
		if action in self.__dict__:
			valid = self.__dict__[action].is_permitted(user_id,
													   check_vals)
		return valid

	def is_valid_user(self, action: str, user_id: str) -> bool:
		valid = True
		if action in self.__dict__:
			valid = valid = self.__dict__[action].is_valid_user(user_id,
																user_id)
		return valid

	@needs_protocols
	def add_user(self, user_id: str, actions: list):
		if actions is None:
			actions = VALID_ACTIONS
		for action in actions:
			if is_valid_action(action):
				if self.__dict__[action].has_validate_user():
					action_list = f'{action}.{USERS}'
					_ = action_list
			else:
				raise ValueError(f'{action} is not a valid action')

	@needs_protocols
	def delete_user(self, user_id: str, actions: list):
		if actions is None:
			actions = VALID_ACTIONS
		for action in actions:
			if is_valid_action(action):
				if self.__dict__[action].has_validate_user():
					action_list = f'{action}.{USERS}'
					_ = action_list
			else:
				raise ValueError(f'{action} is not a valid action')


def is_permitted(prot_name, action, user_id: str = '', auth_key: str = '',
				 api_key: str = '', phrase: str = '', code: str = None):
	prot = fetch_by_key(prot_name)
	if not prot:
		raise ValueError(f'Unknown protocol: {prot_name=}')
	check_vals = {}
	check_vals[API_KEY] = api_key
	check_vals[AUTH_KEY] = auth_key
	check_vals[CODES] = code
	check_vals[PASS_PHRASE] = phrase
	check_vals[VALIDATE_USER] = user_id
	return prot.is_permitted(action, user_id, check_vals)


@needs_protocols
def fetch_by_key(prot_name: str):
	ret = protocols.get(prot_name, None)
	return ret


def is_valid_user(prot_name: str, action: str, user: str):
	valid = True
	prot = fetch_by_key(prot_name)
	if prot:
		valid = prot.is_valid_user(action, user)
	return valid


def add(protocol):
	if not isinstance(protocol, SecProtocol):
		raise TypeError(f'Invalid type for protocol: {type(protocol)}')
	name = protocol.get_name()
	if name in protocols:
		raise ValueError(f"Can't add duplicate name to protocols: {name=}")
	protocols[name] = protocol


def exists(name):
	return name in protocols


@needs_protocols
def delete(name):
	if name in protocols:
		del protocols[name]
	else:
		raise ValueError(f'Attempt to delete non-existent protocol: {name=}')


def checks_from_json(check_json):
	if not check_json:
		return ActionChecks()
	return ActionChecks(api_key=check_json.get(API_KEY, False),
						auth_key=check_json.get(AUTH_KEY, False),
						pass_phrase=check_json.get(PASS_PHRASE, False),
						valid_api_keys=check_json.get(API_KEYS, []),
						valid_users=check_json.get(USERS, None),
						ip_address=check_json.get(IP_ADDRESS, None),
						this_phrase=check_json.get(PASSWORD, None),
						codes=check_json.get(CODES, None))


def protocol_from_json(protocol_json):
	protocol_name = protocol_json[PROT_NM]
	create_checks = checks_from_json(protocol_json.get(CREATE))
	read_checks = checks_from_json(protocol_json.get(READ))
	update_checks = checks_from_json(protocol_json.get(UPDATE))
	delete_checks = checks_from_json(protocol_json.get(DELETE))
	return SecProtocol(protocol_name,
					   create=create_checks,
					   read=read_checks,
					   update=update_checks,
					   delete=delete_checks)


def fetch_all() -> None:
	if len(protocols) < 1:
		protocols[USERS] = USERS_PROTOCOL
		protocols[LOGS] = LOGS_PROTOCOL


@needs_protocols
def refresh_all() -> bool:
	protocols.clear()
	return fetch_all()


@needs_protocols
def add_to_db(protocol):
	return protocol.to_json()


def fetch_journal_protocol_name() -> str:
	return USERS


def add_user_to_protocol(
	protocol_name: str,
	user_id: str,
	actions: list = None,
):
	prot = fetch_by_key(protocol_name)
	if prot is None:
		raise ValueError(f'Could not find {protocol_name} protocol')
	return prot.add_user(user_id, actions)


def delete_user_from_protocol(
	protocol_name: str,
	user_id: str,
	actions: list = None,
):
	prot = fetch_by_key(protocol_name)
	if prot is None:
		raise ValueError(f'Could not find {protocol_name} protocol')
	return prot.delete_user(user_id, actions)


USERS_API_KEY = os.environ.get('WINTEREST_USERS_API_KEY', 'WINTEREST_USERS_KEY')
USERS_SEC_CHECKS = ActionChecks(api_key=True,
								valid_api_keys=[USERS_API_KEY])
USERS_PROTOCOL = SecProtocol(USERS, update=USERS_SEC_CHECKS)

LOGS_API_KEY = os.environ.get('WINTEREST_LOGS_API_KEY', 'WINTEREST_LOGS_KEY')
LOGS_SEC_CHECKS = ActionChecks(api_key=True,
						valid_api_keys=[LOGS_API_KEY])
LOGS_PROTOCOL = SecProtocol(LOGS, read=LOGS_SEC_CHECKS)


def protect(feature_name: str, action: str = CREATE, header_name: str = 'X-API-Key'):
	def decorator(fn):
		@wraps(fn)
		def wrapper(*args, **kwargs):
			from flask import request

			api_key_value = request.headers.get(header_name, '')
			if not is_permitted(feature_name, action, api_key=api_key_value):
				return {'error': 'API key required or invalid'}, 401
			return fn(*args, **kwargs)

		return wrapper

	return decorator


refresh_all()
