"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""
# from http import HTTPStatus

from flask import Flask
from flask_restx import Resource, Api, reqparse
from flask import request
from flask_cors import CORS
import bcrypt

import countries.queries_countries as countries
from countries.hints import build_country_hints
import states.queries_states as states
import cities.queries_cities as cities
from cities.hints import build_cities_hints
import counties.queries_counties as counties
import prompts.queries_prompts as prompts
import puzzles.queries_puzzles as puzzles
import scores.queries_scores as scores_mod
from users import queries_users as qu
import friends.queries_friends as friends_mod

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
PUZZLES_EP = '/puzzles'
PUZZLE_QUIZ_EP = '/puzzle/quiz'
SCORES_EP = '/scores'
FRIENDS_EP = '/friends'
SCORES_FRIENDS_EP = '/scores/friends'
LEADERBOARD_FILTERS_EP = '/leaderboard/filters'

prompt_list_parser = reqparse.RequestParser()
prompt_list_parser.add_argument('type', required=False, location='args')

quiz_parser = reqparse.RequestParser()
quiz_parser.add_argument('type', required=True, location='args')
quiz_parser.add_argument('count', required=False, location='args',
                         type=int, default=5)

puzzle_list_parser = reqparse.RequestParser()
puzzle_list_parser.add_argument('entity_type',
                                required=False, location='args')

puzzle_quiz_parser = reqparse.RequestParser()
puzzle_quiz_parser.add_argument('entity_type',
                                required=True, location='args')
puzzle_quiz_parser.add_argument('count',
                                required=False, location='args', default=1)


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


@api.route(PUZZLES_EP)
class Puzzles(Resource):
    @api.expect(puzzle_list_parser)
    def get(self):
        args = puzzle_list_parser.parse_args()
        entity_type = args.get('entity_type')
        return {'puzzles': puzzles.read(entity_type=entity_type)}, 200

    def post(self):
        try:
            data = request.get_json(force=True) or {}
            new_id = puzzles.create(data)
            return {'id': new_id,
                    'message': 'Puzzle created successfully'}, 201
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500


@api.route(PUZZLE_QUIZ_EP)
class PuzzleQuiz(Resource):
    @api.expect(puzzle_quiz_parser)
    def get(self):
        try:
            args = puzzle_quiz_parser.parse_args()
            entity_type = args['entity_type']

            count_raw = args.get('count', 1)
            try:
                count = int(count_raw)
            except (TypeError, ValueError):
                count = 1

            qs = puzzles.random_puzzles(entity_type, count)
            return {'puzzles': qs}, 200

        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500


@api.route(SCORES_EP)
class Scores(Resource):
    def get(self):
        return {'scores': scores_mod.read()}, 200

    def post(self):
        try:
            data = request.get_json(force=True) or {}
            new_id = scores_mod.create(data)
            return {'id': new_id,
                    'message': 'Score created successfully'}, 201
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500


@api.route(FRIENDS_EP)
class Friends(Resource):
    def get(self):
        user_id = request.args.get('user_id')
        if not user_id:
            return {'error': 'user_id is required'}, 400
        try:
            friend_ids = friends_mod.read(user_id)
            friends_list = []
            for fid in friend_ids:
                for user in qu.read():
                    if user.get(qu.ID) == fid:
                        friends_list.append({
                            'id': fid,
                            'email': user.get(qu.EMAIL),
                        })
                        break
            return {'friends': friends_list}, 200
        except Exception as e:
            return {'error': str(e)}, 500

    def post(self):
        try:
            data = request.get_json(force=True) or {}
            user_id = data.get('user_id')
            friend_email = data.get('friend_email', '').strip().lower()
            if not user_id or not friend_email:
                return {'error': 'user_id and friend_email are required'}, 400
            friend = qu.find_by_email(friend_email)
            if not friend:
                return {'error': 'No user found with that email'}, 404
            friend_id = friend.get(qu.ID)
            friends_mod.create(user_id, friend_id)
            return {
                'message': 'Friend added',
                'friend': {
                    'id': friend_id,
                    'email': friend.get(qu.EMAIL),
                },
            }, 201
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500

    def delete(self):
        try:
            data = request.get_json(force=True) or {}
            user_id = data.get('user_id')
            friend_id = data.get('friend_id')
            if not user_id or not friend_id:
                return {'error': 'user_id and friend_id are required'}, 400
            friends_mod.delete(user_id, friend_id)
            return {'message': 'Friend removed'}, 200
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500


@api.route(SCORES_FRIENDS_EP)
class ScoresFriends(Resource):
    def get(self):
        user_id = request.args.get('user_id')
        if not user_id:
            return {'error': 'user_id is required'}, 400
        try:
            friend_ids = friends_mod.read(user_id)
            all_ids = friend_ids + [user_id]
            scores = scores_mod.read_by_user_ids(all_ids)
            return {'scores': scores}, 200
        except Exception as e:
            return {'error': str(e)}, 500


@api.route(LEADERBOARD_FILTERS_EP)
class LeaderboardFilters(Resource):
    def get(self):
        return {
            'filters': [
                {'value': 'all', 'label': 'All Players'},
                {'value': 'friends', 'label': 'Friends Only'},
            ]
        }, 200


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
            countries_with_hints = []
            for country in sorted_countries:
                country_payload = dict(country)
                country_payload['hints'] = build_country_hints(country)
                countries_with_hints.append(country_payload)
            return {'countries': countries_with_hints}, 200
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
            cities_with_hints = []
            for city in sorted_cities:
                city_payload = dict(city)
                city_payload['hints'] = build_cities_hints(city)
                cities_with_hints.append(city_payload)
            return {'cities': cities_with_hints}, 200
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


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    if not data:
        return {"error": "Missing JSON body"}, 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return {"error": "Email and password are required"}, 400

    if len(password) < 6:
        return {"error": "Password must be at least 6 characters"}, 400

    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    try:
        qu.create({
            qu.EMAIL: email,
            qu.PASSWORD: hashed_password,
        })
    except ValueError as e:
        return {"error": str(e)}, 409

    return {"message": "Account created successfully"}, 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return {"error": "Missing JSON body"}, 400
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return {"error": "Email and password are required"}, 400

    user = qu.find_by_email(email)
    if not user:
        return {"error": "Invalid email or password"}, 401

    stored_password = user.get(qu.PASSWORD, "")

    if not bcrypt.checkpw(
        password.encode("utf-8"),
        stored_password.encode("utf-8")
    ):
        return {"error": "Invalid email or password"}, 401

    return {
        "message": "Login successful",
        "user": {
            "id": user.get(qu.ID),
            "email": user.get(qu.EMAIL),
        }
    }, 200
