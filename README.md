# Pipeline ETL Automatizado de Datos de Binance (BTCUSDT)

Este proyecto es un pipeline de extracción, transformación y carga (ETL) desarrollado en Python y contenerizado con **Docker**, diseñado para descargar datos históricos o en tiempo real de Binance (Klines de futuros), procesarlos y generar reportes visuales limpios en formato de velas diarias (24H).

---

##  Requisitos previos

Para ejecutar este proyecto en tu equipo, solo necesitas tener instalado:
* **Docker** y **Docker Compose** en tu sistema operativo.
* Git (si decides clonar el repositorio).

---

##  Obtención del Proyecto

Puedes obtener el código de dos formas distintas:

### Opción A: Clonando el repositorio con Git
Abre tu terminal y ejecuta:

git clone [https://github.com/TU_USUARIO/binance-market-etl.git](https://github.com/TU_USUARIO/binance-market-etl.git)
cd binance-market-etl


### Opción B: Descargando el archivo ZIP desde GitHub
-Ve a la página principal del repositorio en GitHub.
-Haz clic en el botón verde "Code" y selecciona "Download ZIP".
-Descomprime el archivo ZIP descargado en una carpeta de tu preferencia.
-Abre tu terminal (PowerShell en Windows, o terminal en Linux/Mac) y sitúate dentro de esa carpeta.

## Construir la imagen del entorno
docker compose build

## Descargar y procesar un semestre histórico específico
docker compose run --rm binance-env python src/main.py --anio #### --semestre #

## Descargar y procesar el mes actual en tiempo real
docker compose run --rm binance-env python src/main.py --actual
