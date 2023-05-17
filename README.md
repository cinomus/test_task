## Документация
Создан REST API сервер игры 'Жизнь', используя библиотеки asyncio и psycopg.

Запуск:
```
python main.py
```

Urls:
    
   - GET `/` - возвращает пустое поле игры.
Inputs: None
Returns: {'field':[]}
   - GET `/games/{game_id}` - возвращает все игры.
Inputs: None
Returns: {'field':[]}
   - GET `/games/{game_id}/steps/{step_number}` - возвращает поле определенное поколение игры.
   - POST `/games` - принимает измененное поле, с произвольно заполненными клетками. Возвращает id игры.
   - POST `/games/{game_id}/steps` - создает и возвращает следующее поколение.