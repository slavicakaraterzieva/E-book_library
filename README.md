# E-book_library
Upload and reed pdf books and files online

Video Demo: https://youtu.be/1NnNS33sgmk?si=xCfjSY2Mli0X8eZ0
Description: Upload pdf books or files for public reading. Read pdf books or files online.
Resources used: This site has being build upon the finance project, using the login, register, apology, app.py, styles.css and some other files also. Youtube course Youtube for uploading image files from a file form, saved in a folder and the file path saved in a database table. Also displayed on a page for reading. Modified to upload pdf files for the purpose of this project. For handling foreign keys in tables using DELETE clause:https://www.sqlitetutorial.net/sqlite-foreign-key/ For creating entity relationship diagrams: https://dbdiagram.io/d Delete file from a folder programmatically: https://www.geeksforgeeks.org/delete-a-directory-or-file-using-python/ The cs50sql course: https://www.youtube.com/playlist?list=PLhQjrBD2T382v1MBjNOhPu9SiJ1fsD4C0 Cover photo: https://pixabay.com/photos/search/ artist:un-perfect Google's Word Counter for this readme file.

Detailed description: This platform allows users to read documents and books in pdf format without creating account, by browsing files that have been uploaded on the platform. It has two options for creating accounts: As publisher who can publish files for reading. Also, with a privilege to modify description or delete the files uploaded. As a reader who can read documents and books that have been published by publishers, with a privilege to save desired books for reading latter in a read-latter list. this list can be updated by the readers to their liking. So it is a dynamic platform, where content is presented according to users data. As for the accounts, the data can be updated by each user or deleted by each user who created it.

The files: styles.css: It is adopted from the previous project, and it is not changed much. I just added the styling for the layout page, with an animation.

about.html: It is a short description about this project. The route used is @app.route("/about").

account.html: It fetches data from the project.db database according to the user logged in. The route @app.route("/account"). And it sends the data to the route @app.route("/update_account") also to the route @app.route("/delete_account").

apology.html: this file too was adopted from the previous project and I used it where flash messages weren't applicable.

dashboard.html: It is the users own control panel from where they can control their account and uploaded files. Routes to the account, uploading updating and reading files, and more.

edit_account.html: Here the data of the users that have an account is fetched from the database in the route @app.route("/update_account"). Checking if the user exists, validating inputs and inserting in the two tables reader and publisher accordingly to the type of account. this is the page from where the users control their account, editing details or removing, deleting the account.

edit_desc.html: This is where the publisher edits the file description in the books table, after the file has been uploaded and description has been set. So If the user decides to change the title, author and other details. @app.route("/edit_desc") processes the fetching of the selected document from the books table and if changes are made, books table is updated.

edit_login.html: Here the data is fetched from the database according to the logged user, inputs validated and data saved if there are changes, processed in the route @app.route("/edit_account").

edit_login.html: here the users can edit their login details. Data is fetched from the database according to the user logged in, inputs validated and if any changes the user table is updated. All processed in @app.route("/login")

index.html: Its the hero page that is visible to anyone with a link to the search page from where flies can be read by anyone. Routes are extended from the layout page.

instructions.html: Instructions on how to use the platform.

layout.html: This is the main layout that extends to all the pages on the platform, consisting of the header, navigation menu, flash messages, main content block and the footer. Contains the routes to login, register, logout search, about, instructions, home index, dashboard.

list_of_books.html: This file presents a list of files available for reading. Files are uploaded from the updates directory. Cross checked with the database for the path of the file in the files table and file_id from the books table to fetch the details of the file such as title, author, description and so on. the route used is @app.route("/list_books"). The file is served in anchor tag with a target that opens the selected file in a new tab. Another route is@app.route("/read_later/") option for the readers. If users chose a document to read, the data is saved to a read table. For the readers there is an option for the book to be saved with a type "later". this creates read "latter list" with documents stored for reading latter, processed by the route @app.route("/read_later/"). This type can be removed by the reader trough a button via the route @app.route("/remove_file/").

login.html: Gets user data from database. Validates the inputs and logs in the user. Route @app.route("/login")

read.html: This file is used by the users that don't have an account. It serves the browsed file without login and creating account. The other users can have privileges only if they make an account. That is why it was necessary to create this file without privileges. Routes used are @app.route("/serve-file/") this route gets the name of the file from the search, stored in the "read" link. @app.route("/read") This route checks if the path of the selected file exists in the database and if so, it calls the file from the uploads directory, the folder where the files are stored.

register.html: Registers two types of users, reader or publisher, selected by radio buttons. Inserts the data into users table. Route used @app.route("/register")

search.html: It allows users and visitors to search documents and books by title, author, date published and category. Once the file is selected the user is redirected via link to the read page. Routes are @app.route("/search") and @app.route("/read").

update_desc.html: This is where description of the file is set by the publisher after the file has been uploaded. Category is chosen and the rest of the details. There is an option not to fill all the details here, because the author or date published might be unknown. That is why there is an option to edit the description latter. Route @app.route("/update_details")

upload_file.html: file can be uploaded by choosing from the user's computer. Must be pdf format for now. For the sake of simplicity I omitted other formats such as text or word document. And there is a limit of size up to 16 mega bites configured like this: app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024. The file is saved to uploads folder and the path name is saved in files table. The file id is saved in the books table.

app.py: Even though this file has been borrowed from the previous project, all of it has been changed to serve this platform. Many thanks for the insight on how flask framework works. Doing this project from scratch would have taken much more time. I wanted to have the experience of teamwork, because before this course I did everything by myself. Even when I followed tutorials, there wasn't a person that I can turn for further instructions, except StuckOverflow or some facebook groups.

project.db: The database has 8 tables, some one to one in relationship, some one to many and some many to many, and two junction tables. The tables are: users(id, user name and hashed password), categories(id and category name), books(id, category id, file id, title, description, author date published), files(id, user id, file path, book id), publisher(user id, first and last name), reader(user id first and last name), publish(user id, book id), read(user id book id and type). I used a entity relationship diagram to figure out how to save unique book id for each file, so each file can have only one book id.

schema.sql: Its the backup sql file for the database.

Fun facts: README.md Has 1269 words, 8066 characters, 6834 characters without space, 76 sentences and 38 paragraphs. According to Google's word count tool.
