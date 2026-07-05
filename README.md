# Bot Discord: Muzyka + Ranking

Bot gra muzykę (wyszukiwanie, linki YouTube, pojedyncze utwory i całe playlisty
Spotify), potrafi siedzieć 24/7 na wybranym kanale głosowym i grać playlistę
w kółko, oraz prowadzi ranking aktywności (wiadomości + minuty na kanałach
głosowych) z ładną grafiką rangi pod `/ranga`.

## Architektura: bot + Lavalink (dwie usługi)

Odtwarzanie muzyki idzie przez **Lavalink** - osobny, mały serwer (napisany w
Javie), który robi całe wyszukiwanie/streamowanie z YouTube. To rozwiązanie,
którego używa większość dużych botów muzycznych, bo jest dużo bardziej
odporne na blokady YouTube niż odtwarzanie bezpośrednio z kodu bota - a te
blokady prawie zawsze uderzają w boty hostowane w chmurze (Railway, Heroku
itp.), bo YouTube rozpoznaje i ogranicza adresy IP centrów danych.

To oznacza, że wdrażasz **dwie usługi w tym samym projekcie Railway**:
1. **bot** (główny kod Pythona w tym repo)
2. **lavalink** (folder `lavalink/` w tym repo - osobny serwer)

Obie instrukcje wdrożenia są niżej (sekcje 4 i 5).

## Komendy

| Komenda | Opis |
|---|---|
| `/graj <zapytanie>` | Dodaje do kolejki utwór (nazwa, link YouTube, link Spotify, a nawet link do playlisty) |
| `/playlista <link>` | Dodaje całą playlistę (Spotify lub YouTube) do kolejki |
| `/pomin` | Pomija aktualny utwór |
| `/pauza` / `/wznow` | Pauza / wznowienie |
| `/kolejka` | Pokazuje aktualną kolejkę |
| `/stop` | Zatrzymuje muzykę i bot opuszcza kanał (niedostępne gdy włączony tryb 24/7) |
| `/ranga [użytkownik]` | Wysyła grafikę z rangą, poziomem i statystykami |
| `/profil [użytkownik]` | Rozbudowany profil (embed): ranga, poziom, wiadomości, czas głosowy, data dołączenia |
| `/top` | Ranking top 10 serwera |
| `/rolaadmina <rola>` | *(Zarządzaj serwerem)* Ustawia rolę uprawnioną do zarządzania botem |
| `/kanalpoziomow <kanał>` | *(rola admina bota)* Kanał, na który wysyłane są powiadomienia o awansie poziomu |
| `/autoplay24_7 wlacz:<True/False> kanal:... playlista:...` | *(rola admina bota)* Tryb 24/7 - bot siedzi na kanale i gra playlistę w kółko |
| `/rolapoziom <poziom> <rola>` | *(rola admina bota)* Rola nadawana automatycznie od danego poziomu |
| `/usunrolepoziom <poziom>` | *(rola admina bota)* Usuwa regułę roli za poziom |
| `/listarole` | Pokazuje wszystkie ustawione role za poziomy |

**Punktacja i poziomy:** 1 wiadomość = `POINTS_PER_MESSAGE` pkt (domyślnie 1),
1 minuta na głosowym = `POINTS_PER_VOICE_MINUTE` pkt (domyślnie 1). Poziom =
suma punktów // `LEVEL_POINTS` (domyślnie 100 pkt/poziom). Wszystko
konfigurowalne w `.env`. Żeby zapobiec spamowaniu rankingu, wiadomości liczą
się do punktów **co najwyżej raz na 2 minuty** na osobę (`MESSAGE_COOLDOWN_SECONDS`
w `config.py`) - pisanie częściej nie daje dodatkowych punktów, ale nie blokuje
samego pisania na czacie.

**Rola administracyjna bota:** zaraz po dodaniu bota na serwer, osoba z
uprawnieniem *Zarządzaj serwerem* powinna wywołać `/rolaadmina @Rola`, żeby
ustalić, kto może zarządzać botem (autoplay, kanał poziomów, role za poziomy).
Dopóki nikt tego nie ustawi, tymi komendami może się posługiwać każdy z
uprawnieniem *Zarządzaj serwerem*. Administratorzy serwera mają dostęp zawsze.

**Status kanału głosowego:** gdy bot gra muzykę, ustawia też natywny
"status kanału głosowego" Discorda (to samo pole, które widać pod nazwą
kanału głosowego) na tytuł granego utworu, i czyści go, gdy przestaje grać.

---

## 1. Zakładanie bota na Discordzie

