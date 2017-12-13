# Item Catalog Application

This is a RESTful web application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.


### Summary
- This RESTful web application is built using the Python's framework Flask along with implementing third-party Google's OAuth 2.0 authentication for securing from CSRF attacks. 
- The project implements a JSON endpoint that serves the same information as displayed in the HTML endpoints for an arbitrary item in the catalog.
- Page implements a third-party authentication & authorization service (like Google Accounts) instead of implementing its own authentication & authorization spec. The important pages which updates the database information are secured and needs authentication before using them.
- This web application is bulit using SQLAlchemy - SQL toolkit and object-relational mapper for the Python.
- Also, the code is neatly formatted and compliant with the Python PEP 8 style guide.

### Tools, Technologies and Services used
- Python / Flask framework
- Sqlite / SQLAlchemy
- HTML5 / CSS3
- JSON
- Javascript / jQuery
- Bootstrap
- Google's oAuth 2.0
- Oracle's VirtualBox
- Linux - Ubuntu
- Vagrant
- Git / github.com


### Execution Instruction

#### Prerequisites
1. VirtualBox
2. Vagrant
3. Git
 
#### Steps
1. Open terminal
2. Clone this directory using `git clone https://github.com/adipixel/catalog.git` inside the vagrant directory
3. Go inside the vagrant directory
4. Run `vagrant up`
5. Run `vagrant ssh`
6. Traverse to the directory `cd catalog`
7. Run `python project.py` command
8. The server starts running on `http://localhost:5000`
9. Open browser (like Google Chrome) and goto `http://localhost:5000`

### Json endpoints
- `/catalog/JSON`
- `/catalog/<CATEGORY_NAME>/JSON`
- `/catalog/<CATEGORY_NAME>/<ITEM_NAME>/JSON`



