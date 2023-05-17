import asyncio
import sys
import psycopg

from server_asyncio import run_server


async def main():
    async with await psycopg.AsyncConnection.connect('postgresql://admin:admin@localhost:5432/postgres') as con:
        async with con.cursor() as cur:
            await cur.execute('''CREATE TABLE IF NOT EXISTS Games
                                       (id SERIAL PRIMARY KEY, status VARCHAR(50));''')
            await cur.execute('''CREATE TABLE IF NOT EXISTS GameSteps
                                       (id SERIAL PRIMARY KEY, number INTEGER, game_id INTEGER REFERENCES Games(id) ON DELETE CASCADE, field INTEGER[][] NOT NULL);''')


if __name__ == '__main__':
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
    asyncio.run(run_server())
