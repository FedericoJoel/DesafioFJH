# Challenge ML

Sistema capaz de buscar en una cuenta de Gmail los correos que contengan la palabra DevOps ya sea en el Subject o en el contenido del mismo, almacenándolos en una base de datos MYSQL.

## Por que Python
Por que elegi este lenguaje?
Este ejercicio esta pensado como un desafío. Siguiendo este pensamiento, elegí python por que es el lenguaje que ustedes utilizan habitualmente. Si bien este no es un lenguaje que domine, siempre es bueno utilizar las oportunidades como esta para aprender alguno nuevo.

## Requerimientos
Cumple con el requerimiento funcional, intentado mantener el script lo mas simple posible.
Dentro de este hay comentarios en el código para facilitar su lectura.
## Getting Started

### Prerequisites

    1.Python 2.7
    2.Pypi

Por medio del comando pip podemos realizar la instalación de las dependencias (espero no haber olvidado ninguna).

```
sudo pip install -r requirements.txt
```

### Installing

    1. Copiamos la clave del cliente client_secret.json (enviado por correo) en el root del repositorio junto con el script.py
    2. Verificamos tener el usuario: root password :"", o modificamos el usuario de base de datos en la linea 95, verificando que el utilizado no necesite sudo para establecer conexión.
    3. Iniciamos el servidor MySQL en localhost
    4. Ejecutamos script.py
