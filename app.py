import os
from flask import Flask, flash, redirect, url_for, render_template, request, session, send_from_directory
#from cs50 import SQL
#from flask_session import Session
from flask import session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
# sanitizes the file name
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from helpers import apology, login_required
# Configure application
app = Flask(__name__)
# directory of the pdf files
app.config["UPLOAD_DIRECTORY"] = "uploads/"
# max file size 16MB
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
# allowed file extensions
app.config["ALLOWED_EXTENSIONS"] = [".pdf"]
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
#Session(app)

# Configure CS50 Library to use SQLite database
#db = SQL("sqlite:///project.db")


@app.after_request
def after_request(response):
    # Ensure responses aren't cached
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Routes
@app.route("/")
def index():
    # hero page
    # via get method
    if session.get("user_id") is None:
        return render_template("index.html")
    # via post method
    else:
        # get the user logged in
        id = session["user_id"]

        # search the database for name and type of account
        type = db.execute("SELECT type FROM users WHERE id = ?", id)[0]["type"]
        username = db.execute("SELECT username FROM users WHERE id = ?", id)[0]["username"]
        return render_template("index.html", type=type, username=username)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to user panel page
        return redirect("/dashboard")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")
        reader = request.form.get("reader")
        publisher = request.form.get("publisher")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

        # Ensure password was submitted
        if not password:
            return apology("must provide password", 400)

        # Ensure the two passwords match
        if password == confirm:
            # If they match then hash the password
            hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        else:
            return apology("passwords don't match", 400)

        if username:
            # Check database if username exists
            rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if reader:
            type = reader
        elif publisher:
            type = publisher

        # Ensure username doesn't exist
        if len(rows):
            return apology("username already exists, chose another one", 400)
        # Store everything in database
        rows = db.execute("INSERT INTO users (username, hash, type) VALUES (?, ?, ?)", username, hash, type)
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(rows) == 1:
            session["user_id"] = rows[0]["id"]

        # Redirect user to update account details page
        flash(f"Registered!")
        return redirect("/account")
    else:
        # return apology("TODO")
        return render_template("register.html")

@app.route("/dashboard")
@login_required
def dashboard():
    id = session["user_id"]
    # search the database for name and type of account
    type = db.execute("SELECT type FROM users WHERE id = ?", id)[0]["type"]
    username = db.execute("SELECT username FROM users WHERE id = ?", id)[0]["username"]
    # code for publisher
    if type == "publisher":
        # Getting books from database
        published = db.execute("SELECT * FROM books INNER JOIN publish ON publish.book_id = books.id WHERE publish.user_id = ?", id)

        # Checking if any books in database
        if not published:
            # If no books don't load any
            return render_template("dashboard.html", type=type, username=username)
        else:
            # Query files associated with the user
            files = db.execute("SELECT * FROM files WHERE user_id = ?", id)
            return render_template("dashboard.html", type=type, username=username, published=published, files=files)

    # code for reader
    if type == "reader":
        later = []
        file_type = db.execute("SELECT book_id, user_id FROM read WHERE type == 'later' AND user_id = ?", id)
        for read_later in file_type:
            later.append(read_later["book_id"])  # Append book_id directly

        # Check for files in read table that match the filename
        matching_files = []
        for book_id in later:
            match = db.execute("SELECT path FROM files WHERE id = ?", (book_id,))
            for matches in match:
                matching_files.append(matches["path"])
        print(matching_files)
        # write a query that joins books and files tables with everything from books and path from files
        select_book = db.execute("SELECT * FROM books LEFT JOIN files ON books.file_id = files.id ORDER BY file_id")
        # Upload files that are already in folder
        files = os.listdir(app.config["UPLOAD_DIRECTORY"])
        print(files)
        pdf = []
        for file in files:
            if file in matching_files:
                pdf.append(file)
        return render_template("dashboard.html", pdf=pdf, type=type, username=username, files=files, select_book=select_book)



