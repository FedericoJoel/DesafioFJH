from __future__ import print_function
import httplib2
import os
import re
import MySQLdb

from apiclient import discovery
from apiclient import errors
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Challenge'

def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:
            credentials = tools.run(flow, store)
        print('Guardamos las credenciales en: ' + credential_path)
    return credentials

def ListMessagesWithWord(service, user_id, query=''):
  try:
    response = service.users().messages().list(userId=user_id,
                                               q=query).execute()
    messages = []
    #Obtenemos los mensajes y los de todas las paginas
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id, q=query,
                                         pageToken=page_token).execute()
      messages.extend(response['messages'])

    return messages
  except errors.HttpError, error:
    print ('Opps..Hubo un problema al conectarse: %s' % error)

    if __name__ == '__main__':
        main()

def GetMessage(service, user_id, msg_id):
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id,fields='payload,snippet,id',format='metadata', metadataHeaders=['subject','from','date']).execute()

    return message
  except errors.HttpError, error:
    print ('An error occurred: %s' % error)

def ContainInSubjectOrBody(mensaje,word):
    # Obtenemos el valor del Subject y content
    subject = mensaje['payload']['headers'][1]['value']
    content = mensaje['snippet']

    # Utilizamos RE por que queremos encontrar la palabra DevOps. Pero no queremos encontrarla como substring holaDevOpsHola
    matchInSubject = re.search(r'\bDevOps\b',subject)
    matchInContent = re.search(r'\bDevOps\b',content)
    if matchInSubject or matchInContent:
        return True

def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    # Obtenemos los mensajes que contengan DevOps en algun lugar.
    messages = ListMessagesWithWord(service,'me','+DevOps')

    if not messages:
        print('No se encontraron mensajes con la palabra DevOps')
    else:
        db = MySQLdb.connect("localhost", "root","")
        cursor = db.cursor()

        # Creamos la base de datos
        # Ocultamos el warning
        cursor.execute("SET sql_notes = 0; ")
        cursor.execute("create database IF NOT EXISTS challenge;")

        # Creamos la tabla si es que no existe
        # Como en muchas partes, esto se podría complejizar, verificar si el registro ya existe al agregarlo y que sea incremental el resguardo de los correos.
        # En este caso me apegue al requerimiento manteniendo la simpleza, cada vez que se ejecuta, elimina la tabla en caso de que exista y la crea nuevamente
        # Eliminando así los correos que ya habían quedado registrados.
        cursor.execute("SET sql_notes = 0; ")
        cursor.execute("drop table IF EXISTS  challenge.correos")
        cursor.execute("create table challenge.correos (id int NOT NULL AUTO_INCREMENT,remitente VARCHAR(70),subject varchar(70), fecha varchar(70),PRIMARY KEY(id));")
        cursor.execute("SET sql_notes = 1; ")
        cursor.close()

        for message in messages:

            # Obtenemos para cada id la informacion que nos es relevante del correo.
            mensaje = GetMessage(service,'me',message['id'])

            # Verificamos que la palabra este en el Subject o en el Body
            # Tenemos que hacerlo asi ya que Gmail no nos permite buscar unicamente en el body
            if(ContainInSubjectOrBody(mensaje, 'DevOps')):
                print('Guardamos el correo con ID:' + mensaje['id'])

                # Insertamos el correo
                cursor = db.cursor()

                # Preparamos para insertar
                # En estee caso, no habiendo un requerimiento donde tenga que usar o mostrar la info, lo inserte de la forma mas facil.
                # Se podria mapear el tipo de dato que viene de la api y guardarlo como DATE en la BD
                sql = "INSERT INTO challenge.correos (remitente,subject,fecha) VALUES (%s,%s,%s);"

                # Queda bastante acoplado a la respuesta de la api en este caso, se podria generar una funcion para abstraerse del orden de los elementos.
                rem = mensaje['payload']['headers'][0]['value']
                sub = mensaje['payload']['headers'][1]['value']
                dat = mensaje['payload']['headers'][2]['value']

                t = (rem,sub,dat)
                cursor.execute(sql,t)

                # Comiteamos los cambios
                db.commit()
                cursor.close()

        db.close()

if __name__ == '__main__':
    main()

