import pandas as pd
import requests

# Charger votre dataset
df = pd.read_csv('products.csv')

# Fonction pour vérifier les liens d'images
def check_image_url(url):
    try:
        response = requests.head(url)
        if response.status_code == 200:
            return True
        else:
            return False
    except:
        return False

# Appliquer la fonction sur la colonne image
df['image_accessible'] = df['image'].apply(check_image_url)

# Compter le nombre de produits avec des images inaccessibles
products_removed = df[df['image_accessible'] == False].shape[0]

# Filtrer les produits avec des images accessibles
df_cleaned = df[df['image_accessible'] == True]

# Sauvegarder le dataset nettoyé
df_cleaned.to_csv('products.csv', index=False)

print(f"Le dataset a été nettoyé et sauvegardé dans 'products.csv'.")
print(f"Nombre de produits effacés : {products_removed}")
