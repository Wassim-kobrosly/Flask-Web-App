import pandas as pd
import aiohttp
import asyncio
import time

# Charger votre dataset
print("Chargement du dataset...")
df = pd.read_csv('products.csv')
print("Dataset chargé avec succès.")

# Fonction asynchrone pour vérifier les liens d'images
async def check_image_url(session, url, retries=3):
    for attempt in range(retries):
        try:
            async with session.head(url, timeout=10) as response:
                if response.status == 200:
                    return True
                else:
                    return False
        except asyncio.TimeoutError:
            print(f"Timeout pour l'URL (Tentative {attempt + 1}/{retries}) : {url}")
        except Exception as e:
            print(f"Erreur pour l'URL {url} (Tentative {attempt + 1}/{retries}) : {e}")
        time.sleep(2)  # Pause de 2 secondes avant de réessayer
    return False

# Fonction principale pour vérifier tous les liens
async def check_all_images(urls, max_concurrency=100):
    connector = aiohttp.TCPConnector(limit_per_host=max_concurrency)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [check_image_url(session, url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)

# Vérifier les liens d'images en utilisant l'approche asynchrone
print("Vérification des liens d'images...")
urls = df['image'].tolist()

# Créer une nouvelle boucle d'événements si aucune n'existe
try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

results = loop.run_until_complete(check_all_images(urls, max_concurrency=100))

df['image_accessible'] = results
print("Vérification terminée.")

# Imprimer l'état de chaque produit et le total des produits vérifiés
total_checked = len(df)
total_accessible = sum(df['image_accessible'])
total_inaccessible = total_checked - total_accessible

for index, row in df.iterrows():
    if row['image_accessible']:
        print(f"Produit {index + 1} gardé : Image accessible.")
    else:
        print(f"Produit {index + 1} effacé : Image inaccessible.")

print(f"Total des produits vérifiés : {total_checked}")
print(f"Total des produits avec images accessibles : {total_accessible}")
print(f"Total des produits avec images inaccessibles : {total_inaccessible}")

# Filtrer les produits avec des images accessibles
print("Suppression des produits avec des images inaccessibles...")
df_cleaned = df[df['image_accessible'] == True]
print("Suppression terminée.")

# Sauvegarder le dataset nettoyé
print("Sauvegarde du dataset nettoyé...")
df_cleaned.to_csv('products_cleaned.csv', index=False)
print("Le dataset a été nettoyé et sauvegardé dans 'products_cleaned.csv'.")
print(f"Nombre de produits effacés : {total_inaccessible}")

