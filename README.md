# Library Management System

Libraries and Frameworks

• Python Libraries
o flask
o flask_sqlalchemy
o datetime
• Database
o SQLite3
• Frontend
o HTML5
o JavaScript
o Bootstrap

Database Model

Table: Book
Field Type Constraint
ID INTEGER Primary Key, Not NULL,
Unique, Auto Increment
Name TEXT
Author TEXT
SID INTEGER

Table: Users
Field Type Constraint
ID TEXT Primary Key, Not NULL,
Unique
Password TEXT

Table: Section
Field Type Constraint
ID INTEGER Primary Key, Not NULL,
Unique, Auto Increment
Name TEXT
Desc TEXT

Table: Issued
Field Type Constraint
SL INTEGER Primary Key, Auto Increment
BID INTEGER
UID INTEGER
Status TEXT
DOI TEXT
DOR TEXT

Main Features

• Librarian
o Login with Admin Privileges
o View, Add, Edit and Delete Sections
o View, Add, Edit and Delete Books
o Accept and Decline Requests
o View and Revoke Issued Books
o Filter Option

• User
o Register and Login
o View Current, Completed and Requested Books
o View all available books
o Request, Read and Return Books
o Filter Option

Video Link: https://drive.google.com/file/d/1d5b7voPK14ATOqKm6-
h5cTUE4fKJpFFQ/view?usp=sharing
