from flask import Flask, render_template, request, redirect, flash, session, make_response, url_for
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os
from datetime import datetime
import uuid
import csv

app = Flask(__name__)
app.secret_key = 'secret_key'

# Configuration de la base de données SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Définition du modèle de produit
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    main_category = db.Column(db.String(100), nullable=False)
    sub_category = db.Column(db.String(100), nullable=True)
    image = db.Column(db.String(100), nullable=True)
    link = db.Column(db.String(100), nullable=True)
    ratings = db.Column(db.String(100), nullable=True)
    no_of_ratings = db.Column(db.String(100), nullable=True)
    discount_price = db.Column(db.String(100), nullable=True)
    actual_price = db.Column(db.String(100), nullable=True)

# Charger l'ID utilisateur actuel
current_user_id_path = os.path.join(os.path.dirname(__file__), 'data', 'current_user_id.txt')
if os.path.exists(current_user_id_path):
    with open(current_user_id_path, 'r') as file:
        current_user_id = int(file.read().strip())
else:
    current_user_id = 1

# Fonction pour enregistrer les utilisateurs dans un fichier CSV
def record_user(user_id):
    users_csv_path = os.path.join(os.path.dirname(__file__), 'data', 'users.csv')
    file_exists = os.path.isfile(users_csv_path)

    with open(users_csv_path, 'a', newline='') as csvfile:
        fieldnames = ['user_id', 'timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()  # Écrire l'entête seulement si le fichier n'existe pas

        writer.writerow({'user_id': user_id, 'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')})

# Fonction pour enregistrer les interactions dans un fichier CSV
def record_interaction(user_id, product_id, action):
    interactions_csv_path = os.path.join(os.path.dirname(__file__), 'data', 'interactions.csv')
    file_exists = os.path.isfile(interactions_csv_path)

    with open(interactions_csv_path, 'a', newline='') as csvfile:
        fieldnames = ['interaction_id', 'user_id', 'product_id', 'action']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()  # Écrire l'entête seulement si le fichier n'existe pas

        interaction_id = sum(1 for row in csv.DictReader(open(interactions_csv_path))) + 1 if file_exists else 1
        writer.writerow({'interaction_id': interaction_id, 'user_id': user_id, 'product_id': product_id, 'action': action})

# Créer la base de données et les tables si elles n'existent pas
if not os.path.exists(os.path.join('instance', 'products.db')):
    if not os.path.exists('instance'):
        os.makedirs('instance')
    with app.app_context():
        db.create_all()
        dataset = pd.read_csv(os.path.join('data', 'products.csv'))
        for _, row in dataset.iterrows():
            product = Product(
                name=row['name'],
                main_category=row['main_category'],
                sub_category=row['sub_category'],
                image=row['image'],
                link=row['link'],
                ratings=str(row['ratings']),
                no_of_ratings=str(row['no_of_ratings']),
                discount_price=str(row['discount_price']),
                actual_price=str(row['actual_price'])
            )
            db.session.add(product)
        db.session.commit()

@app.route('/')
def index():
    # Vérifier si c'est la première visite de l'utilisateur
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        record_user(session['user_id'])  # Enregistrer le nouvel utilisateur dans users.csv
        flash("Bienvenue sur notre site ! C'est votre première visite.", "info")
    else:
        flash("Bienvenue de retour !", "info")

    category = request.args.get('category')
    sub_category = request.args.get('sub_category')
    search = request.args.get('search')
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Nombre de produits par page

    # Filtrer les produits
    filtered_products = Product.query
    if category:
        filtered_products = filtered_products.filter_by(main_category=category)
    if sub_category:
        filtered_products = filtered_products.filter_by(sub_category=sub_category)
    if search:
        filtered_products = filtered_products.filter(Product.name.ilike(f'%{search}%'))

    filtered_products = filtered_products.paginate(page=page, per_page=per_page)

    # Récupérer les catégories principales et secondaires
    main_categories = Product.query.with_entities(Product.main_category).distinct().all()
    sub_categories = Product.query.with_entities(Product.sub_category).distinct().all()

    # Produits récents et populaires
    recent_products = Product.query.order_by(Product.id.desc()).limit(5).all()
    popular_products = Product.query.order_by(Product.ratings.desc()).limit(5).all()

    # Récupérer le panier depuis la session
    cart = []
    if 'cart' in session:
        cart = [Product.query.get(product_id) for product_id in session['cart']]

    # Charger les recommandations à partir de predictions.csv
    predictions_csv_path = os.path.join(os.path.dirname(__file__), 'data', 'predictions.csv')
    recommendations = pd.read_csv(predictions_csv_path)

    # Sélectionner les 5 dernières interactions
    last_interactions = recommendations.sort_values(by='id_interaction', ascending=False).head(5)
    last_recommendations = []
    for _, interaction in last_interactions.iterrows():
        recommended_product = Product.query.filter_by(id=interaction['id_produit_recommande']).first()
        if recommended_product:
            last_recommendations.append({
                'product_id': recommended_product.id,
                'name': recommended_product.name,
                'main_category': recommended_product.main_category,
                'sub_category': recommended_product.sub_category,
                'actual_price': recommended_product.actual_price
            })

    return render_template(
        'index.html',
        products=filtered_products.items,
        recent_products=recent_products,
        popular_products=popular_products,
        main_categories=main_categories,
        sub_categories=sub_categories,
        selected_category=category,
        selected_sub_category=sub_category,
        search_query=search,
        cart=cart,
        last_recommendations=last_recommendations,
        pagination=filtered_products
    )

@app.route('/accept_cookies')
def accept_cookies():
    global current_user_id
    user_id = str(current_user_id)
    current_user_id += 1

    # Sauvegarder l'ID utilisateur actuel
    with open(current_user_id_path, 'w') as file:
        file.write(str(current_user_id))

    session['user_id'] = user_id
    session['cart'] = []

    # Ajouter l'utilisateur dans users.csv
    record_user(user_id)

    resp = make_response(redirect('/'))
    resp.set_cookie('user_id', user_id, max_age=60*60*24*30)  # Cookie persistant pour 30 jours

    return resp

@app.route('/decline_cookies')
def decline_cookies():
    return "Vous avez refusé les cookies. Certaines fonctionnalités peuvent être limitées."

@app.route('/product/<int:product_id>')
def product(product_id):
    product = Product.query.get_or_404(product_id)
    cart = []
    if 'cart' in session:
        cart = [Product.query.get(product_id) for product_id in session['cart']]
    # Enregistrer l'interaction de vue
    record_interaction(session['user_id'], product_id, 'viewed')
    return render_template('product.html', product=product, cart=cart)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    if product:
        if 'cart' not in session:
            session['cart'] = []
        session['cart'].append(product_id)
        flash(f'{product.name} a été ajouté au panier.', 'success')
        record_interaction(session['user_id'], product_id, 'added_to_cart')
    return redirect('/')

@app.route('/purchase/<int:product_id>')
def purchase(product_id):
    product = Product.query.get_or_404(product_id)
    flash(f'Achat de {product.name} réussi.', 'success')
    record_interaction(session['user_id'], product_id, 'purchased')
    return redirect('/')

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item != product_id]
    flash(f'Le produit a été retiré du panier.', 'danger')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port=5001)


