from sqlalchemy import create_engine, text
import requests
from dotenv import load_dotenv
import os
import random
import html

load_dotenv()

API_KEY = os.getenv("OMDB_API_KEY")

URL = "http://www.omdbapi.com/"


# Define the database URL
DB_URL = "sqlite:///data/movies.db"


# Create the engine
engine = create_engine(DB_URL, echo=False)


# Create the movies table if it does not exist
with engine.connect() as connection:
    connection.execute(text("DROP TABLE IF EXISTS movies"))
    connection.commit()
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """))
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            poster_url TEXT,
            user_id INTEGER NOT NULL,
            note TEXT,
            imdb_id TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """))
    connection.commit()


def select_or_create_user():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, name FROM users ORDER BY name"))
        users = result.fetchall()
        print("\nSelect a user profile:")
    for idx, user in enumerate(users, start=1):
        print(f"{idx}. {user[1]}")
    print(f"{len(users) + 1}. Create new user")
    choice = input("Enter choice: ").strip()
    try:
        choice = int(choice)
    except ValueError:
        print("Invalid choice, please enter a number.")
        return select_or_create_user()
    if 1 <= choice <= len(users):
        selected_user = users[choice - 1]
        return selected_user[0], selected_user[1]
    elif choice == len(users) + 1:
        name = input("Enter a new user: ").strip()
        if not name:
            print("Username cannot be empty")
            return select_or_create_user()
        with engine.connect() as conn:
            conn.execute(text(
              "INSERT INTO users (name) VALUES (:name)"),
              {"name": name}
            )
            conn.commit()
            user = conn.execute(text(
              "SELECT id, name FROM users WHERE name=:name"),
              {"name": name}
            ).fetchone()
        print(f"User '{name}' created and selected")
        return user[0], user[1]
    else:
        print("Invalid choice, try again")
        return select_or_create_user()
        

def stats(user_id):
    """Finding the avg, the median the best movie and the worst movie"""
    movies = list_movies(user_id)
    if not movies:
        print("No movies to display stats.")
        return
    ratings = []
    for record in movies.values():
        try:
            rating = float(record.get('rating', 0))
            if rating > 0:
                ratings.append(rating)
        except (TypeError, ValueError):
            continue
    if not ratings:
        print("No numeric ratings found")
        return
    avg = sum(ratings) / len(ratings)
    n = len(ratings)
    ratings.sort()
    mid = n // 2
    if n % 2 == 1:
        median = ratings[mid]
    else:
        median = (ratings[mid - 1] + ratings[mid]) / 2
    best_rating = max(ratings)
    worst_rating = min(ratings)
    best_titles = [title for title, rec in movies.items() if float(rec.get('rating', 0)) == best_rating]
    worst_titles = [title for title, rec in movies.items() if float(rec.get('rating', 0)) == worst_rating]
    print(f"Average rating: {avg:.1f}")
    print(f"Median rating: {median}")
    print(f"Best: {', '.join(best_titles)} ({best_rating})")
    print(f"Worst: {', '.join(worst_titles)} ({worst_rating})")



def random_movie(user_id):
    """Select a random movie from the database"""
    movies = list_movies(user_id)
    if not movies:
        print("No movies in your collection.")
        return
    title, info = random.choice(list(movies.items()))
    print(f"Random movie: {title} ({info['year']}): {info['rating']}")


def search_movie(user_id):
    """Search a movie """
    query = input("Enter part of movie name: ").lower()
    movies = list_movies(user_id)
    found = False
    for title, info in movies.items():
        if query in title.lower():
            print(f"{title} ({info['year']}): {info['rating']}")
            found = True
    if not found:
        print("No movies found matching your search.")


def sorted_by_rating(user_id):
    """Sort movies by their ratings"""
    movies = list_movies(user_id)
    sorted_movies = sorted(movies.items(), key=lambda item: float(item[1]['rating'] or 0), reverse=True)
    if not sorted_movies:
        print("No movies to sort.")
        return
    for title, info in sorted_movies:
        print(f"{title} ({info['year']}): {info['rating']}")


