from flask import Flask, render_template, url_for, request, redirect, flash

app = Flask(__name__)
app.secret_key = 'secret_key'  # Nécessaire pour utiliser flash messages

# Données fictives pour les produits avec catégories
products = [
    {'id': 1, 'name': 'Produit 1', 'price': '10.00', 'image': 'images/product1.jpg', 'description': 'Description du produit 1', 'category': 'Informatique'},
    {'id': 2, 'name': 'Produit 2', 'price': '20.00', 'image': 'images/product2.jpg', 'description': 'Description du produit 2', 'category': 'Téléphonie'},
    {'id': 3, 'name': 'Produit 3', 'price': '30.00', 'image': 'images/product3.jpg', 'description': 'Description du produit 3', 'category': 'Électroménager'},
    {'id': 4, 'name': 'Produit 4', 'price': '40.00', 'image': 'images/product4.jpg', 'description': 'Description du produit 4', 'category': 'Informatique'},
    {'id': 5, 'name': 'Produit 5', 'price': '50.00', 'image': 'images/product5.jpg', 'description': 'Description du produit 5', 'category': 'Téléphonie'},
    {'id': 6, 'name': 'Produit 6', 'price': '60.00', 'image': 'images/product6.jpg', 'description': 'Description du produit 6', 'category': 'Électroménager'},
    {'id': 7, 'name': 'Produit 7', 'price': '70.00', 'image': 'images/product7.jpg', 'description': 'Description du produit 7', 'category': 'Informatique'}
]

# Panier
cart = []

@app.route('/')
def index():
    category = request.args.get('category')
    search = request.args.get('search')
    filtered_products = products

    if category:
        filtered_products = [product for product in products if product['category'] == category]

    if search:
        filtered_products = [product for product in filtered_products if search.lower() in product['name'].lower()]

    return render_template('index.html', products=filtered_products, selected_category=category, search_query=search, cart=cart)

@app.route('/product/<int:product_id>')
def product(product_id):
    product = next((item for item in products if item["id"] == product_id), None)
    return render_template('product.html', product=product)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    product = next((item for item in products if item["id"] == product_id), None)
    if product:
        cart.append(product)
        flash(f'{product["name"]} a été ajouté au panier.', 'success')
    return redirect('/')

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    global cart
    cart = [item for item in cart if item['id'] != product_id]
    flash(f'Le produit a été retiré du panier.', 'danger')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)

