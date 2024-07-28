# A/B testing platform

## Description

This is an A/B testing platform start. The idea is based on donation pages. There are two iterations of the web page with the user being displayed one or other at random. The user can enter the donation amount and then if the donation amount is validated, they are led to a thank you page. The code makes sure that one user is always displayed the same kind of page and also keeps count of how many times a user visits the donation page. Multiple user functionality is also supported backed by a database. The user creates an account and then logs in to the platform. Donations are stored in a separate table with the user id being the foreign key. Passwords are hashed using the bcrypt library so that they are not stored in plain text.

## Usage

After navigating to the right directory, run the following commands in the terminal to launch the application:

```bash
python3 -m venv venv
venv\Scripts\activate.bat
pip3 install -r requirements.txt
python3 app.py
```
