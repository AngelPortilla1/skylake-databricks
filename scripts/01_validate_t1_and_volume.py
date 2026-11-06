# Databricks notebook source
# MAGIC %md
# MAGIC # Validación SKY-004 (Volume I/O) y SKY-006 (T1: Salida a Internet)

# COMMAND ----------

# SKY-004: Prueba de escritura y lectura en el Volume
path = '/Volumes/skylake/bronze/landing/_test/hello.txt'
dbutils.fs.mkdirs('/Volumes/skylake/bronze/landing/_test')
dbutils.fs.put(path, 'hola skylake', True)
print("Lectura desde Volume:", dbutils.fs.head(path))

# COMMAND ----------

# SKY-006 (T1): Prueba de salida a internet desde compute serverless
import requests

urls = [
    'https://opensky-network.org/api/states/all?lamin=4&lomin=-75&lamax=5&lomax=-73',
    'https://github.com',
    'https://pypi.org',
]

for u in urls:
    try:
        r = requests.get(u, timeout=10)
        print(u, '->', r.status_code)
    except Exception as e:
        print(u, '-> FALLA', type(e).__name__, str(e))
