from movie_storage import movie_storage_sql as storage

def menu_display():
    print()
    print("Menu:")
    print("0. Exit")
    print("1. List movies")
    print("2. Add movies")
    print("3. Delete movies")
    print("4. Update movies")
    print("5. Stats")
    print("6. Random movie")
    print("7. Search movie")
    print("8. Movies sorted by rating")
    print("9. Generate website")
    print("10. Switch user")

def main():
    current_user_id, current_username = storage.select_or_create_user()
    print(f"Active user: {current_username}")
    while True:
        menu_display()
        try:
            print()
            num = int(input("Enter choice (0-10): "))
        except ValueError:
            print("Invalid choice")
            continue
        if num == 0:
            print("Bye!")
            break
        elif num == 1:
            print()
            movies = storage.list_movies(current_user_id)
            if not movies:
                print("No movies yet")
            else:
                for title, record in movies.items():
                    year = record.get("year")
                    rating = record.get("rating")
                    print(f"{title} ({year}): {rating}")
        elif num == 2:
            print()
            title = input("Enter a title: ")
            if not title:
                print("Enter a valid title")
                continue
            storage.add_movie(title, current_user_id)
        elif num == 3:
            print()
            title = input("Enter a movie to delete: ")
            try:
                storage.delete_movie(title, current_user_id)
            except KeyError:
                print(f"Movie {title} does not exist")
        elif num == 4:
            print()
            title = input("Enter movie name: ")
            db = storage.list_movies(current_user_id)
            if title not in db:
                print(f"Movie {title} not found")
                continue
            note = input("Enter movie note: ")
            storage.update_movie(title, note, current_user_id)
        elif num == 5:
            print()
            storage.stats(current_user_id)
        elif num == 6:
            print()
            storage.random_movie(current_user_id)
        elif num == 7:
            print()
            storage.search_movie(current_user_id)
        elif num == 8:
            print()
            storage.sorted_by_rating(current_user_id)
        elif num == 9:
            print()
            storage.generate_website(current_user_id, current_username)
        elif num == 10:
            print()
            current_user_id, current_username = storage.select_or_create_user()
            print(f"Active user: {current_username}")
        print()
        input("Press Enter to continue")

if __name__ == '__main__':
    main()
