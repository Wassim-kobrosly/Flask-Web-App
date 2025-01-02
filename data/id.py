import pandas as pd

# Charger votre dataset
print("Chargement du dataset...")
df = pd.read_csv('products.csv')
print("Dataset chargé avec succès.")

# Ajouter une colonne ID produit
df.insert(0, 'ID_produit', range(1, len(df) + 1))
print("Colonne ID_produit ajoutée.")

# Sauvegarder le dataset mis à jour
df.to_csv('product.csv', index=False)
print("Le dataset mis à jour a été sauvegardé dans 'product.csv'.")

# Imprimer le nombre total de produits
total_products = len(df)
print(f"Nombre total de produits : {total_products}")
