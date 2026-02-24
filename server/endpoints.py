"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""
# from http import HTTPStatus

from flask import Flask
from flask_restx import Resource, Api, reqparse
from flask import request
from flask_cors import CORS

import countries.queries_countries as countries
import states.queries_states as states
import cities.queries_cities as cities
import counties.queries_counties as counties
import prompts.queries_prompts as prompts

# import werkzeug.exceptions as wz

app = Flask(__name__)
CORS(app)
api = Api(
    app,
    version='1.0',
    title='Geographic Database API',
    description='A REST API for managing geographic data including '
                'countries, states, and cities',
    doc='/'
)

ENDPOINT_EP = '/endpoints'
ENDPOINT_RESP = 'Available endpoints'
HELLO_EP = '/hello'
HELLO_RESP = 'hello'
MESSAGE = 'Message'

PROMPTS_EP = '/prompts'
QUIZ_QUESTIONS_EP = '/quiz/questions'


prompt_list_parser = reqparse.RequestParser()
prompt_list_parser.add_argument('type', required=False, location='args')

quiz_parser = reqparse.RequestParser()
quiz_parser.add_argument('type', required=True, location='args')
quiz_parser.add_argument('count', required=False, location='args',
                         type=int, default=5)


@api.route(HELLO_EP)
class HelloWorld(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    def get(self):
        """
        A trivial endpoint to see if the server is running.
        """
        return {HELLO_RESP: 'world'}


@api.route(ENDPOINT_EP)
class Endpoints(Resource):
    """
    This class will serve as live, fetchable documentation of what endpoints
    are available in the system.
    """
    def get(self):
        """
        The `get()` method will return a sorted list of available endpoints.
        """
        endpoints = sorted(rule.rule for rule in api.app.url_map.iter_rules())
        return {"Available endpoints": endpoints}


@api.route('/health')
class Health(Resource):
    """
    Health check endpoint
    """
    @api.doc('health_check')
    def get(self):
        """
        Check if the API is running
        """
        return {'status': 'ok'}


@api.route('/echo')
class Echo(Resource):
    """
    Echo endpoint for testing POST requests
    """
    @api.doc('echo_post')
    def post(self):
        """
        Echo back the data sent in the request body
        """
        data = request.get_json(force=True)
        return {'echo': data}


@api.route('/stats')
class Stats(Resource):
    """
    Statistics endpoint
    """
    @api.doc('get_stats')
    def get(self):
        """
        Get count of all geographic entities
        """
        try:
            return {
                'countries': len(countries.read()),
                'states': len(states.read()),
                'cities': len(cities.read()),
                'counties': len(counties.read()),
                'prompts': len(prompts.read())
            }, 200
        except Exception as e:
            return {'error': str(e)}, 500


@api.route(PROMPTS_EP)
class Prompts(Resource):
    @api.expect(prompt_list_parser)
    def get(self):
        args = prompt_list_parser.parse_args()
        ptype = args.get('type')
        return {'prompts': prompts.read(prompt_type=ptype)}, 200

    def post(self):
        try:
            data = request.get_json(force=True) or {}
            new_id = prompts.create(data)
            return {'id': new_id,
                    'message': 'Prompt created successfully'}, 201
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500


@api.route(QUIZ_QUESTIONS_EP)
class QuizQuestions(Resource):
    @api.expect(quiz_parser)
    def get(self):
        try:
            args = quiz_parser.parse_args()
            ptype = args['type']

            count_raw = args.get('count', 5)
            try:
                count = int(count_raw)
            except (TypeError, ValueError):
                count = 5

            qs = prompts.random_questions(ptype, count)
            return {'questions': qs}, 200

        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500


@api.route('/countries')
class Countries(Resource):
    """
    Endpoints for managing countries
    """
    @api.doc('get_countries')
    def get(self):
        """
        Get all countries
        """
        try:
            all_countries = countries.read()
            sorted_countries = sorted(all_countries,
                                      key=lambda x: x.get('name', ''))
            return {'countries': sorted_countries}, 200
        except Exception as e:
            return {'error': str(e)}, 500

    @api.doc('create_country')
    def post(self):
        """
        Create a new country
        """
        try:
            data = request.get_json(force=True)
            new_id = countries.create(data)
            return {'id': new_id,
                    'message': 'Country created successfully'}, 201
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500


@api.route('/countries/<string:country_id>')
class Country(Resource):
    """
    Endpoints for managing a specific country
    """
    @api.doc('get_country')
    def get(self, country_id):
        """
        Get a specific country by ID
        """
        try:
            country = countries.read(country_id)
            if country:
                return country, 200
            else:
                return {'error': 'Country not found'}, 404
        except Exception as e:
            return {'error': str(e)}, 500

    @api.doc('update_country')
    def put(self, country_id):
        """
        Update a specific country by ID
        """
        try:
            data = request.get_json(force=True)
            countries.update(country_id, data)
            return {'message': 'Country updated successfully'}, 200
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500

    @api.doc('delete_country')
    def delete(self, country_id):
        """
        Delete a specific country by ID
        """
        try:
            countries.delete(country_id)
            return {'message': 'Country deleted successfully'}, 200
        except ValueError as e:
            return {'error': str(e)}, 404
        except Exception as e:
            return {'error': str(e)}, 500


@api.route('/states')
class States(Resource):
    """
    Endpoints for managing states
    """
    @api.doc('get_states')
    def get(self):
        """
        Get all states
        """
        try:
            all_states = states.read()
            sorted_states = sorted(all_states,
                                   key=lambda x: x.get('name', ''))
            return {'states': sorted_states}, 200
        except Exception as e:
            return {'error': str(e)}, 500

    @api.doc('create_state')
    def post(self):
        """
        Create a new state
        """
        try:
            data = request.get_json(force=True)
            new_id = states.create(data)
            return {'id': new_id, 'message': 'State created successfully'}, 201
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500


@api.route('/states/<string:state_id>')
class State(Resource):
    """
    Endpoints for managing a specific state
    """
    @api.doc('get_state')
    def get(self, state_id):
        """
        Get a specific state by ID
        """
        try:
            state = states.read(state_id)
            if state:
                return state, 200
            else:
                return {'error': 'State not found'}, 404
        except Exception as e:
            return {'error': str(e)}, 500

    @api.doc('update_state')
    def put(self, state_id):
        """
        Update a specific state by ID
        """
        try:
            data = request.get_json(force=True)
            states.update(state_id, data)
            return {'message': 'State updated successfully'}, 200
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500

    @api.doc('delete_state')
    def delete(self, state_id):
        """
        Delete a specific state by ID
        """
        try:
            states.delete(state_id)
            return {'message': 'State deleted successfully'}, 200
        except ValueError as e:
            return {'error': str(e)}, 404
        except Exception as e:
            return {'error': str(e)}, 500


@api.route('/cities')
class Cities(Resource):
    """
    Endpoints for managing cities
    """
    @api.doc('get_cities')
    def get(self):
        """
        Get all cities
        """
        try:
            all_cities = cities.read()
            sorted_cities = sorted(all_cities,
                                   key=lambda x: x.get('name', ''))
            return {'cities': sorted_cities}, 200
        except Exception as e:
            return {'error': str(e)}, 500

    @api.doc('create_city')
    def post(self):
        """
        Create a new city
        """
        try:
            data = request.get_json(force=True)
            new_id = cities.create(data)
            return {'id': new_id, 'message': 'City created successfully'}, 201
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500


@api.route('/cities/<string:city_id>')
class City(Resource):
    """
    Endpoints for managing a specific city
    """
    @api.doc('get_city')
    def get(self, city_id):
        """
        Get a specific city by ID
        """
        try:
            city = cities.read(city_id)
            if city:
                return city, 200
            else:
                return {'error': 'City not found'}, 404
        except Exception as e:
            return {'error': str(e)}, 500

    @api.doc('update_city')
    def put(self, city_id):
        """
        Update a specific city by ID
        """
        try:
            data = request.get_json(force=True)
            cities.update(city_id, data)
            return {'message': 'City updated successfully'}, 200
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500

    @api.doc('delete_city')
    def delete(self, city_id):
        """
        Delete a specific city by ID
        """
        try:
            cities.delete(city_id)
            return {'message': 'City deleted successfully'}, 200
        except ValueError as e:
            return {'error': str(e)}, 404
        except Exception as e:
            return {'error': str(e)}, 500


@api.route('/counties')
class Counties(Resource):
    """
    Endpoints for managing counties
    """
    @api.doc('get_counties')
    def get(self):
        """
        Get all counties
        """
        try:
            all_counties = counties.read()
            sorted_counties = sorted(all_counties,
                                     key=lambda x: x.get('name', ''))
            return {'counties': sorted_counties}, 200
        except Exception as e:
            return {'error': str(e)}, 500

    @api.doc('create_county')
    def post(self):
        """
        Create a new county
        """
        try:
            data = request.get_json(force=True)
            new_id = counties.create(data)
            return {'id': new_id,
                    'message': 'County created successfully'}, 201
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500


@api.route('/counties/<string:county_id>')
class County(Resource):
    """
    Endpoints for managing a specific county
    """
    @api.doc('get_county')
    def get(self, county_id):
        """
        Get a specific county by ID
        """
        try:
            county = counties.read(county_id)
            if county:
                return county, 200
            else:
                return {'error': 'County not found'}, 404
        except Exception as e:
            return {'error': str(e)}, 500

    @api.doc('update_county')
    def put(self, county_id):
        """
        Update a specific county by ID
        """
        try:
            data = request.get_json(force=True)
            state_code = data.get('STATE_CODE') or data.get('state_code', '')
            counties.update(county_id, state_code, data)
            return {'message': 'County updated successfully'}, 200
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500

    @api.doc('delete_county')
    def delete(self, county_id):
        """
        Delete a specific county by ID
        """
        try:
            counties.delete(county_id)
            return {'message': 'County deleted successfully'}, 200
        except ValueError as e:
            return {'error': str(e)}, 404
        except Exception as e:
            return {'error': str(e)}, 500
