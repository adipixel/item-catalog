from flask import Flask, render_template, request, redirect, jsonify, url_for, flash


from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User


app = Flask(__name__)


# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()



@app.route('/')
@app.route('/catalog/')
def showCategories():
	cat = session.query(Category).all()
	return render_template("index.html", categories = cat)



# JSON APIs to view Category Information
@app.route('/catalog/<int:category_id>/list/JSON')
def categoryListJSON(category_id):
    cat = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(
        category_id=category_id).all()
    return jsonify(items=[i.serialize for i in items])

@app.route('/catalog/<string:category_name>/items')
def catalogItems(category_name):
    cat = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(
        category_id=cat.id).all()
    categories = session.query(Category).all()
    #return jsonify(items=[i.serialize for i in items])
    return render_template("itemDetails.html", categories = categories, category= cat, items = items)

#item information
@app.route('/catalog/<string:category_name>/<string:item_name>')
def itemsInfo(category_name, item_name):
	item = session.query(Item).filter_by(name = item_name).one()
	return render_template("itemInfo.html", category_name = category_name, item = item)


@app.route('/catalog/<string:category_name>/<string:item_name>/edit', methods =['GET', 'POST'])
def editItem(category_name, item_name):
	category = session.query(Category).filter_by(name = category_name).one()
	item = session.query(Item).filter_by(name = item_name, category_id = category.id).one()
	if request.method == 'POST':
		item.name = request.form['name']
		item.description = request.form['desc']
		session.commit()
		#flash("Item updated sucessfully")
		return redirect(url_for('showCategories'))
	else:	
		return render_template("editItem.html", category_name = category_name, item = item)


@app.route('/catalog/<string:category_name>/<string:item_name>/delete', methods =['GET', 'POST'])
def deleteItem(category_name, item_name):
	category = session.query(Category).filter_by(name = category_name).one()
	item = session.query(Item).filter_by(name = item_name, category_id = category.id).one()
	if request.method == 'POST':
		session.delete(item)
		#flash("Item deleted sucessfully")
		return redirect(url_for('showCategories'))
	else:	
		return render_template("deleteItem.html", category_name = category_name, item = item)



@app.route('/catalog/item/add', methods =['GET', 'POST'])
def addItem():
	if request.method == 'POST':
		category = session.query(Category).filter_by(id = request.form['category']).one()
		newItem = Item(name=request.form['name'], description = request.form['desc'], category = category)
		session.add(newItem)
		session.commit()
		return redirect(url_for('showCategories'))
	else:
		categories = session.query(Category).all()
		return render_template('addItem.html', categories=categories)
	


@app.route('/catalog/category/add', methods =['GET', 'POST'])
def addCategory():
	if request.method == 'POST':
		newCategory = Category(name=request.form['name'])
		session.add(newCategory)
		session.commit()
		return redirect(url_for('showCategories'))
	else:
		return render_template('addCategory.html')


@app.route('/catalog/<string:category_name>/edit/', methods =['GET', 'POST'])
def editCategory(category_name):
	category = session.query(Category).filter_by(name = category_name).one()
	if request.method == 'POST':
		category.name = request.form['name']
		session.commit()
		#flash("Item updated sucessfully")
		return redirect(url_for('showCategories'))
	else:	
		return render_template("editCategory.html", category = category)


@app.route('/catalog/<string:category_name>/delete/', methods =['GET', 'POST'])
def deleteCategory(category_name):
	category = session.query(Category).filter_by(name = category_name).one()
	if request.method == 'POST':
		session.delete(category)
		session.commit()
		#flash("Item updated sucessfully")
		return redirect(url_for('showCategories'))
	else:
		return render_template("deleteCategory.html", category = category)



@app.route('/catalog/JSON')
def catalogJSON():
    cat = session.query(Category).all()
    return jsonify(categories=[i.serialize for i in cat])

@app.route('/catalog/<string:category_name>/JSON')
def categoryJSON(category_name):
    cat = session.query(Category).filter_by(name = category_name).one()
    items = session.query(Item).filter_by(category_id = cat.id)
    return jsonify(items=[i.serialize for i in items])

@app.route('/catalog/<string:category_name>/<string:item_name>/JSON')
def itemJSON(category_name, item_name):
    cat = session.query(Category).filter_by(name = category_name).one()
    items = session.query(Item).filter_by(category_id = cat.id, name = item_name)
    return jsonify(itemInfo=[i.serialize for i in items])





if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
