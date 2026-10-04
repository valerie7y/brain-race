# Brain Race 🏁

A car-trivia race for the family. Live at **https://valerie7y.github.io/brain-race/**

- One self-contained `index.html` (no external dependencies). `sw.js` is an optional helper that caches the page so it still opens with no signal.
- Players: Anthony (Age 8), Liz (Age 12), Eugene (Expert). Names, levels, emoji/color, and the player list are editable in ⚙️ Settings.
- Scoring: 3 points with no hints, 2 with one hint, 1 with two. Missed questions can be stolen for 1 point.
- Question bank sources live in `src/` (`q8.txt`, `q12.txt`, `qadult.txt`; format: `category|question|hint1|hint2|answer|fun fact`). Rebuild with `python3 src/build.py`.
- Tests: `python3 test.py http://localhost:PORT/index.html` (Playwright, 390×844 viewport).
