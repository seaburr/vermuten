# vermuten
German for "guess", vermuten is a very basic riddle/puzzle application. Upon server start, a config file that contains riddle information is loaded into memory and defines the riddles that a group of classmates must answer.

It is important to note that there is a single instance of this server so, if desired, multiple web browsers can be used to interact with the same game instance.

# Technologies
* Python 3.13 (language)
* Flask (web framework)
* Gunicorn (web server, one worker process with threads)
* Docker (container image published to `ghcr.io/seaburr/vermuten`)

# Configuration
Set `VERMUTEN_CONFIG` to a JSON config file within the application directory to load one game at start-up (the Docker image defaults to `demo.json`). See `demo.json` for the config format. Riddle images are served from `static/`, so `image_name` values must name files there.

Without `VERMUTEN_CONFIG`, `/` shows a setup page where a config file (up to 256 KB) can be uploaded; each upload starts its own game with its own link.

`PORT` sets the listening port in the Docker image (default `8080`).

Game state is held in memory, so run exactly one process. Restarting the server resets all games.

# Running
```bash
pip install -r requirements.txt -r requirements-dev.txt
make test     # python -m unittest
make lint     # black --check .
make run      # gunicorn on port 8080 with demo.json

docker build -t vermuten .
docker run --rm -p 8080:8080 vermuten
```

# Endpoints
## Game
### /
Redirects to the game when `VERMUTEN_CONFIG` is set; otherwise shows the setup page.

### /riddle/ and /riddle/&lt;game_id&gt;/
Returns the current riddle. Submit a guess with `?guess=...`.

### POST /setup
Upload a config (`file` form field). Returns `{"game_url": ...}`, or a 400 with `{"error": ...}` for invalid JSON or a config in the wrong shape (413 if it is too large).

## Progress Report
### /riddle/admin/progress (or /riddle/&lt;game_id&gt;/admin/progress)
Returns a status page.

## Progress Reset
### /riddle/admin/reset (or /riddle/&lt;game_id&gt;/admin/reset)
Resets game progress and redirects to the progress page.

## Health
### /healthz
Returns 200.

# License
Copyright 2021 seaburr

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.