import numpy as np
from scipy.stats import mannwhitneyu
import numpy as np
import syncflowai
import json
import os
# Informations de connexion pour les bases de données A et B
def get_mannwhitneyu(which):
DATABASE = os.getenv('DATABASE')
DATABASE_HOST_A = os.getenv("DATABASE_HOST_A")
DATABASE_PASSWORD_A = os.getenv("DATABASE_PASSWORD_A")
DATABASE_USERNAME_A = os.getenv("DATABASE_USERNAME_A")

DATABASE_HOST_B = os.getenv("DATABASE_HOST_B")
DATABASE_PASSWORD_B = os.getenv("DATABASE_PASSWORD_B")
DATABASE_USERNAME_B = os.getenv("DATABASE_USERNAME_B")

# Utilisation de la fonction pour récupérer les notes des deux bases de données
feedback_a = syncflowai.fetch_feedback(DATABASE_HOST_A, DATABASE_USERNAME_A, DATABASE_PASSWORD_A, DATABASE, 15)
feedback_b = syncflowai.fetch_feedback(DATABASE_HOST_B, DATABASE_USERNAME_B, DATABASE_PASSWORD_B, DATABASE, 15)

ratings_a = feedback_a['ratings']
ratings_b = feedback_b['ratings']

comments_a = feedback_a['comments']
comments_b = feedback_b['comments']
# Effectuer le test de Mann-Whitney U
u_stat, p_value = mannwhitneyu(ratings_a, ratings_b)
alpha = 0.05

dico = {#"wordcount": wordcount,
        'u_stat': u_stat,
        'p_value': p_value,
        "mean_A": np.mean(ratings_a), 
        "mean_B" : np.mean(ratings_b),
        "significance_threshold": alpha}

# Interprétation
if p_value > alpha:
    dico['significance'] = "Pas de différence significative"
else:
    dico['significance'] = "Différence significative"

with open('stats.json', 'w') as outfile:
    json.dump(dico, outfile)