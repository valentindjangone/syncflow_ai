import MySQLdb
from collections import Counter
import re
import datetime
import json
from nltk.corpus import stopwords
import os

os.chdir('./wordcloud/data/')

# Paramètres de connexion à la base de données
host = os.getenv('DATABASE_HOST')
user = os.getenv('DATABASE_USERNAME')
passwd = os.getenv('DATABASE_PASSWORD')
db = os.getenv('DATABASE')


# Connexion à la base de données
conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db)
cursor = conn.cursor()

# Requête SQL pour récupérer les 50 derniers commentaires
sql = "SELECT user_comments FROM user_feedback WHERE user_rating BETWEEN 1 AND 3 LIMIT 50"
cursor.execute(sql)

# Récupération des données
comments = [item[0] for item in cursor.fetchall()]

# Liste des stop words
stop_words = set(stopwords.words('english'))

# Nettoyage et comptage des mots
words = []
for comment in comments:
    comment = re.sub(r'\W+', ' ', comment.lower())
    words.extend([word for word in comment.split() if word not in stop_words])

word_freq = Counter(words)

# Générer un nom de fichier timestampé
timestamp = datetime.datetime.today().strftime("%Y-%m-%d")
filename = f'wordcloud_data_{timestamp}.json'

# Conversion des données en format JSON
wordcloud_data = [{'word': word, 'frequency': freq} for word, freq in word_freq.items()]

# Enregistrement des données dans un fichier JSON
with open(filename, 'w', encoding='utf-8') as jsonfile:
    json.dump(wordcloud_data,jsonfile, ensure_ascii=False, indent=4)

print(f"Les données ont été enregistrées dans '{filename}'")

# Fermeture de la connexion à la base de données
cursor.close()
conn.close()