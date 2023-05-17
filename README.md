## Документация
Создан REST API сервер игры 'Жизнь', используя библиотеки asyncio и psycopg.

Запуск:
```
python main.py
```

Urls:
    
   - GET `/` - возвращает пустое поле игры.

Inputs: `None`

Returns: `{'field':List[List[int]]}`

---------------
   - GET `/games/{game_id}` - возвращает все игры.

Inputs: `None`

Returns: `{'game_id':int, 'status':Typle['in process','ended']}`

---------------
   - GET `/games/{game_id}/steps/{step_number}` - возвращает поле определенное поколение игры.

Inputs: in url: `{'game_id':int, 'step_number':int}`

Returns: `{'game_id':int, 'step_number':int, 'field': List[List[int]]}`

---------------
   - POST `/games` - принимает измененное поле, с произвольно заполненными клетками. Возвращает id игры.

Inputs: in body: `{'field':List[List[int]]}`

Returns: `{'game_id':int}`

---------------
   - POST `/games/{game_id}/steps` - создает и возвращает следующее поколение.

Inputs: in url:`{'game_id':int}`

Returns: `{'game_id':int, 'step_number':int, 'field': List[List[int]]}`
