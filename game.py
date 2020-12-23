import json
import jsonschema
from jsonschema import validate

NUMBER_OF_PLAYERS = 2

schema = {
    'type': 'object',
    'properties': {
        'players': {
            'type': 'array',
            'minItems': NUMBER_OF_PLAYERS,
            'maxItems': NUMBER_OF_PLAYERS,
            'items': [
                {
                    'type': 'object',
                    'properties': {
                        'username': {'type': 'string'},
                        'answer': {'type': 'string'}
                    },
                    'required': [
                        'username',
                        'answer'
                    ],
                    'additionalProperties': False
                }
            ]
        }
    },
    'required': [
        'players'
    ]
}


def create_player(username, answer, client):
    return Player(username, answer, client)


def parse_data(data):
    players = []
    for player_data in data['players']:
        player = Player(player_data['username'], player_data['answer'], None)
        players.append(player)
    return players


def init_players():
    players = []
    answer = ''
    for i in range(NUMBER_OF_PLAYERS):
        players.append(create_player(f'Player {i}', answer, None))
    return players


def validate_json(data):
    try:
        validate(instance=data, schema=schema)
    except jsonschema.exceptions.ValidationError:
        return False
    return True


def load_game_from_json(json_file_path):
    with open(json_file_path) as json_file:
        try:
            data = json.load(json_file)
            if validate_json(data):
                return data
        except json.decoder.JSONDecodeError:
            pass
    return None


def dump_game_to_json(players, json_file_path):
    data = {'players': []}
    for player in players:
        data['players'].append(player.to_dict())
    with open(json_file_path, 'w') as output:
        json.dump(data, output, indent=4)


class Player:
    def __init__(self, username, answer, client_socket):
        self.username = username
        self.answer = answer
        self.client_socket = client_socket

    def __str__(self):
        return f'Player username: {self.username}, answer: {self.answer}'

    def get_answer(self):
        return self.answer

    def move(self, answer):
        self.answer = answer

    def to_dict(self):
        return {
            'username': self.username,
            'answer': self.answer
        }
