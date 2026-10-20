# white-sub

Объединённая подписка V2Ray для клиента V2Box. Скрипт скачивает публичные списки белых конфигураций из [igareck/vpn-configs-for-russia](https://github.com/igareck/vpn-configs-for-russia) (ветка `main`), оставляет только строки прокси (`vless://`, `vmess://`, `trojan://`, `ss://`, `hysteria2://`, `hy2://`, `tuic://`), убирает дубликаты и публикует один файл.

Обновление запускается каждый час и вручную. Если источник пустой или недоступен, он пропускается. Пустой результат не затирает уже опубликованный список.

## Ссылки на подписку

- https://raw.githack.com/Arthurnsk/white-sub/main/sub.txt
- https://cdn.jsdelivr.net/gh/Arthurnsk/white-sub@main/sub.txt
- https://raw.githubusercontent.com/Arthurnsk/white-sub/main/sub.txt
- https://translate.yandex.ru/translate?url=https://raw.githubusercontent.com/Arthurnsk/white-sub/main/sub.txt&lang=de-de

`sub.txt` — обычный список URI, по одному на строку. `sub_b64.txt` — тот же список в Base64 одной строкой.

## Как добавить в V2Box

1. Откройте V2Box.
2. На экране конфигураций нажмите «+».
3. Выберите **Add Subscription**.
4. Вставьте одну из ссылок выше и сохраните подписку.
5. Включите **auto update**, чтобы список обновлялся сам.
6. Для подключения выберите **Auto** или **Smart Connect**.