@app.route("/upload", methods=["POST"])
@login_required
def upload():
        # publisher uploads files in database
        try:
            # get the file from the form
            file = request.files["file"]
            # omit[0] because is the name of the file before the split
            extension = os.path.splitext(file.filename)[1].lower()

            # check if there is file
            if not file:
                flash(f"Select file!")
            else:
                if extension not in app.config["ALLOWED_EXTENSIONS"]:
                    return apology("Only pdf files accepted", 403)
                # load file name in a secure string to be saved in a folder
                file.save(os.path.join(app.config["UPLOAD_DIRECTORY"],secure_filename(file.filename)))
        except RequestEntityTooLarge:
            return apology("File too large, file limit is 16MB", 403)

        # saving file path to database
        file_path = os.path.join(secure_filename(file.filename))
        id = session["user_id"]
        new_file = db.execute("SELECT path FROM files WHERE path = ?", file_path)

        if new_file:
            return apology("File Already Loaded")
        else:
            db.execute("INSERT INTO files (path, user_id) VALUES (?, ?)", file_path, id)
            new_book = db.execute("SELECT file_id FROM books WHERE file_id = (SELECT id FROM files WHERE path = ?)", file_path)
            if new_book:
                return apology("File couldn't be loaded")
            else:
                db.execute("INSERT INTO books (file_id) VALUES((SELECT id FROM files WHERE path = ?))", file_path)
                db.execute("INSERT INTO publish (user_id, book_id) VALUES(?, (SELECT id FROM books ORDER BY id DESC LIMIT 1))", id)
                db.execute("UPDATE files SET book_id = (SELECT id FROM books ORDER BY id DESC LIMIT 1) WHERE path = ?", file_path)
                flash("File Loaded Successfully")
                return redirect("/update_desc")


# route for visitors
@app.route("/read", methods=["GET"])
def read():
    search = request.args.get("search")
    if search:
        search_term = f"%{search}%"
        try:
            search_file = db.execute("SELECT path FROM files WHERE id = (SELECT file_id FROM books WHERE title LIKE ?)", (search_term,))
            if not search_file:
                flash("No books to read")
                return render_template("read.html")
            else:
                # split the list
                path_name = search_file[0]['path']
                file_path = path_name.split(":")
                # upload files that are in the folder
                files = os.listdir(app.config["UPLOAD_DIRECTORY"])
                for file in files:
                    if file in file_path:
                        return render_template("read.html", files=files, file_path=file_path)
        except Exception as e:
            flash(f"An error occurred: {e}")
            return render_template("read.html")
    else:
        flash("No search term provided")
        return render_template("read.html")


# get the filename from previous function read_later
@app.route("/list_books", methods=["GET"])
def list_books():
            id = session["user_id"]
            type = db.execute("SELECT type FROM users WHERE id = ?", id)[0]["type"]
            # write a query that joins books and files tables with everything from books and path from files
            select_book = db.execute("SELECT * FROM books LEFT JOIN files ON books.file_id = files.id ORDER BY file_id")
            # upload files that already exist
            files = os.listdir(app.config["UPLOAD_DIRECTORY"])
            pdf = []
            for file in files:
                pdf.append(file)
            return render_template("list_of_books.html", pdf=pdf, type=type, select_book=select_book)


@app.route("/read_later/<filename>", methods=["GET"])
@login_required
def read_later(filename):
     # get the user logged in
    id = session["user_id"]
    type = "later"
    # Get the book_id from the filename
    book_id = db.execute("SELECT id FROM books WHERE file_id = (SELECT id from files WHERE path = ?)", filename)

     # Check if book_id was found
    if book_id:
        # check if book is already saved
        existing_entry = db.execute("SELECT user_id, book_id FROM read WHERE user_id = ? AND book_id = ?",id, book_id[0]['id'])
        # Save the opened file to the database
        if not existing_entry:
             db.execute("INSERT INTO read (user_id, book_id, type) VALUES (?, ?, ?)", id, book_id[0]['id'], type)
        else:
             return send_from_directory(app.config["UPLOAD_DIRECTORY"], filename)
        flash(f"Book added to read later list")
        return redirect("/dashboard")


