from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

app = Flask(__name__)
app.secret_key = 'secret_key'  # Nécessaire pour utiliser flash messages

# Configuration de la base de données SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modèle de produit
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    main_category = db.Column(db.String(100), nullable=False)
    sub_category = db.Column(db.String(100), nullable=True)
    image = db.Column(db.String(100), nullable=True)
    link = db.Column(db.String(100), nullable=True)
    ratings = db.Column(db.Float, nullable=True)
    no_of_ratings = db.Column(db.Integer, nullable=True)
    discount_price = db.Column(db.Float, nullable=True)
    actual_price = db.Column(db.Float, nullable=True)

# Créer la base de données et les tables
db.create_all()

# Lire le dataset CSV et remplir la base de données
dataset = pd.read_csv('/home/osboxes/Desktop/test/data/products.csv')
for index, row in dataset.iterrows():
    product = Product(
        name=row['name'],
        main_category=row['main_category'],
        sub_category=row['sub_category'],
        image=row['image'],
        link=row['link'],
        ratings=row['ratings'],
        no_of_ratings=row['no_of_ratings'],
        discount_price=row['discount_price'],
        actual_price=row['actual_price']
    )
    db.session.add(product)
db.session.commit()

# Panier
cart = []

@app.route('/')
def index():
    category = request.args.get('category')
    search = request.args.get('search')
    filtered_products = Product.query

    if category:
        filtered_products = filtered_products.filter_by(main_category=category)

    if search:
        filtered_products = filtered_products.filter(Product.name.ilike(f'%{search}%'))

    filtered_products = filtered_products.all()

    return render_template('index.html', products=filtered_products, selected_category=category, search_query=search, cart=cart)

@app.route('/product/<int:product_id>')
def product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    if product:
        cart.append(product)
        flash(f'{product.name} a été ajouté au panier.', 'success')
    return redirect('/')

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    global cart
    cart = [item for item in cart if item.id != product_id]
    flash(f'Le produit a été retiré du panier.', 'danger')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)

