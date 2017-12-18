from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)
app.secret_key = 'fksHnQeC90azPHPO7KZ5yX81'

CLIENT_ID = json.loads(
    open('/vagrant/listing-project/client_secrets.json', 'r')
    .read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"

# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Creating anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


# Logging in user using oAuth
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validating state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtaining authorization code
    code = request.data

    try:
        # Upgrading the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Checking that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verifing that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verifing that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print
        "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response
        (json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Storing the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Geting user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if user_id is None:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<img class=" img-circle" src="'
    output += login_session['picture']
    output += ''' " style = "width: 200px; height: 200px;"> '''
    output += '<div class="caption text-center"><h2>Welcome, '
    output += login_session['username']
    output += '!</h2></div>'

    flash("you are now logged in as %s" % login_session['username'])
    print
    "done!"
    return output


# Disconnecting the user
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps(
                'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']  # NOQA
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        return redirect(url_for('showCategories'))
    else:
        response = make_response(
            json.dumps(
                'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# ------------------------------------------


# Retriving list of categories
@app.route('/')
@app.route('/catalog/')
def showCategories():
    loggedUser = {}
    loginFlag = False
    if 'username' in login_session:
        loggedUser = {'name': login_session['username']}
        loginFlag = True
    cat = session.query(Category).all()
    items = session.query(Item).all()
    return render_template(
        "index.html", categories=cat, items=items,
        loginFlag=loginFlag, loggedUser=loggedUser)


# Retriving list of items
@app.route('/catalog/<string:category_name>/items')
def catalogItems(category_name):
    loggedUser = {}
    loginFlag = False
    if 'username' in login_session:
        loggedUser = getUserInfo(login_session['user_id'])
        loginFlag = True
    cat = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(
        category_id=cat.id).all()
    categories = session.query(Category).all()
    # return jsonify(items=[i.serialize for i in items])
    return render_template(
        "itemDetails.html", categories=categories, category=cat,
        items=items, loginFlag=loginFlag, loggedUser=loggedUser)


# item information
@app.route('/catalog/<string:item_name>')
def itemsInfo(item_name):
    loggedUser = {}
    loginFlag = False
    if 'username' in login_session:
        loggedUser = getUserInfo(login_session['user_id'])
        loginFlag = True
    item = session.query(Item).filter_by(name=item_name).one()
    category = session.query(Category).filter_by(id=item.category_id).one()
    return render_template(
        "itemInfo.html", category_name=category.name, item=item,
        loginFlag=loginFlag, loggedUser=loggedUser)


# Editing item
@app.route(
    '/catalog/<string:category_name>/<string:item_name>/edit/',
    methods=['GET', 'POST'])
def editItem(category_name, item_name):
    if 'username' not in login_session:
        return redirect('/login')
    loggedUser = {}
    loginFlag = False
    if 'username' in login_session:
        loggedUser = getUserInfo(login_session['user_id'])
        loginFlag = True

        category = session.query(Category).filter_by(name=category_name).one()
        item = session.query(Item).filter_by(
            name=item_name, category_id=category.id).one()
        if request.method == 'POST':
            # authorization double check
            if loggedUser.id == category.user_id:
                item.name = request.form['name']
                item.description = request.form['desc']
                item.image = request.form['image']
                session.commit()
                # flash("Item updated sucessfully")
                return redirect(
                    url_for(
                        'itemsInfo', item_name=item.name,
                        loginFlag=loginFlag, loggedUser=loggedUser))
            else:
                return '''You are not authorized to perform this action!
                <a href="/">Home</a>'''
        else:
            return render_template(
                "editItem.html", category_name=category_name, item=item,
                loginFlag=loginFlag, loggedUser=loggedUser)


# Deleting an item
@app.route(
    '/catalog/<string:category_name>/<string:item_name>/delete', methods=[
        'GET', 'POST'])
def deleteItem(category_name, item_name):
    if 'username' not in login_session:
        return redirect('/login')
    loggedUser = {}
    loginFlag = False
    if 'username' in login_session:
        loggedUser = getUserInfo(login_session['user_id'])
        loginFlag = True
        category = session.query(Category).filter_by(name=category_name).one()
        item = session.query(Item).filter_by(
            name=item_name, category_id=category.id).one()
        if request.method == 'POST':
            # authorization double check
            if loggedUser.id == category.user_id:
                session.delete(item)
                session.commit()
                # flash("Item deleted sucessfully")
                return redirect(url_for(
                    'catalogItems', category_name=category_name,
                    loginFlag=loginFlag, loggedUser=loggedUser))
            else:
                return '''You are not authorized to perform this action!
                <a href="/">Home</a>'''
        else:
            return render_template(
                "deleteItem.html", category_name=category_name,
                item=item, loginFlag=loginFlag, loggedUser=loggedUser)


# Adding new item
@app.route('/catalog/item/add', methods=['GET', 'POST'])
def addItem():
    if 'username' not in login_session:
        return redirect('/login')
    loggedUser = {}
    loginFlag = False
    if 'username' in login_session:
        loggedUser = getUserInfo(login_session['user_id'])
        loginFlag = True
    if request.method == 'POST':
        category = session.query(Category).filter_by(
            id=request.form['category']).one()
        newItem = Item(
            name=request.form['name'],
            description=request.form['desc'],
            image=request.form['image'],
            category=category,
            user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        categories = session.query(Category).all()
        return render_template(
            'addItem.html', categories=categories,
            loginFlag=loginFlag, loggedUser=loggedUser)


# Adding new category
@app.route('/catalog/category/add', methods=['GET', 'POST'])
def addCategory():
    if 'username' not in login_session:
        return redirect('/login')
    loggedUser = {}
    loginFlag = False
    if 'username' in login_session:
        loggedUser = getUserInfo(login_session['user_id'])
        loginFlag = True
    if request.method == 'POST':
        newCategory = Category(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template(
            'addCategory.html',
            loginFlag=loginFlag, loggedUser=loggedUser)


# Editing category
@app.route(
    '/catalog/<string:category_name>/edit/', methods=['GET', 'POST'])
def editCategory(category_name):
    if 'username' not in login_session:
        return redirect('/login')
    loggedUser = {}
    loginFlag = False
    if 'username' in login_session:
        loggedUser = getUserInfo(login_session['user_id'])
        loginFlag = True
        category = session.query(Category).filter_by(name=category_name).one()
        if request.method == 'POST':
            # authorization double check
            if loggedUser.id == category.user_id:
                category.name = request.form['name']
                session.commit()
                # flash("Item updated sucessfully")
                return redirect(url_for('showCategories'))
            else:
                return '''You are not authorized to perform this action!
                <a href="/">Home</a>'''
        else:
            return render_template(
                "editCategory.html", category=category,
                loginFlag=loginFlag, loggedUser=loggedUser)


# Deleting category
@app.route(
    '/catalog/<string:category_name>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_name):
    if 'username' not in login_session:
        return redirect('/login')
    loggedUser = {}
    loginFlag = False
    if 'username' in login_session:
        loggedUser = getUserInfo(login_session['user_id'])
        loginFlag = True
        category = session.query(Category).filter_by(name=category_name).one()
        if request.method == 'POST':
            # authorization double check
            if loggedUser.id == category.user_id:
                session.delete(category)
                session.commit()
            # flash("Item updated sucessfully")
                return redirect(url_for('showCategories'))
            else:
                return '''You are not authorized to perform this action!
                <a href="/">Home</a>'''
        else:
            return render_template(
                "deleteCategory.html", category=category,
                loginFlag=loginFlag, loggedUser=loggedUser)


# JSON api for categories
@app.route('/catalog/JSON')
def catalogJSON():
    cat = session.query(Category).all()
    return jsonify(categories=[i.serialize for i in cat])


# JSON api for items form a category
@app.route('/catalog/<string:category_name>/items/JSON')
def categoryJSON(category_name):
    cat = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_id=cat.id)
    return jsonify(items=[i.serialize for i in items])


# JSON api for item details
@app.route('/catalog/<string:category_name>/<string:item_name>/JSON')
def itemJSON(category_name, item_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(
        category_id=category.id, name=item_name).one()
    return jsonify(itemInfo=items.serialize)


# JSON APIs to view Category Information
@app.route('/catalog/<string:category_name>/info/JSON')
def categoryInfoJSON(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    return jsonify(category.serialize)


if __name__ == '__main__':
    # app.secret_key = 'fksHnQeC90azPHPO7KZ5yX81'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
