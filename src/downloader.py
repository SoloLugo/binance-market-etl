import os
import argparse
import requests
import hashlib
import pandas as pd
from tqdm import tqdm
from datetime import datetime

def download_file(url, local_path):
    if os.path.exists(local_path):
        print(f"[*] Ya existe: {os.path.basename(local_path)}")
        return True
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        print(f"[!] Error 404: {url}")
        return False
    total_size = int(response.headers.get('content-length', 0))
    with open(local_path, 'wb') as file, tqdm(
        desc=os.path.basename(local_path), total=total_size, unit='iB', unit_scale=True, unit_divisor=1024
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)
    return True

def verify_checksum(zip_path, checksum_path):
    with open(checksum_path, 'r') as f:
        expected_hash = f.read().split()[0]
    sha256_hash = hashlib.sha256()
    with open(zip_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return expected_hash == sha256_hash.hexdigest()

def main():
    parser = argparse.ArgumentParser(description="Descargador de Klines de Binance")
    parser.add_argument("--anio", type=int, default=2024, help="Año a descargar")
    parser.add_argument("--semestre", type=int, choices=[1, 2], default=1, help="Semestre (1 o 2)")
    parser.add_argument("--symbol", type=str, default="BTCUSDT", help="Par de monedas")
    parser.add_argument("--actual", action="store_true", help="Activa la descarga diaria del mes en curso")
    args = parser.parse_args()

    RAW_DIR = "data/raw"
    os.makedirs(RAW_DIR, exist_ok=True)

    # Bifurcación: Modo Actual (Diario) vs Modo Semestral (Mensual)
    if args.actual:
        hoy = datetime.now()
        print(f"\nIniciando ingesta DIARIA: {args.symbol} | Mes en curso ({hoy.strftime('%Y-%m')})")
        start_date = f"{hoy.year}-{hoy.month:02d}-01"
        fechas = pd.date_range(start=start_date, end=hoy, freq="D")
        BASE_URL = f"https://data.binance.vision/data/futures/um/daily/klines/{args.symbol}/15m/"
        formato_fecha = "%Y-%m-%d"
    else:
        print(f"\nIniciando ingesta MENSUAL: {args.symbol} | Semestre {args.semestre} de {args.anio}")
        start_date = f"{args.anio}-01-01" if args.semestre == 1 else f"{args.anio}-07-01"
        end_date = f"{args.anio}-06-01" if args.semestre == 1 else f"{args.anio}-12-01"
        fechas = pd.date_range(start=start_date, end=end_date, freq="MS")
        BASE_URL = f"https://data.binance.vision/data/futures/um/monthly/klines/{args.symbol}/15m/"
        formato_fecha = "%Y-%m"

    for fecha in fechas:
        fecha_str = fecha.strftime(formato_fecha)
        zip_filename = f"{args.symbol}-15m-{fecha_str}.zip"
        
        zip_url, checksum_url = BASE_URL + zip_filename, BASE_URL + zip_filename + ".CHECKSUM"
        zip_local, checksum_local = os.path.join(RAW_DIR, zip_filename), os.path.join(RAW_DIR, zip_filename + ".CHECKSUM")
        
        if download_file(checksum_url, checksum_local):
            if download_file(zip_url, zip_local):
                if verify_checksum(zip_local, checksum_local):
                    print(f"  [OK] {fecha_str} verificado.")
                else:
                    print(f"  [ERROR] {zip_filename} corrupto.")

if __name__ == "__main__":
    main()