def list_movies(user_id):
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT title, year, rating, poster_url, note, imdb_id FROM movies WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        movies = result.fetchall()
    return {
      row[0]: {"year": row[1], 
      "rating": row[2], 
      "poster_url": row[3],
      "note": row[4],
      "imdb_id": row[5]
    } 
    for row in movies}



def fetch_movie_from_omdb(title):
    """Searching the movie in the OMDB API and fething the parameter
    Title, Year, Rating, Poster Image URL"""
    params = {"apikey": API_KEY, "t": title}
    try:
        response = requests.get(URL, params=params, timeout=5)
        data = response.json()
    except requests.RequestException:
        raise RunTimeError("API is not accessible. Please check your connection.")
    if data.get("Response") == 'False':
        raise ValueError(f"Movie not found {title}")
    return {
      "title": data.get("Title", ""),
      "year": data.get("Year", ""),
      "rating": data.get("imdbRating", ""),
      "poster_url": data.get("Poster", ""),
      "imdb_id" : data.get("imdbID", "")
    }


def add_movie(title, user_id):
    """Add a new movie to the database."""
    try:
        movie = fetch_movie_from_omdb(title)
    except RuntimeError as e:
        print(e)
        return
    except ValueError as e:
        print(e)
        return
    movie['user_id'] = user_id
    with engine.connect() as connection:
        try:
            connection.execute(text(
                "INSERT INTO movies (title, year, rating, poster_url, user_id, imdb_id) VALUES (:title, :year, :rating, :poster_url, :user_id, :imdb_id)"
            ), movie)
            connection.commit()
            print(f"Movie '{title}' added successfully.")
        except Exception as e:
            print(f"Error adding to database: {e}")


def delete_movie(title, user_id):
    """Delete a movie from the database."""
    with engine.connect() as connection:
        try:
            result = connection.execute(
                text("DELETE FROM movies WHERE title = :title AND user_id = :user_id"),
                {"title": title, "user_id": user_id}
            )
            connection.commit()
            if result.rowcount > 0:
                print(f"Movie '{title}' deleted successfully.")
            else:
                print(f"No movie found with title '{title}'.")
        except Exception as e:
            print(f"Error: {e}")



def update_movie(title, note, user_id):
    """Update a movie's rating in the database."""
    with engine.connect() as connection:
        try:
            result = connection.execute(
                text("UPDATE movies SET note = :note WHERE title = :title AND user_id = :user_id"),
                {"note": note, "title": title, "user_id": user_id}
            )
            connection.commit()
            if result.rowcount > 0:
                print(f"Movie '{title}' updated successfully")
            else:
                print(f"No movie found with title '{title}'.")
        except Exception as e:
            print(f"Error: {e}")


def generate_website(user_id, username):
    """Fetch all movies and generate the website."""
    movies = list_movies(user_id)
    movies_grid_html = ""
    for title, info in movies.items():
        imdb_id = info.get("imdb_id")
        imdb_url = f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else '#'
        note = html.escape(info.get("note") or "")
        poster = info.get("poster_url") or "https://via.placeholder.com/300x450?text=No+Image"
        movies_grid_html += f"""
        <li>
            <div class="movie-item">
                <a href="{imdb_url}" target="_blank" rel="noopener noreferrer" >
                    <img class="movie-poster" src="{poster}" alt="{title} poster" title="{note}">
                </a>
                <div class="movie-title">{title}</div>
                <div class="movie-year">{info['year']}</div>
                <div class="movie-rating">{info['rating']}</div>
            </div>
        </li>
        """
    with open("_static/index_template.html", "r") as f:
        template = f.read()
    template = template.replace("__TEMPLATE_TITLE__", f"{username}'s Movie App")
    template = template.replace("__TEMPLATE_MOVIE_GRID__", movies_grid_html)
    with open(f"_static/{username}.html", "w") as f:
        f.write(template)
    print(f"Website for {username} was generated successfully.")
