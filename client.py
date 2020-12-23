import socket
from server import PORT, send, receive

BUFFER_SIZE = 2 ** 10


def exit_client(code, s):
    s.close()
    print('Stopping the client')
    exit(code)


if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            client_socket.connect((socket.gethostname(), PORT))
            break
        except (socket.error, OverflowError):
            pass
    message = {}
    try:
        message = receive(client_socket)
    except (ConnectionAbortedError, ConnectionResetError):
        exit_client(1, client_socket)
    username = message['username']
    print(f'You entered the game under the name {username}')
    if message['action'] == 'continue':
        print('Game continued from the last save')
    elif message['action'] == 'begin':
        print('A new game is started')
    else:
        exit_client(1, client_socket)
    answer = ''
    while True:
        try:
            message = receive(client_socket)
        except (ConnectionAbortedError, ConnectionResetError):
            exit_client(1, client_socket)
        if message['action'] == 'move':
            answer = input('Will you hand over your partner?. Enter y or n: ')
            while type(answer) != str:
                try:
                    answer = str(answer)
                    if answer != 'y' or answer !='n':
                        raise ValueError()
                except ValueError:
                    answer = input('Invalid input. Try again: ')
            send(client_socket, {
                'answer': answer
            })
            try:
                message = receive(client_socket)
            except (ConnectionAbortedError, ConnectionResetError):
                exit_client(1, client_socket)
            print(f'Your answer: {message["answer"]}. Wait for your turn')
        elif message['action'] == 'end':
            if message['type'] == 'yy':
                print('The game is over! You will go to jail for 2 years')
            elif message['type'] == 'nn':
                print('The game is over! You will go to jail for six months')
            elif message['type'] == 'yn' and answer == 'y':
                print('The game is over! You will be released')
            elif message['type'] == 'yn' and answer == 'n':
                print('The game is over! You will go to jail for 10 years')
            exit_client(0, client_socket)
