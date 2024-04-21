import serial
import pymongo
import json
import time
from bson import ObjectId  # Importa la clase ObjectId de bson

# Configuración del puerto serial
puerto_serial = '/dev/ttyUSB0'  # Ajustar según el puerto conectado al Arduino
baudios = 9600

# Configuración de la conexión a MongoDB
mongo_url = "mongodb+srv://Miky:chavez123@cluster0.irs3owq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
mongo_db = "sensores"
mongo_collection = "datos"

# Función para serializar documentos MongoDB a JSON
def serialize_mongodb_documents(documents):
    serialized_docs = []
    for doc in documents:
        # Convierte el ObjectId a una cadena antes de serializar el documento
        doc['_id'] = str(doc['_id'])
        serialized_docs.append(doc)
    return serialized_docs

# Configuración de la conexión serial
try:
    arduino = serial.Serial(puerto_serial, baudios, timeout=1)
    print("Conectado al Arduino")
except serial.SerialException as e:
    print(f"Error al conectar al Arduino: {e}")
    exit(1)

# Bucle principal
while True:
    # Inicializar conexión a MongoDB
    try:
        cliente_mongo = pymongo.MongoClient(mongo_url)
        db = cliente_mongo[mongo_db]
        coleccion = db[mongo_collection]
        print("Conectado a MongoDB")
    except pymongo.errors.ConnectionFailure as e:
        print(f"Error al conectar a MongoDB: {e}")
        continue

    # Leer datos del Arduino
    datos_arduino = arduino.readline().decode('utf-8').strip()
    if datos_arduino:
        # Limpiar los datos recibidos y dividirlos en partes
        datos_sensor = datos_arduino.strip().split(':')
        if len(datos_sensor) == 3:
            identificador = datos_sensor[0]
            valor_str = datos_sensor[1].strip().split()[0]  # Obtener la primera parte antes de cualquier espacio
            unidad = datos_sensor[2].strip()
            # Convertir el valor a flotante si es posible
            try:
                valor = float(valor_str)
            except ValueError:
                print(f"Error: No se pudo convertir '{valor_str}' a flotante")
                continue

            # Crear diccionario con datos
            dato_sensor = {
                "identificador": identificador,
                "valor": valor,
                "unidad": unidad
            }

            # Guardar datos en MongoDB
            try:
                coleccion.insert_one(dato_sensor)
                print("Datos guardados en MongoDB")
            except Exception as e:
                print(f"Error al guardar datos en MongoDB: {e}")

    # Obtener documentos de MongoDB
    documentos_mongodb = coleccion.find({})

    # Serializar los documentos
    documentos_serializados = serialize_mongodb_documents(documentos_mongodb)

    # Crear archivo JSON con todos los datos
    try:
        with open('datos_sensores.json', 'w') as archivo_json:
            json.dump(documentos_serializados, archivo_json, indent=4)
        print("Archivo JSON creado")
    except Exception as e:
        print(f"Error al crear archivo JSON: {e}")

    # Esperar un segundo antes de leer de nuevo
    time.sleep(1)
