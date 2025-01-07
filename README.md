# Flask-Web-App
 Plateforme de E-commerce 

Site Web crée avec flask 

-Filtrage des produit

-Detection d'interactions et des utilisateur et enregistrement dans des datasets



Prochaine etape : 

!! l'ajout de recommendation de produit similaire en bas sur la page product 

!! quelques filtrage sont corrompu dans index.html

et finalement hebergement avec orender

MLOPS_Project/

├── Data/                     # Repertoire pour contenir les datasets

│   ├── products.csv          # Extraite depuis kaggle et ensuite netoyè (amazon products)

│   ├── users.csv             #  Detectè a partir des cookies de session

│   ├── interactions.csv      # Chaque interaction (viewed,purchased added to cart) est enregistrè

│   └── predictions.csv       # Les recommendation sont recu depuis le modele dans https://github.com/Wassim-kobrosly/MLOPS.git

├── Templates/                # Convertir products.csv en fichier .db pour la rapidité des requettes

│   ├── Index.html            # Acceuil de tout les produits avec possibilté de filtrage,recherche et affichage des recommendations

│   ├── Product.html          # Page pour chaque produit
