"""
extraer_info.py

Autor: Diego Garcia

Este script Python tiene como objetivo extraer información de un archivo resultado de un modelo de computer vision que detecta informacion documental importante. La información extraída incluye el número de matrícula, la fecha de impresión,
la ubicación (departamento, municipio y vereda), y el estado del folio.

Uso:
python extraer_info.py <ruta_archivo_json>

Ejemplo de uso:
python extraer_info.py 'archivo.json'
"""

import json
import re
from datetime import datetime
import sys
from unidecode import unidecode

# Diccionario que mapea nombres de meses en español a números de mes
meses = {
    'enero': 1,
    'febrero': 2,
    'marzo': 3,
    'abril': 4,
    'mayo': 5,
    'junio': 6,
    'julio': 7,
    'agosto': 8,
    'septiembre': 9,
    'octubre': 10,
    'noviembre': 11,
    'diciembre': 12
}

def extraer_informacion(ruta_archivo_json):
    """
    Extrae información específica de un archivo JSON.

    Parámetros:
    - ruta_archivo_json (str): Ruta del archivo JSON.

    Retorna:
    - dict: Diccionario con la información extraída.
    """
    
    with open(ruta_archivo_json, 'r', encoding='utf-8') as archivo:
        datos = json.load(archivo)

    def extraer_de_texto(patron, texto):
        """
        Busca un patrón en un texto y devuelve la coincidencia.

        Parámetros:
        - patron (str): Expresión regular a buscar.
        - texto (str): Texto en el que buscar.

        Retorna:
        - re.Match o None: Coincidencia o None si no hay coincidencia.
        """
        coincidencia = re.search(patron, texto)
        return coincidencia if coincidencia else None
    
    # Patrones regex para la deteccion de las entidades de interes
    patron_matricula = r'Nro Matr[ií]cula: (\S+)'
    patron_fecha = r'Impreso el (.+)'
    patron_ubicacion = r'CIRCULO REGISTRAL: \d+.*?DEPTO: (.*?)\s*MUNICIPIO: (.*?)\s*VEREDA: (.+)'
    patron_estado = r'ESTADO DEL FOLIO:'

    numero_matricula = None
    fecha_impresion = None
    departamento = None
    municipio = None
    vereda = None
    folio_encontrado = None
    estado_folio = None

    bloques = datos['Blocks']
    for i, bloque in enumerate(bloques):
        if bloque['BlockType'] == 'LINE':

            texto = bloque['Text'].strip()
            
            numero_matricula = numero_matricula or extraer_de_texto(patron_matricula, unidecode(texto))
            
            fecha_impresion = fecha_impresion or extraer_de_texto(patron_fecha, texto)

            coincidencia = re.search(patron_ubicacion, texto)
            if coincidencia:
                departamento = coincidencia.group(1)
                municipio = coincidencia.group(2)
                vereda = coincidencia.group(3)

            folio_encontrado = folio_encontrado or extraer_de_texto(patron_estado, texto)

            if folio_encontrado is not None:
                siguiente_bloque = bloques[i + 1]
                estado_folio = siguiente_bloque.get('Text', '').strip()
                    
            if all([numero_matricula, fecha_impresion, departamento, municipio, vereda, estado_folio]):
                break

    partes_fecha = fecha_impresion.group(1).split()
    fecha_formateada = datetime(int(partes_fecha[4]), meses[partes_fecha[2].lower()], int(partes_fecha[0])).strftime("%Y/%m/%d")
    return {
        'numero_matricula': numero_matricula.group(1),
        'fecha_impresion': fecha_formateada,
        'info_ubicacion': {
            'departamento': departamento,
            'municipio': municipio,
            'localidad': vereda
        },
        'estado_folio': estado_folio
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python extraer_info.py <ruta_archiv_json>")
    else:
        ruta_archivo_json = sys.argv[1]
        resultado = extraer_informacion(ruta_archivo_json)

        if resultado:
            print("Información extraída:")
            print(f"Número de Matrícula: {resultado['numero_matricula']}")
            print(f"Fecha de Impresión: {resultado['fecha_impresion']}")
            print(f"Departamento: {resultado['info_ubicacion']['departamento']}")
            print(f"Municipio: {resultado['info_ubicacion']['municipio']}")
            print(f"Vereda: {resultado['info_ubicacion']['localidad']}")
            print(f"Estado del Folio: {resultado['estado_folio']}")