@app.route("/remove_file/<filename>", methods=["GET"])
@login_required
def remove_file(filename):
     db.execute("DELETE FROM read WHERE book_id = (SELECT id from files WHERE path = ?)", filename)
     flash(f"file removed from list")
     return redirect("/dashboard")


# serves pdf's in the browser
@app.route("/serve-file/<filename>", methods=["GET"])
def serve_file(filename):
    return send_from_directory(app.config["UPLOAD_DIRECTORY"], filename)


@app.route("/instructions")
def instructions():
    return render_template("instructions.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/search", methods=["GET","POST"])
def search():
    if request.method == "GET":
         category = db.execute("SELECT * FROM categories")
         return render_template("search.html", category=category)

    if request.method == "POST":
        category = db.execute("SELECT * FROM categories")
        category_list = request.form.get("category")
        # validate the category input
        if category_list:
            selected_book = db.execute("SELECT * FROM books WHERE category_id = ?", category_list)
            if not selected_book:
                flash(f"no books found")
                return render_template("search.html", category=category)
            else:
                return render_template("search.html", category=category, selected_book=selected_book)

        else:
            search = request.form.get("search")
            if search:
                search_term = f"%{search}%"
                check_data = db.execute("SELECT title, author, description, date_published FROM books")
                if check_data:
                    title = db.execute("SELECT title, description, author, date_published FROM books WHERE title LIKE ?", search_term)
                    author = db.execute("SELECT title, description, author, date_published FROM books WHERE author LIKE ?", search_term)
                    date = db.execute("SELECT title, description, author, date_published FROM books WHERE date_published LIKE ?", search_term)

                    if not title and not author and not date:
                        flash("No books found")
                        return render_template("search.html", category=category)
                    else:
                         search = ""
                         return render_template("search.html", title=title, author=author, date=date, category=category)
            else:
                flash("Please enter a search term")
                return render_template("search.html", category=category)



@app.route("/upload_file")
@login_required
def upload_file():
        # get the user logged in
        id = session["user_id"]
        # search the database for name and type of account
        type = db.execute("SELECT type FROM users WHERE id = ?", id)[0]["type"]
        username = db.execute("SELECT username FROM users WHERE id = ?", id)[0]["username"]

        # code for publisher
        if type == "publisher":
            # do stuff
            return render_template("upload_file.html", type=type, username=username)

@app.route("/update_desc")
@login_required
def update_desc():
        # it loads the data of files and categories from database in the update_dsc.html
        # get the user logged in
        id = session["user_id"]
        # search the database for name and type of account
        type = db.execute("SELECT type FROM users WHERE id = ?", id)[0]["type"]
        publisher = db.execute("SELECT first_name FROM publisher WHERE user_id = ?", id)
        file = db.execute("SELECT * FROM files WHERE user_id = ?", id)
        category = db.execute("SELECT * FROM categories")
        for item in publisher:
            # if account is updated
            if item["first_name"] is not None:
                name = item["first_name"]
                # get the file and the category
                file = db.execute("SELECT * FROM files WHERE user_id = ?", id)
                category = db.execute("SELECT * FROM categories")
                return render_template("update_desc.html", name=name, file=file, category=category, type=type)

        return render_template("update_desc.html", file=file, category=category, type=type)


