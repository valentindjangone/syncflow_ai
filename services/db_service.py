import os
import MySQLdb
import pandas as pd
import json
from fastapi import HTTPException
from dotenv import load_dotenv

def connect_to_db():
    load_dotenv()
    db_host = os.getenv("DATABASE_HOST_A")
    db_user = os.getenv("DATABASE_USERNAME_A")
    db_password = os.getenv("DATABASE_PASSWORD_A")
    db_name = os.getenv("DATABASE")
    if not all([db_host, db_user, db_password, db_name]):
        raise Exception("Les informations de connexion à la base de données sont incomplètes.")
    if 'valentin' and 'apple' in str(os.environb):
        connection = MySQLdb.connect(
            host=db_host,
            user=db_user,
            passwd=db_password,
            db=db_name,
            autocommit=True,
            ssl_mode="VERIFY_IDENTITY",
            ssl={"ca": "/etc/ssl/cert.pem"}
        )
    else:
        connection = MySQLdb.connect(
            host=db_host,
            user=db_user,
            passwd=db_password,
            db=db_name,
            autocommit=True,
            ssl_mode="VERIFY_IDENTITY",
            ssl={"ca": "/etc/secrets/cert.pem"}
    )
    return connection

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


def fetch_data(query):
    with connect_to_db() as db:
        cur = db.cursor()
        cur.execute(query)
        columns = [col[0] for col in cur.description]
        data = pd.DataFrame(list(cur.fetchall()), columns=columns)
        cur.close()
    return data



def store_raw_response(raw_response):
    connection = connect_to_db()

    try:
        cursor = connection.cursor()

        # Préparation et exécution de la requête SQL
        insert_query = """
            INSERT INTO raw_response (
                id, created, choices, model, object, system_fingerprint, usage, cost
            ) VALUES (
                %s, FROM_UNIXTIME(%s), %s, %s, %s, %s, %s, %s
            )
            """
        cursor.execute(insert_query, (
            raw_response["id"], 
            raw_response["created"], 
            json.dumps(raw_response["choices"][0]), 
            raw_response["model"], 
            raw_response["object"], 
            raw_response["system_fingerprint"], 
            json.dumps(raw_response["usage"]),
            json.dumps(raw_response["cost"])
        ))

    except MySQLdb.Error as err:
        raise err

    finally:
        # Fermeture de la connexion à la base de données
        if connection and connection.open:
            cursor.close()
            connection.close()

def store_processed_mission(mission_dict):
    connection = connect_to_db()
    try:
        cursor = connection.cursor()
        insert_query = """
            INSERT INTO processed_mission (id, created, mission_name, mission_abstract, mission_detail, roles, budget, metadata_id) 
            VALUES (%s, FROM_UNIXTIME(%s), %s, %s, %s, %s, %s, %s)
        """
        created = mission_dict["created"]
        budget = mission_dict.get("budget")
        if budget is not None:
            budget = json.dumps(budget)
        name = mission_dict.get("name")
        if name is not None:
            name = json.dumps(name)
        abstract = mission_dict.get("abstract")
        if abstract is not None:
            abstract = json.dumps(abstract)
        detail = mission_dict.get("detail")
        if detail is not None:
            detail = json.dumps(detail)
        roles = mission_dict.get("roles")
        if roles is not None:
            roles = json.dumps(roles)

        cursor.execute(insert_query, (
            mission_dict["id"],
            created,
            name,
            abstract,
            detail,
            roles,  # Utilise une liste vide si "roles" n'est pas présent
            budget,  # Utilise None si "budget" n'est pas présent
            mission_dict["metadata_id"]
        ))

    except Exception as e:
            # Cela capturera toutes les exceptions, y compris KeyError, MySQLdb.Error, etc.
            raise HTTPException(status_code=500, detail=f"Erreur rencontrée : {str(e)}")

    finally:
        if connection and connection.open:
            cursor.close()
            connection.close()

def update_mission_details(mission_id, mission_update):
    # Connexion à la base de données MySQL en utilisant la fonction existante
    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        # Construction de la requête SQL pour mettre à jour la mission
        update_query = "UPDATE processed_mission SET "
        update_parts = []
        params = []

        if mission_update.abstract is not None:
            update_parts.append("mission_abstract = %s")
            params.append(mission_update.abstract)

        if mission_update.detail is not None:
            update_parts.append("mission_detail = %s")
            params.append(mission_update.detail)

        # Ajoutez d'autres champs ici si nécessaire

        update_query += ", ".join(update_parts)
        update_query += "WHERE id = %s"
        params.append(str(mission_id))

        # Exécution de la requête
        cursor.execute(update_query, params)
        conn.commit()

    except MySQLdb.Error as e:
        print(f"Error updating mission: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    finally:
        cursor.close()
        conn.close()

    return {"message": "Mission updated successfully"}

