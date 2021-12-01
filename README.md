План работ.

0. Прочитать весь канал project в слак, выписать все нужные ссылки и вопросы.
1. Добавить вывод поля amount в ингредиент;
2. Добавить автоматическое добавление requst.user в качестве автора рецепта;
3. Поле author - есть вложенный сериализатор UserCustomSerializer. 
    Есть проблема: поле is_subscribed не срабатывает, когда косвенно вызывается
    этот сериализатор: 
                - при подписке на пользователя (вроде, РАБОТАЕТ);
                - при просмотре рецептов (вроде, РАБОТАЕТ)
5. При подписке на автора и просмотре подписчиков в ответе есть поле 
    recipes, причем не все поля отображаются (возможно нужен свой сериализатор) (РАБОТАЕТ)
6. Проверить в тех же подписках, работает ли recipe_count (РАБОТАЕТ).
4. Проверить, что все с рецептами хорошо, все добавляется и работает. 
7. Прописать урлы, вьюхи, сериализаторы для избранного и списка покупок. 
    (по аналогии с подписками на авторов).
8. Прописать action в /recipes с путем /recipes/download_shopping_cart/. 
    Берет все ингредиенты из всех моих рецептов, убирает повторяющиеся, 
    суммируя их количества. Выдает файл в .pdf или .txt (Яйцо куриное (шт) — 5)
13. Прописать все пермишены и уровни доступа согласно документации

9. Реализовать фильтрацию по тегам.
10. Поиск ингредиентов по полю name регистронезависимо, по вхождению 
    в начало названия.
11. Воспользуйся стандартным пагинатором DjangoRestFramework. Переопределить 
    название поля, отвечающего за количество результатов в выдаче.
12. Рецепты на всех страницах сортируются по дате публикации. Новые сначала
14. Обработка ошибки 404.
15. На странице рецепта вывести общее число добавлений этого рецепта в избранное.
16. Подключить как-то фронт, чтобы проверить работоспособность проекта.
17. Провести рефакторинг кола, если останется время. actions и разные методы
    имеют схожие коды, надо  избегать дублирования.