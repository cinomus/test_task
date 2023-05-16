import asyncio
import json
from asyncio import StreamReader

import psycopg


async def init_board():
    return [[0 for _ in range(16)] for _ in range(16)]


async def start_game(field):
    async with await psycopg.AsyncConnection.connect('postgresql://admin:admin@localhost:5432/postgres') as conn:
        async with conn.cursor() as cur:
            # Создаем запись об игре в бд
            await cur.execute("INSERT INTO games (status) VALUES (%s) RETURNING id;", ('in_process',))
            # await conn.commit()
            # await cur.fetchone()
            game_id = (await cur.fetchone())[0]
            print(game_id)
            # Добавляем начальный шаг в бд
            await cur.execute("INSERT INTO game_steps (game_id, number, field) VALUES (%s, %s, %s)",
                              (game_id, 0, field))
            await conn.commit()

            return game_id


async def tick_game(game_id):
    async with await psycopg.AsyncConnection.connect('postgresql://admin:admin@localhost:5432/postgres') as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT id, number, field FROM game_steps WHERE game_id = %s AND number = (SELECT MAX(number) FROM game_steps WHERE game_id = %s)",
                (game_id, game_id))
            id, number, field = await cur.fetchone()
            # Делаем тик в игре
            await cur.execute("INSERT INTO game_steps (game_id, number, field) VALUES (%s, %s, %s)",
                              (game_id, number+1, field))
            print('state', state)


async def init_board_handler():
    print('init_board_handler')
    return json.dumps({'field': await init_board()})


async def start_game_handler(request):
    body = request.split('\r\n\r\n')[1]
    request_data = json.loads(body)
    game_id = await start_game(request_data['field'])
    field = await tick_game(game_id)

    return json.dumps({'field': {}})


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
            response_data = await start_game_handler(request)
            response = headers + response_data + '\n'
        else:
            headers = (
                'HTTP/1.1 404 Not Found\n'
                'Content-Type: text/plain\n\n'
                '404 Not Found'
            )
            response = headers
    except Exception as err:
        print(err)
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

# if __name__ == '__main__':
#     asyncio.run(run_server())
