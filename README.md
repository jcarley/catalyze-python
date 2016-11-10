# catalyze-python
A very basic REST API. Tested in Python 3.4.3

##Setup
1. Run `$ python setupdb.py` in the root directory to create the necessary SQLite database
2. Make sure the bcrypt and falcon packages are installed
3. Make your first user! (see below)

##Usage
Make sure to include the `Authorize: <token>` header for all requests except for `POST /user`, `POST /auth`, and `GET /`

###GET /
- Accessing without the Authorize header will give you a "Hello World" message
- Accessing with a valid Authorize token will give you the user data

###POST /auth
Create a new access token. Tokens are valid for 24 hours by default.

Example Input: 

    {
      "username": "brubbles",
      "password": "barneyrules"
    }
    
###DELETE /auth
Invalidates access token that is in the Authorization header. No input necessary.

###POST /user
Create a new user.

Example Input: 

    {
      "username": "yabadabadood",
      "password": "wilma4",
      "first_name": "Fred",
      "last_name": "Flintstone",
      "favorite_color": "orange"
    }

###GET /user
Access the authenticated users data. 

Example Output: 

    {
      "id": 2,
      "first_name": "Wilma",
      "last_name": "Flintstone",
      "username": "cavelady",
      "favorite_color": "white"
    }
    
###PUT /user
Updates the authenticated user.

Example Input: 

    {
      "first_name": "Betty",
      "last_name": "Rubbles",
      "favorite_color": "blue"
    }
    
###DELETE /user
Deletes the authenticated user. All associated access tokens automatically get deleted as well. 