1. Wejdź na https://discord.com/developers/applications → **New Application**.
2. Zakładka **Bot** → **Reset Token** → skopiuj token (to Twój `DISCORD_TOKEN`).
3. Tam samo włącz **Privileged Gateway Intents**:
   - `SERVER MEMBERS INTENT`
   - `MESSAGE CONTENT INTENT`
4. Zakładka **OAuth2 → URL Generator**:
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: `Send Messages`, `Read Message History`, `Connect`,
     `Speak`, `Attach Files`, `Embed Links`, `View Channels`, `Manage Channels`
     (to ostatnie tylko po to, żeby bot mógł ustawiać "status kanału głosowego"
     z aktualnie graną piosenką), `Manage Roles` (do nadawania ról za poziomy)
   - Skopiuj wygenerowany link i otwórz go, żeby zaprosić bota na swój serwer.

## 2. Spotify - NIE jest wymagana żadna rejestracja

Bot obsługuje linki i playlisty Spotify "z pudełka", bez zakładania żadnej
aplikacji ani kluczy API - korzysta z darmowej, publicznej metody (tego
samego mechanizmu, którego używa strona z podglądem linku Spotify).
Wystarczy, że playlista jest **publiczna**.

Jeśli mimo to wolisz użyć oficjalnego, zarejestrowanego API Spotify (może
być trochę stabilniejsze przy bardzo dużym obciążeniu):
1. Wejdź na https://developer.spotify.com/dashboard → **Create app**.
2. Redirect URI możesz wpisać `http://localhost:3000` (nieużywane, ale wymagane).
3. Skopiuj `Client ID` i `Client Secret` z **Settings** aplikacji i wpisz je
   jako `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET` w `.env` / Railway
   Variables - bot automatycznie ich użyje zamiast darmowej metody.

## 3. Uruchomienie lokalnie

Potrzebujesz też lokalnie działającego Lavalinka (Java 17+):

```bash
# Pobierz Lavalink.jar z https://github.com/lavalink-devs/Lavalink/releases
# Umieść je w folderze lavalink/ obok application.yml, potem:
cd lavalink
java -jar Lavalink.jar
```

W drugim terminalu uruchom bota:

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Skopiuj `.env.example` do `.env`, uzupełnij `DISCORD_TOKEN` (domyślne wartości
`LAVALINK_HOST=localhost` / `LAVALINK_PORT=2333` pasują do lokalnego Lavalinka
z domyślnym `application.yml`), następnie:

```bash
python bot.py
```

## 4. Wdrożenie bota na Railway przez GitHub

1. Wrzuć ten cały folder jako repozytorium na GitHub (np. przez GitHub Desktop
   albo:
   ```bash
   git init
   git add .
   git commit -m "Discord music + ranking bot"
   git branch -M main
   git remote add origin https://github.com/TWOJ_LOGIN/TWOJE_REPO.git
   git push -u origin main
   ```
   — plik `.gitignore` już dba o to, żeby `.env` i baza danych NIE trafiły do repo).

2. Wejdź na https://railway.app → **New Project** → **Deploy from GitHub repo**
   → wybierz swoje repozytorium. To będzie usługa **bota** (Root Directory
   zostaw domyślne, czyli główny folder repo).

3. W zakładce **Variables** tej usługi dodaj:
   - `DISCORD_TOKEN`
   - `DB_PATH` = `/data/rankings.db` *(ważne, patrz punkt niżej o Volume)*
   - `LAVALINK_HOST`, `LAVALINK_PORT`, `LAVALINK_PASSWORD` - uzupełnisz je
     PO wdrożeniu usługi Lavalink w sekcji 5 (na razie możesz zostawić puste)
   - *(opcjonalnie)* `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET`, jeśli
     chcesz użyć oficjalnego API Spotify zamiast domyślnej darmowej metody

4. **Trwałość rankingu (Volume):** domyślny dysk na Railway jest kasowany przy
   każdym redeployu. Żeby ranking się nie zerował:
   - Wejdź w usługę bota → zakładka **Volumes** → **New Volume**
   - Mount path: `/data`
   - Dzięki `DB_PATH=/data/rankings.db` (krok 3) baza będzie zapisywana na
     tym trwałym dysku.

5. Railway wykryje `nixpacks.toml` (instaluje Pythona) oraz `Procfile`
   (uruchamia `python bot.py`) automatycznie.

## 5. Wdrożenie serwera Lavalink na Railway

1. W TYM SAMYM projekcie Railway kliknij **New** → **GitHub Repo** → wybierz
   to samo repozytorium jeszcze raz (druga usługa w projekcie).
