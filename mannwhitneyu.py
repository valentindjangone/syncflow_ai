import numpy as np
from scipy.stats import mannwhitneyu
import numpy as np
import syncflowai
import json
# Informations de connexion pour les bases de données A et B
DATABASE = "syncflow"
DATABASE_HOST_A = "aws.connect.psdb.cloud"
DATABASE_PASSWORD_A = "pscale_pw_LhQn0Ezma4br1IEIAWpIuOpW3F6130vbI3PHayY4e5x"
DATABASE_USERNAME_A = "3c1lfs5yya7lrubhzbpi"

DATABASE_HOST_B = "aws.connect.psdb.cloud"
DATABASE_PASSWORD_B = "pscale_pw_YEti6llWKsSaYC78C0I7vsrr4Qb0UwwPZw3MhYMDhNj"
DATABASE_USERNAME_B = "ced19wlcwfmfbt3wb7u2"

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