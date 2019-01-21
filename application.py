# +++++++++++
# imports
# ++++++++++
from flask import Flask, render_template, url_for,\
    request, redirect, flash, jsonify, make_response
from flask_bootstrap import Bootstrap
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from cityDB import Base, AREA, Neighborhood, User
from flask import session as login_session
from flask_login import current_user
import random
import string
# from flask_login import LoginManager
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


# create app


app = Flask(__name__)
# login = LoginManager(app)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "item catalog"


bootstrap = Bootstrap(app)

# connecting to database
engine = create_engine('sqlite:///city.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


# anti forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    request.get_data()
    code = request.data.decode('utf-8')

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
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

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already\
			connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;\
		-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# helper functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
        'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.user_id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.user_id
    except:
        return None


# logout
@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print(result['status'])
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = redirect(url_for('Home'))
        flash("You are now logged out.")
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# ++++++++
# json
# ++++++++

@app.route('/json')
def allItemjson():
    catalog = session.query(AREA).all()
    catalog_dict = [c.serialize for c in catalog]
    for c in range(len(catalog_dict)):
        items = [
            i.serialize for i in session.query(Neighborhood)
            .filter_by(area_name=catalog_dict[c]["id"]).all()
        ]
        if items:
            catalog_dict[c]["item"] = items
    return jsonify(Catalog=catalog_dict)


# display the catagries/areas
@app.route('/catalog/json')
def catalogJson():
    catalog = session.query(AREA).all()
    return jsonify(Area=[c.serialize for c in catalog])


# dispaly the items/Neighborhoods
@app.route('/item/json')
def item():
    item = session.query(Neighborhood).all()
    return jsonify(Neighborhood=[c.serialize for c in item])

# dispalys the items in one catalog


@app.route('/area/<int:area_id>/json')
def catalogItemsJson(area_id):
    catolog = session.query(AREA).filter_by(id=area_id).one()
    items = session.query(Neighborhood).filter_by(
        area_name=area_id).all()
    return jsonify(items=[i.serialize for i in items])

# displays one Item in spacific catalog


@app.route('/area/<int:area_id>/<int:nhood_id>/json')
def catalogItemJson(area_id, nhood_id):
    catolog = session.query(AREA).filter_by(id=area_id).one()
    item = session.query(Neighborhood).filter_by(
        area_name=area_id,
        id=nhood_id
    ).one()
    return jsonify(item=[item.serialize])


# ++++++++
# flask routing
# +++++++++


@app.route('/')
@app.route('/home')
def Home():
    areas = session.query(AREA).all()
    nhoods = session.query(Neighborhood).all()
    return render_template("home.html", nhood=nhoods, area=areas)
    # return "home item catolog"


@app.route('/area/<int:area_id>/')
def sortArea(area_id):
    areas = session.query(AREA).all()
    nhood = session.query(Neighborhood).filter_by(area_name=area_id)
    return render_template("home.html", nhood=nhood, area=areas)


@app.route('/area/<int:nhood_id>/neighborhood')
def showNhood(nhood_id):
    nhood = session.query(Neighborhood).filter_by(id=nhood_id).one()
    return render_template("itemdesc.html", nhood=nhood)


@app.route('/area/add', methods=['GET', 'POST'])
def nhoodAdd():
    if 'username' not in login_session:
        return redirect('/login')
    areas = session.query(AREA).all()
    if request.method == "POST":
        area_name = session.query(AREA).filter_by(
            area_name=request
            .form['catagries']).one()
        newitem = Neighborhood(
            nhood_name=request.form['Nname'],
            description=request.form['description'],
            area_name=area_name.id,
            user_id=login_session['user_id'])
        session.add(newitem)
        session.commit()
        print('Item Successfully Added!')
        return redirect(url_for('Home'))
    return render_template("itemadd.html", area=areas)


@app.route('/area/<int:nhood_id>/neighborhood/edit', methods=['GET', 'POST'])
def editNeighbor(nhood_id):
    editedItem = session.query(Neighborhood).filter_by(id=nhood_id).one()
    areas = session.query(AREA).all()
    nhood = session.query(Neighborhood).filter_by(id=nhood_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedItem.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You\
         are not authorized!')}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        areaName = session.query(AREA).filter_by(
            area_name=request.form['catagries']).one()
        if request.form['Nname']:
            editedItem.nhood_name = request.form['Nname']
        if request.form['description']:
            editedItem.description = request.form['description']
        editedItem.area_name = areaName.id
        session.add(editedItem)
        # session.rollback()
        session.commit()
        return redirect(url_for('showNhood', nhood_id=nhood_id))
    else:
        return render_template(
            'itemedit.html', area=areas, nhood=nhood)


@app.route('/area/<int:nhood_id>/neighborhood/delete',
           methods=['GET', 'POST'])
def delNeighbor(nhood_id):
    if 'username' not in login_session:
        return redirect('/login')
    deleItem = session.query(Neighborhood).filter_by(
        id=nhood_id).one()
    if deleItem.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You \
        are not authorized!')}</script><body onload='myFunction()'>"
    else:
        session.delete(deleItem)
        session.commit()
        flash('item deleted Successfully!')
        return redirect(url_for('Home'))
    return render_template("itemdel.html", nhood=deleItem)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
