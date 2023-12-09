from services.db_service import fetch_feedback
import numpy as np
from scipy.stats import mannwhitneyu
import os
from nltk.corpus import stopwords
from collections import Counter
import re
import nltk
import MySQLdb

def get_stats(days):

    # Utilisation de la fonction pour récupérer les notes des deux bases de données
    feedback_a = fetch_feedback(days, which_db="A")
    feedback_b = fetch_feedback(days, which_db="B")

    ratings_a = feedback_a['ratings']
    ratings_b = feedback_b['ratings']

    start_date = feedback_a['start_date']
    end_date = feedback_a['end_date']
    # Effectuer le test de Mann-Whitney U
    u_stat, p_value = mannwhitneyu(ratings_a, ratings_b)
    alpha = 0.05

    dico = {#"wordcount": wordcount,
            'start_date': start_date,
            'end_date': end_date,
            'n_values_A': len(ratings_a),
            'n_values_B': len(ratings_b),
            'U_stat': u_stat,
            'p_value': p_value,
            "mean_A": np.mean(ratings_a), 
            "mean_B" : np.mean(ratings_b),
            "significance_threshold": alpha}

    # Interprétation
    if p_value > alpha:
        dico['significance'] = "Pas de différence significative"
    else:
        dico['significance'] = "Différence significative"

    return dico

def get_wordcount(which_db):
    # Paramètres de connexion à la base de données
    host = os.getenv('DATABASE_HOST_' + str(which_db))
    user = os.getenv('DATABASE_USERNAME_' + str(which_db))
    passwd = os.getenv('DATABASE_PASSWORD_' + str(which_db))
    db = os.getenv('DATABASE')


    # Connexion à la base de données
    connection = MySQLdb.connect(
        host=host,
        user=user,
        passwd=passwd,
        db=db,
        autocommit=True,
        ssl_mode="VERIFY_IDENTITY",
        ssl={"ca": "/etc/secrets/cert.pem"}
    )
    cursor = connection.cursor()

    # Requête SQL pour récupérer les 50 derniers commentaires
    sql = "SELECT user_comments FROM user_feedback WHERE user_rating BETWEEN 1 AND 3 LIMIT 150"
    cursor.execute(sql)

    # Récupération des données
    comments = [item[0] for item in cursor.fetchall()]
    nltk.download('stopwords')

    # Liste des stop words
    stop_words = set(stopwords.words('english') + ['ai'])

    # Nettoyage et comptage des mots
    words = []
    for comment in comments:
        comment = re.sub(r'\W+', ' ', comment.lower())
        words.extend([word for word in comment.split() if word not in stop_words])

    word_freq = Counter(words)

    # Utilisation de most_common pour récupérer les 20 termes les plus fréquents
    top_words_freq = word_freq.most_common(40)

    # Conversion des données en format JSON
    wordcloud_data = [{'name': word, 'value': freq} for word, freq in top_words_freq]
    # Fermeture de la connexion à la base de données
    cursor.close()
    connection.close()

    return wordcloud_data

