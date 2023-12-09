import os
import MySQLdb 
import numpy as np
import uuid
from services.db_service import connect_to_db
from datetime import datetime, timedelta

def fetch_feedback(days, which_db): # DAG

    host = os.getenv('DATABASE_HOST_' + str(which_db))
    user = os.getenv('DATABASE_USERNAME_' + str(which_db))
    passwd = os.getenv('DATABASE_PASSWORD_' + str(which_db))
    db = os.getenv('DATABASE')

    # Établir la connexion à la base de données
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

    # Obtenir la date la plus récente des notes dans la base de données
    cursor.execute("SELECT MAX(created) FROM user_feedback")
    most_recent_date = cursor.fetchone()[0]
    if most_recent_date is None:
        return np.array([])  # Retourner un tableau vide s'il n'y a pas de notes

    # Calculer la date de début pour la période de 15 jours
    start_date = most_recent_date - timedelta(days=days)

    # Requête SQL pour récupérer les notes sur la période spécifiée
    query = """
    SELECT user_rating, user_comments FROM user_feedback
    WHERE created BETWEEN %s AND %s
    """
    cursor.execute(query, (start_date, most_recent_date))
    ratings = [item[0] for item in cursor.fetchall()]
    comments = [item[1] for item in cursor.fetchall()]
    # Fermeture du curseur et de la connexion à la base de données
    cursor.close()
    connection.close()

    return {'ratings': ratings, 'comments': comments, "start_date": start_date, "end_date": most_recent_date}


def write_feedback(mission_id, user_comment, rating, prompt_version='unknown'):

    generated_id = {'id' : uuid.uuid1()}

    feedback = dict(generated_id)
    feedback['id'] = uuid.uuid1()
    feedback['user_rating'] = int(rating)
    feedback['user_comments'] = str(user_comment)
    feedback['mission_id'] = mission_id
    feedback['prompt_version'] = prompt_version
    feedback['created'] = datetime.datetime.today()
    connection = connect_to_db()

    try:
        cursor = connection.cursor()

        # Préparation et exécution de la requête SQL
        insert_query = """
            INSERT INTO user_feedback (
                id, user_rating, user_comments, mission_id, created, prompt_version
            ) VALUES (
                %s, %s, %s, %s, %s, %s
            )
            """

        cursor.execute(insert_query, (
            feedback.get("id"),
            feedback.get("user_rating"),
            feedback.get("user_comments"),
            feedback.get('mission_id'),
            feedback.get('created'),
            feedback.get('prompt_version')
        ))

    except MySQLdb.Error as err:
        raise err

    finally:
        # Fermeture de la connexion à la base de données
        if connection and connection.open:
            cursor.close()
            connection.close()
            
    # Après insertion dans la base de données
    feedback_id = feedback.get("id")
    
    # Retourner l'ID de feedback ou l'objet de feedback
    return {'id': feedback_id}


def store_feedback(feedback):
    connection = connect_to_db()

    try:
        cursor = connection.cursor()
        
        # Préparation et exécution de la requête SQL
        insert_query = """
            INSERT INTO user_feedback (
                id, user_rating, user_comments, prompt_version, mission_id, created
            ) VALUES (
                %s, %s, %s, %s, %s, %s
            )
            """
        cursor.execute(insert_query, (
            feedback.get("id"),
            feedback.get("user_rating"), 
            feedback.get("user_comments"),
            feedback.get("prompt_version"),
            feedback.get('mission_id'),
            feedback.get('created')

        ))

    except MySQLdb.Error as err:
        raise err

    finally:
        # Fermeture de la connexion à la base de données
        if connection and connection.open:
            cursor.close()
            connection.close()