@app.route("/update_details", methods=["POST"])
@login_required
def update_details():
        # it updates the details in the books table
        # the id's from the selected options
        file_id = request.form.get("file")
        category_id = request.form.get("category")
        # all the rest inputs
        book_title = request.form.get("title")
        book_description = request.form.get("description")
        book_author = request.form.get("author")
        book_date = request.form.get("date")

        # search if any books to update
        all_books = ("SELECT * FROM books WHERE file_id = ?", file_id)
        for the_book in all_books:
           if the_book:
            category = db.execute("SELECT category_id FROM books WHERE file_id = ?", file_id)
            if category != category_id:
                db.execute("UPDATE books SET category_id = ? WHERE file_id = ?",
                category_id, file_id)

            title = db.execute("SELECT title FROM books WHERE file_id = ?", file_id)
            if title != book_title:
                db.execute("UPDATE books SET title = ? WHERE file_id = ?",
                book_title, file_id)

            description = db.execute("SELECT description FROM books WHERE file_id = ?", file_id)
            if description != book_description:
                db.execute("UPDATE books SET description = ? WHERE file_id = ?",
                book_description, file_id)

            author = db.execute("SELECT author FROM books WHERE file_id = ?", file_id)
            if author != book_author:
                db.execute("UPDATE books SET author = ? WHERE file_id = ?",
                book_author, file_id)

            date = db.execute("SELECT date_published FROM books WHERE file_id = ?", file_id)
            if date != book_date:
                db.execute("UPDATE books SET date_published = ? WHERE file_id = ?",
                book_date, file_id)

            flash(f"Details updated successfully!")
            return redirect("/dashboard")


@app.route("/edit_desc", methods=["POST", "GET"])
@login_required
def edit_desc():
        # it edits the details from the books table
        if request.method == "GET":
            # get the user logged in
            id = session["user_id"]
            # search the database for name and type of account
            type = db.execute("SELECT type FROM users WHERE id = ?", id)[0]["type"]
            username = db.execute("SELECT username FROM users WHERE id = ?", id)[0]["username"]
            book = request.args.get("book")
            # book_name gets the entire list {['path':'fitness.pdf']} it needs to be split and only fitness.pdf send as a result
            book_name = db.execute("SELECT path FROM files WHERE id =?", book)
            path_name = book_name[0]['path']
            split_path = path_name.split(":")
            all_books = db.execute("SELECT * FROM books")
            # get the file and the category
            file = db.execute("SELECT * FROM files WHERE id = ?", book)
            category = db.execute("SELECT * FROM categories")
            cat_id = request.args.get("cat")
            cat_name = db.execute("SELECT category_name FROM categories WHERE id = ?", cat_id)
            # cat_name gets the entire list {['category_name':'fitness']} it needs to be split and only fitness send as a result
            category_name = cat_name[0]['category_name']
            split_list = category_name.split(":")
            # get the selected book
            publisher = db.execute("SELECT * FROM publisher WHERE user_id = ?", id)
            selected_book = db.execute("SELECT title, description, author, date_published FROM books WHERE file_id =?", book)
            return render_template("edit_desc.html", type=type, username=username, book=book, file=file, category=category, cat_id=cat_id, cat_name=split_list[0], book_name=split_path[0], selected_book=selected_book, publisher=publisher)

        if request.method == "POST":
            # the id's from the selected options
            file_id = request.form.get("file")
            category_id = request.form.get("category")
            # all the rest inputs
            book_title = request.form.get("title")
            book_description = request.form.get("description")
            book_author = request.form.get("author")
            book_date = request.form.get("date")
            # check for the category
            selected_cat = db.execute("SELECT category_name FROM categories WHERE category_name = ?", category_id)
            for selected in selected_cat:
                if selected != category_id:
                    db.execute("UPDATE categories SET category_name = ? WHERE category_name = ?", category_id)
                else:
                    return apology("Choose category")

            # get the books
            all_books = db.execute("SELECT * FROM books")
            # check if data is changed
            for selected in all_books:
                 if selected["title"] != book_title:
                      db.execute("UPDATE books SET title = ? WHERE file_id = ?", book_title, file_id)

                 if selected["description"] != book_description:
                      db.execute("UPDATE books SET description = ? WHERE file_id = ?", book_description, file_id)

                 if selected["author"] != book_author:
                      db.execute("UPDATE books SET author = ? WHERE file_id = ?", book_author, file_id)

                 if selected["date_published"] != book_date:
                      db.execute("UPDATE books SET date_published = ? WHERE file_id = ?", book_date, file_id)

                 flash(f"Description has been edited successfully!")
                 return redirect("/dashboard")


