import json
import socket
import game

BUFFER_SIZE = 2 ** 10
PORT = 9997
PLAYERS_COUNT = 2
ENCODING = 'utf-8'
END_CHARACTER = '\0'
JSON_FILE_PATH = 'saves.json'


def send(s, d):
    s.sendall((json.dumps(d) + END_CHARACTER).encode(ENCODING))


def receive(s):
    buffer = ""
    while not buffer.endswith(END_CHARACTER):
        buffer += s.recv(BUFFER_SIZE).decode(ENCODING)
    return json.loads(buffer[:-1])


def broadcast(p, d):
    for player in p:
        send(player.client_socket, d)


def exit_server(code, p, s):
    s.close()
    for player in p:
        player.client_socket.close()
    game.dump_game_to_json(players, JSON_FILE_PATH)
    print('Stopping the server')
    exit(code)


if __name__ == '__main__':
    try:
        print('Server is running')
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('', PORT))
        data = game.load_game_from_json(JSON_FILE_PATH)
        players = []
        if data is None:
            players = game.init_players()
        else:
            players = game.parse_data(data)
        server_socket.listen(1)
        for i, player in enumerate(players):
            client_socket = None
            address = None
            try:
                client_socket, address = server_socket.accept()
            except OSError:
                print(f'Connection aborted. Player number: {i}')
                exit_server(1, players, server_socket)
            print('Client connected: {}:{}'.format(*address))
            player.client_socket = client_socket
            send(client_socket, {
                'username': player.username,
                'action': 'begin' if data is None else 'continue'
            })
        print('All players are connected! List of players:')
        for player in players:
            print(player)
        game.dump_game_to_json(players, JSON_FILE_PATH)
        while True:
            for player in players:
                client_socket = player.client_socket
                send(client_socket, {
                    'action': 'move'
                })
                message = {'answer': 0}
                try:
                    message = receive(client_socket)
                except (ConnectionAbortedError, ConnectionResetError):
                    print('Connection aborted')
                    exit_server(1, players, server_socket)
                player.move(message['answer'])
                print(f'{player.username}: answer - {player.get_answer()}')
                send(client_socket, {
                    'answer': player.get_answer()
                })
            print('All the players did in the course, a list of players:')
            for player in players:
                print(player)
            if players[0].answer== 'y' and players[1].answer== 'y':
                broadcast(players, {
                    'action': 'end',
                    'type': 'yy'
                })
                print('The game is over! Both players went to jail!')
                break
            elif players[0].answer== 'n' and players[1].answer== 'n':
                broadcast(players, {
                    'action': 'end',
                    'type': 'nn'
                })
                print('The game is over! Both players went to jail!')
                break
            else:
                broadcast(players, {
                    'action': 'end',
                    'type': 'yn'
                })
                print(f'The game is over! ')
                break
            game.dump_game_to_json(players, JSON_FILE_PATH)
        game.dump_game_to_json([], JSON_FILE_PATH)

        exit_server(0, players, server_socket)
    except RuntimeError as error:
        print(f'Error occurred {str(error)}')
