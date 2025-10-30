# Movie App (CLI + SQLite + Website)

A Python CLI application to manage personal movie collections with multi-user profiles, OMDb API lookups, and static website generation. Each user has an isolated library, and posters link to IMDb. Notes added to movies appear as a tooltip when hovering the poster.

## Features

- Multiple user profiles with isolated movie lists
- Add/delete/update/search/list movies
- Update notes shown as poster tooltips on the website
- Stats per user: average, median, best/worst rating
- Random movie picker and rating sort
- Website generator per user (e.g., `John.html`) with responsive grid
- OMDb integration for title, year, rating, poster, and IMDb ID
- Environment-based API key loading

## Tech stack

- Python 3.10+
- SQLite + SQLAlchemy (Core)
- Requests
- python-dotenv
- HTML/CSS for static website output

## Project structure

project_root/  
├─ movies.py # CLI entry point  
├─ README.md  
├─ requirements.txt  
├─ .gitignore  
├─ .env # contains OMDB_API_KEY  
├─ data/  
│ └─ movies.db # SQLite database  
├─ static/  
│ ├─ style.css  
│ └─ index_template.html
└─ movie_storage/  
├─ **init**.py  
└─ movie_storage_sql.py


## Getting started

### 1) Prerequisites
- Python 3.10 or newer
- Internet access for OMDb API

### 2) Install dependencies
python -m venv .venv

# Linux/macOS

source .venv/bin/activate

# Windows

# .venv\Scripts\activate

```bash
pip install -r requirements.txt
```
```bash
`requirements.txt` should include:
sqlalchemy  
requests  
python-dotenv
```

### 3) Configure environment
Create a `.env` file at the project root:
OMDB_API_KEY=your_omdb_api_key_here

### 4) First run
python movies.py
- Select or create a user profile at startup.
- Use the menu to add/list/update/delete movies, get stats, etc.
- Choose “Generate website” to build `<username>.html`.

## CLI usage

When you run `python movies.py`, you’ll see:

Menu:  
0. Exit

1.  List movies
2.  Add movies
3.  Delete movies
4.  Update movies
5.  Stats
6.  Random movie
7.  Search movie
8.  Movies sorted by rating
9.  Generate website
10.  Switch user


- Add a movie: fetches data from OMDb (Title/Year/IMDb rating/Poster/IMDb ID)
- Update movie: prompts for a note; saved to DB; shown as tooltip on poster hover
- Generate website: produces `<username>.html` using `static/index_template.html`

## Data model

Tables are created automatically if missing.

- `users`
  - `id INTEGER PRIMARY KEY AUTOINCREMENT`
  - `name TEXT UNIQUE NOT NULL`

- `movies`
  - `id INTEGER PRIMARY KEY AUTOINCREMENT`
  - `title TEXT NOT NULL`
  - `year INTEGER NOT NULL`
  - `rating REAL NOT NULL`
  - `poster_url TEXT`
  - `user_id INTEGER NOT NULL REFERENCES users(id)`
  - `note TEXT`
  - `imdb_id TEXT`

If you previously created `movies` without these columns, either run ALTER TABLEs or drop and recreate the table during development.

## Website generation

- Template: `static/index_template.html` must contain the placeholders:
  - `__TEMPLATE_TITLE__`
  - `__TEMPLATE_MOVIE_GRID__`
- Output: `<username>.html`
- Each poster is wrapped in an anchor to IMDb:
  - `<a href="https://www.imdb.com/title/{imdb_id}/" target="_blank" rel="noopener noreferrer">`
- Poster tooltip uses the movie note via the `title` attribute.
- CSS grid is defined in `static/style.css`.

Preview locally in a browser or run a simple server:
python -m http.server

# then open  [http://localhost:8000/](http://localhost:8000/)<username>.html

## Implementation notes - API key loading:
from dotenv import load_dotenv  
import os  
load_dotenv()  
API_KEY = os.getenv("OMDB_API_KEY")
- HTML escaping for safe tooltips:
import html  
note = html.escape(info.get("note") or "")
- Always pass `user_id` into storage functions (list/add/delete/update/stats/search/sort/random/generate).

## Common issues and fixes

- “Not an executable object” with SQLAlchemy:
- Wrap raw SQL strings with `text("...")` before executing.
- “table movies has no column named user_id”:
- Your table predates multi-user. Migrate (ALTER TABLE) or drop/recreate during dev.
- `AttributeError: 'NoneType' object has no attribute 'replace'` from `html.escape`:
- Ensure `html.escape(info.get("note") or "")` so `None` becomes an empty string.
- Posters not showing:
- Ensure `poster_url` is stored and your HTML uses it; fallback to a placeholder if missing.
- Links not opening in a new tab or security warnings:
- Use `target="_blank" rel="noopener noreferrer"` on external links.

## Contributing

- Open issues/PRs with clear descriptions.
- Keep functions user-specific by passing `user_id`.
- Avoid dropping tables in production code.

## License

MIT (or your preferred license). Add a `LICENSE` file if distributing publicly.

## Acknowledgments

- OMDb API for movie metadata and posters.
