import asyncio
import json
from typing import List

import psycopg
from aiohttp import web



class GameOfLife:
    default_height = 16
    default_width = 16

    async def get_game(self):
        pass

    async def tick(self):
        pass

    async def get_board(self):
        pass


game_engine = GameOfLife()


# Создание таблицы для хранения игр и их ходов


class StartGameReq:
    board: List[List[int]]


async def initial_game(request):
    return web.json_response({'board': await init_board()})


async def start_game(request):
    data: StartGameReq = await request.json()
    print(data)
    async with await psycopg.AsyncConnection.connect('postgresql://admin:admin@localhost:5432/postgres') as conn:
        async with conn.cursor() as cur:
            cur.execute("INSERT INTO games (status) VALUES (%s)", ('in_process',))
            conn.commit()
            game_id = cur.fetchone()[0]

            cur.execute("INSERT INTO game_steps (game_id, number, state) VALUES (%s, %s, %s)",
                        (game_id, 0, str(game_field)))
            conn.commit()

    # Создать игру
    # Сохранить первый шаг из полученного поля
    # Определить соседей всех клеток
    # Сохранить новое полученное поле
    # Отдать новое поле на клиент
    response = {'message': 'Game started.'}
    return web.json_response(response)


async def tick_game(request):
    game_id = request.rel_url.query.get('game_id', None)
    game_engine.get_game(game_id)
    game_engine.tick()
    current_board = game_engine.get_board()
    response = {'board': current_board.to_list()}
    return jsonify(response), 200


app = web.Application()
app.add_routes([
    web.get('/', initial_game),
    web.get('/games/{game_id}/steps/{step_id}', tick_game),
    # получение игры. Здесь в query параметрах должен приходить id игры и step. Returns: field, step

    web.post('/games/{game_id}/steps', tick_game),
    # получение игры. Здесь в query параметрах должен приходить id игры и step. Returns: field, step
    web.post('/games', start_game),  # создание новой игры. Returns: field, step

])