@app.route("/delete_book")
@login_required
def delete_book():
     file = request.args.get("del_book")
     book_id = db.execute("SELECT id FROM books WHERE file_id = ?", file)[0]["id"]
     file_path = db.execute("SELECT path FROM files WHERE id = ?", file)
     file_name = file_path[0]['path']
     book_id = int(book_id)
     db.execute("DELETE FROM publish WHERE book_id = ?", book_id)
     db.execute("DELETE FROM books WHERE file_id = ?", book_id)
     db.execute("DELETE FROM files WHERE id = ?", book_id)
     # and remove it from updated folder too
     # full path to files
     file_dir = app.config["UPLOAD_DIRECTORY"] = "uploads/"
     path = os.path.join(file_dir, file_name)
     os.remove(path)
     return redirect("/dashboard")

@app.route("/account")
@login_required
def account():
        # it gets the details from the users account
        # get the user logged in
        id = session["user_id"]
        type = db.execute("SELECT type FROM users WHERE id = ?", id)[0]["type"]
        username = db.execute("SELECT username FROM users WHERE id = ?", id)[0]["username"]
        user_rows = db.execute("SELECT * FROM publisher WHERE user_id = ?", id)
        if user_rows:
            return render_template("account.html", username=username, type=type, user_rows=user_rows)
        else:
             return render_template("account.html", username=username, type=type)



@app.route("/update_account", methods=["POST"])
@login_required
def update_account():
      # it updates the details in the users account
      if request.method == "POST":
            # get the user logged in
            id = session["user_id"]

            # search the database for name and type of account
            type = db.execute("SELECT type FROM users WHERE id = ?", id)[0]["type"]
            first_name = request.form.get("first_name")
            last_name = request.form.get("last_name")

            # save details to publisher table
            if type == "publisher":
                pub_rows = db.execute("SELECT * FROM publisher WHERE user_id = ?", id)
                if len(pub_rows):
                    flash(f"User already exists, would you like to update info?")
                    return redirect("/edit_account")
                else:
                    db.execute("INSERT INTO publisher (user_id, first_name, last_name) VALUES (?, ?, ?)", id, first_name, last_name )

                    flash(f"Details updated successfully!")
                    return redirect("/dashboard")

            if type == "reader":
                read_rows = db.execute("SELECT * FROM reader WHERE user_id = ?", id)
                if len(read_rows):
                    flash(f"User already exists, would you like to update info?")
                    return redirect("/edit_account")
                else:
                        db.execute("INSERT INTO reader (user_id, first_name, last_name) VALUES (?, ?, ?)", id, first_name, last_name )
                        flash(f"Details updated successfully!")
                        return redirect("/dashboard")


