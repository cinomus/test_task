import asyncio
import json
from asyncio import StreamReader
import re

from game import GameOfLife


async def init_board_handler():
    return json.dumps({'field': await GameOfLife.init_board()})


async def start_game_handler(body):
    request_data = json.loads(body)
    game_id = await GameOfLife.start_game(request_data['field'])
    return json.dumps({'game_id': game_id})


async def get_game_handler(game_id):
    game_id, status = await GameOfLife.get_game(game_id)
    return json.dumps({'game_id': game_id, 'status': status})


async def get_game_step_handler(game_id, step_number):
    field = await GameOfLife.get_game_step(game_id, step_number)
    return json.dumps({'game_id': game_id, 'step_number': step_number, 'field': field})


async def next_step_handler(game_id):
    game_id, step_number, field = await GameOfLife.next_step(game_id)
    return json.dumps({'game_id': game_id, 'step_number': step_number, 'field': field})


async def send_response(writer, response):
    writer.write(response.encode())
    await writer.drain()
    writer.close()


async def handle_request(reader: StreamReader, writer):
    response = None
    try:
        raw_request = bytearray()
        while True:
            chunk = await reader.read(1024)
            reader.feed_eof()  # Не до конца понимаю как работает эта функция
            if not chunk:
                break
            raw_request += chunk
        request = raw_request.decode()
        method, path, version = request.split('\n')[0].split(' ')
        headers = (
            'HTTP/1.1 200 OK\n'
            'Content-Type: application/json\n\n'
        )

        if path == '/' and method == 'GET':  # Отдаем пустое поле при заходе на главную страницу
            response_data = await init_board_handler()
            response = headers + response_data + '\n'

        elif path == '/games' and method == 'POST':  # Начинаем игру
            body = request.split('\r\n\r\n')[1]
            response_data = await start_game_handler(body)
            response = headers + response_data + '\n'

        elif re.search(r'/games/(?P<game_id>\d+)/steps', path) and method == 'POST':  # Создание следующего шага
            game_id = re.search(r'/games/(?P<game_id>\d+)/steps', path).group('game_id')
            response_data = await next_step_handler(game_id)
            response = headers + response_data + '\n'

        elif re.search(r'/games/(?P<game_id>\d+)/steps/(?P<step_number>\d+)', path) and method == 'GET':
            match = re.search(r'/games/(?P<game_id>\d+)/steps/(?P<step_number>\d+)', path)
            game_id = match.group('game_id')
            step_number = match.group('step_number')
            response_data = await get_game_step_handler(game_id, step_number)
            response = headers + response_data + '\n'

        elif re.search(r'/games/(?P<game_id>\d+)', path) and method == 'GET':
            game_id = re.search(r'/games/(?P<game_id>\d+)', path).group('game_id')
            response_data = await get_game_handler(game_id)
            response = headers + response_data + '\n'

        else:
            headers = (
                'HTTP/1.1 404 Not Found\n'
                'Content-Type: text/plain\n\n'
                '404 Not Found'
            )
            response = headers
    except:
        headers = (
            'HTTP/1.1 500 Internal Server Error\n'
            'Content-Type: text/plain\n\n'
            '500 Internal Server Error'
        )
        response = headers
    finally:
        await send_response(writer, response)


async def run_server():
    server = await asyncio.start_server(handle_request, host='127.0.0.1', port=3000)
    async with server:
        await server.serve_forever()
