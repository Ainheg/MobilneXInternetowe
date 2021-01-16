# Czwarty kamień milowy
#### Logowanie za pomocą OAuth2.0 / auth0.com 
W aplikacji internetowej dla klienta jest dostępne pod normalnym formularzem logowania
Aplikacja dla kuriera przed otworzeniem właściwego okna wyświetla duży guzik, który prowadzi do logowania, nie jest to może zbyt piękne, ale całkiem skuteczne :)
#### Powiadomienia
Powiadomienia zrealizowałem w sposób wybitnie prosty (ktoś mógłby powiedzieć, że nawet prostacki), po stronie serwera/api po utowrzeniu paczki/zmianie statusu są tworzone rekordy w Redis o kluczach "notification:{username_nadawcy}:{uuid4}" z długością życia 11 sekund (aby wziąć poprawkę na dość wolną odpowiedź serwerów Heroku). Po stronie aplikacji klienta jest zaimplementowany endpoint "/notifications", który co 10 sekund jest odpytywany przez skrypt zawarty w pliku poll.js. 