@app.route("/edit_account", methods=["POST", "GET"])
@login_required
def edit_account():
      # it edits the details in the users account
      # get the user logged in
      id = session["user_id"]

      # search the database for name and type of account
      type = db.execute("SELECT type FROM users WHERE id = ?", id)[0]["type"]
      first_name = request.form.get("first_name")
      last_name = request.form.get("last_name")
      username = db.execute("SELECT username FROM users WHERE id = ?", id)[0]["username"]

      # get the user details from database
      if request.method == "GET":
         if type == "publisher":
            pub_rows = db.execute("SELECT * FROM publisher WHERE user_id = ?", id)
            return render_template("edit_account.html", publish=pub_rows, username=username, type=type)

         if type == "reader":
            read_rows = db.execute("SELECT * FROM reader WHERE user_id = ?", id)
            return render_template("edit_account.html", publish=read_rows, username=username, type=type)

      # handle method post
      if request.method == "POST":
           # code for publisher
           if type == "publisher":
                # check if input info is different than database
                pub_rows = db.execute("SELECT * FROM publisher WHERE user_id = ?", id)
                for rows in pub_rows:
                     first = rows["first_name"]
                     last = rows["last_name"]
                     if first_name == "":
                          return apology("Provide first name")
                     if last_name == "":
                          return apology("Provide last name")
                     # if is different, update info
                     if first != first_name:
                          db.execute("UPDATE publisher SET first_name = ? WHERE user_id = ?", first_name, id)
                          flash(f"Details updated successfully!")
                          return redirect("/dashboard")
                     if last != last_name:
                          db.execute("UPDATE publisher SET last_name = ? WHERE user_id = ?", last_name, id)
                          flash(f"Details updated successfully!")
                          return redirect("/dashboard")
                     else:
                          return redirect("/dashboard")

           # code for reader
           if type == "reader":
              # check if input info is different than database
              pub_rows = db.execute("SELECT * FROM reader WHERE user_id = ?", id)
              for rows in pub_rows:
                    first = rows["first_name"]
                    last = rows["last_name"]
                    if first_name == "":
                        return apology("Provide first name")
                    if last_name == "":
                        return apology("Provide last name")
                    # if is different, update info
                    if first != first_name:
                        db.execute("UPDATE reader SET first_name = ? WHERE user_id = ?", first_name, id)
                        flash(f"Details updated successfully!")
                        return redirect("/dashboard")
                    if last != last_name:
                        db.execute("UPDATE reader SET last_name = ? WHERE user_id = ?", last_name, id)
                        flash(f"Details updated successfully!")
                        return redirect("/dashboard")
                    else:
                         return redirect("/dashboard")


@app.route("/delete_account")
@login_required
def delete_account():
    id = session["user_id"]
    db.execute("DELETE FROM users WHERE id = ?", id)
    session.clear()
    return redirect("/logout")


@app.route("/edit_login", methods=["POST", "GET"])
@login_required
def edit_login():
    # Get the user logged in
    id = session["user_id"]

    if request.method == "GET":
        username = db.execute("SELECT username FROM users WHERE id = ?", id)[0]["username"]
        return render_template("edit_login.html", username=username)

    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        user_name = request.form.get("user_name")

        # Fetch user details once
        user = db.execute("SELECT * FROM users WHERE id = ?", id)[0]
        current = user["hash"]
        name = user["username"]

        # Validate inputs
        if not name:
            return apology("Provide username")
        if not current_password:
            return apology("Enter your current password")
        if not check_password_hash(current, current_password):
            return apology("Incorrect current password")
        if new_password != confirm_password:
            return apology("Passwords don't match", 400)

        # Update user details
        hash = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=16)
        db.execute("UPDATE users SET username = ?, hash = ? WHERE id = ?", user_name, hash, id)
        flash("Details updated successfully!")
        return redirect("/edit_login")



# displays list of books
@app.route("/list_of_books")
@login_required
def list_of_books():
        # get the user logged in
        id = session["user_id"]
        # search the database for name and type of account
        type = db.execute("SELECT type FROM users WHERE id = ?", id)[0]["type"]
        username = db.execute("SELECT username FROM users WHERE id = ?", id)[0]["username"]
        # Get all uploaded books and documents for the logged in user
        all_books = db.execute("SELECT * FROM books")
        # code for publisher
        if type == "publisher":
            return render_template("list_of_books.html", type=type, username=username, all_books=all_books)

        #code for reader
        if type == "reader":
            # do stuff
            return render_template("list_of_books.html", type=type, username=username, all_books=all_books)