2. Wejdź w ustawienia tej nowej usługi → **Settings** → **Root Directory**
   → ustaw na `lavalink` (Railway zbuduje ją z `lavalink/Dockerfile`).
3. W **Variables** tej usługi (Lavalinka) dodaj:
   - `LAVALINK_SERVER_PASSWORD` = jakieś swoje hasło (dowolny ciąg znaków)
4. Zdeployuj. W logach powinnaś/powinieneś zobaczyć, że Lavalink wystartował
   i załadował plugin YouTube.
5. Wróć do usługi **bota** (sekcja 4, punkt 3) i uzupełnij:
   - `LAVALINK_HOST` = prywatna domena tej usługi Lavalink w Railway, np.
     `lavalink.railway.internal` (Railway pokazuje ją w zakładce **Settings**
     → **Networking** → **Private Networking** tej usługi)
   - `LAVALINK_PORT` = `2333`
   - `LAVALINK_PASSWORD` = to samo hasło co w kroku 3
6. Zrób redeploy usługi bota (albo poczekaj na automatyczny, jeśli zmiana
   Variables go wywołała) - w logach bota powinno pojawić się
   `[lavalink] Połączono z węzłem Lavalink: ...`.

### Rozwiązywanie problemów z Lavalink/YouTube

YouTube regularnie zmienia sposób blokowania botów, więc czasem trzeba
dostroić `lavalink/application.yml`:
- Jeśli wyszukiwanie/odtwarzanie przestanie działać mimo poprawnej
  konfiguracji, sprawdź https://github.com/lavalink-devs/youtube-source
  po najnowszą wersję pluginu (podmień `VERSION` w `application.yml`) oraz
  ewentualnie po instrukcje włączenia `pot` (PoToken) lub `oauth`.
  Zmiana `application.yml` = redeploy usługi Lavalink.

## 6. Ustawienie trybu 24/7

Na Discordzie (jako administrator serwera albo osoba z rolą admina bota):

```
/autoplay24_7 wlacz:True kanal:#twoj-kanal-glosowy playlista:https://open.spotify.com/playlist/xxxxxxxx
```

Bot dołączy do kanału i będzie grał playlistę w kółko w losowej kolejności,
nawet po restarcie (konfiguracja zapisana jest w bazie danych). Żeby wyłączyć:

```
/autoplay24_7 wlacz:False
```

## 7. Powiadomienia o awansie poziomu

```
/kanalpoziomow kanal:#ogloszenia
```

Od tej pory przy każdym awansie poziomu bot wyśle tam grafikę z gratulacjami.

## Znane ograniczenia

- Czas na kanale głosowym liczony jest od momentu, gdy bot zaczyna działać —
  restart bota "gubi" trwające w danym momencie sesje głosowe (dolicza się
  dopiero przy kolejnym wyjściu z kanału po restarcie).
- Spotify Web API nie udostępnia surowego audio — utwory ze Spotify są
  dopasowywane i odtwarzane przez wyszukiwanie na YouTube, więc jakość/trafność
  dopasowania zależy od tego, co znajdzie się tam pod daną nazwą.
- Playlisty Spotify muszą być publiczne.
- Status kanału głosowego (pokazujący aktualnie grany utwór) wymaga, żeby bot
  miał uprawnienie "Zarządzaj kanałami" na danym kanale głosowym - w
  przeciwnym razie po prostu się nie ustawi (bot dalej gra muzykę normalnie).
- Żeby role za poziomy działały, rola bota (Ustawienia serwera → Role) musi
  być WYŻEJ na liście niż role, które ma nadawać - inaczej Discord nie
  pozwoli botowi ich przyznać.
- Od 2026 Discord wymaga szyfrowania end-to-end (DAVE) dla połączeń głosowych.
  `requirements.txt` zawiera `dave.py`, które to obsługuje.
- Darmowa metoda Spotify (bez klucza API) korzysta z publicznego,
  nieoficjalnego mechanizmu - może teoretycznie przestać działać, jeśli
  Spotify zmieni swój mechanizm. W takim wypadku ustaw
  `SPOTIFY_CLIENT_ID`/`SPOTIFY_CLIENT_SECRET`, żeby przełączyć się na
  oficjalne API (patrz punkt 2).
- YouTube regularnie zmienia mechanizmy blokowania botów - jeśli po jakimś
  czasie wyszukiwanie/odtwarzanie znów przestanie działać, to niemal zawsze
  kwestia zaktualizowania pluginu `youtube-source` w Lavalinku (patrz sekcja 5).