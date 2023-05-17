from copy import deepcopy

import psycopg


class GameOfLife:
    height = 16
    width = 16

    @classmethod
    async def init_board(cls):
        return [[0 for _ in range(cls.width)] for _ in range(cls.height)]

    @classmethod
    async def start_game(cls, field):
        async with await psycopg.AsyncConnection.connect('postgresql://admin:admin@localhost:5432/postgres') as conn:
            async with conn.cursor() as cur:
                await cur.execute("INSERT INTO Games (status) VALUES (%s) RETURNING id;", ('in_process',))
                game_id = (await cur.fetchone())[0]
                await cur.execute("INSERT INTO GameSteps (game_id, number, field) VALUES (%s, %s, %s)",
                                  (game_id, 0, field))
                return game_id

    @classmethod
    async def get_game(cls, game_id):
        async with await psycopg.AsyncConnection.connect('postgresql://admin:admin@localhost:5432/postgres') as conn:
            async with conn.cursor() as cur:
                await cur.execute('SELECT id, status FROM Games WHERE id=%s ', (game_id,))
                return await cur.fetchone()

    @classmethod
    async def get_game_step(cls, game_id, step_number):
        async with await psycopg.AsyncConnection.connect('postgresql://admin:admin@localhost:5432/postgres') as conn:
            async with conn.cursor() as cur:
                await cur.execute('SELECT field FROM GameSteps WHERE game_id=%s AND number=%s', (game_id, step_number))
                return await cur.fetchone()

    @classmethod
    async def next_step(cls, game_id):
        async with await psycopg.AsyncConnection.connect('postgresql://admin:admin@localhost:5432/postgres') as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT number, field FROM GameSteps WHERE game_id = %s AND number = (SELECT MAX(number) FROM GameSteps WHERE game_id = %s)",
                    (game_id, game_id))
                number, field = await cur.fetchone()

                new_field = deepcopy(field)

                for y in range(cls.height):
                    for x in range(cls.width):
                        neighbor_count = (
                                field[(y - 1) % cls.height][(x - 1) % cls.width]
                                + field[(y - 1) % cls.height][x]
                                + field[(y - 1) % cls.height][(x + 1) % cls.width]
                                + field[y][(x - 1) % cls.width]
                                + field[y][(x + 1) % cls.width]
                                + field[(y + 1) % cls.height][(x - 1) % cls.width]
                                + field[(y + 1) % cls.height][x]
                                + field[(y + 1) % cls.height][(x + 1) % cls.width]
                        )

                        if field[y][x] == 1 and neighbor_count < 2:
                            new_field[y][x] = 0
                        elif field[y][x] == 1 and neighbor_count > 3:
                            new_field[y][x] = 0
                        elif field[y][x] == 0 and neighbor_count == 3:
                            new_field[y][x] = 1

                await cur.execute(
                    "SELECT id, number, field FROM GameSteps WHERE game_id = %s AND field = %s::integer[][]",
                    (game_id, new_field))
                res = await cur.fetchone()
                if res is not None:
                    await cur.execute("UPDATE Games SET status = 'ended' WHERE id = %s", (game_id,))

                await cur.execute("INSERT INTO GameSteps (game_id, number, field) VALUES (%s, %s, %s) RETURNING *",
                                  (game_id, number + 1, new_field))
                return game_id, number + 1, new_field
