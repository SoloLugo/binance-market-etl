import os
import argparse
import pandas as pd
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="Procesador y Transformador")
    parser.add_argument("--anio", type=int, default=2024)
    parser.add_argument("--semestre", type=int, choices=[1, 2], default=1)
    parser.add_argument("--symbol", type=str, default="BTCUSDT")
    parser.add_argument("--actual", action="store_true", help="Procesa los datos diarios del mes en curso")
    args = parser.parse_args()

    RAW_DIR, PROCESSED_DIR = "data/raw", "data/processed"
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    if args.actual:
        hoy = datetime.now()
        start_date = f"{hoy.year}-{hoy.month:02d}-01"
        fechas = pd.date_range(start=start_date, end=hoy, freq="D")
        formato_fecha = "%Y-%m-%d"
        parquet_filename = f"{args.symbol}_24h_{hoy.strftime('%Y_%m')}_ACTUAL.parquet"
    else:
        start_date = f"{args.anio}-01-01" if args.semestre == 1 else f"{args.anio}-07-01"
        end_date = f"{args.anio}-06-01" if args.semestre == 1 else f"{args.anio}-12-01"
        fechas = pd.date_range(start=start_date, end=end_date, freq="MS")
        formato_fecha = "%Y-%m"
        parquet_filename = f"{args.symbol}_24h_{args.anio}_S{args.semestre}.parquet"

    columnas = [
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ]

    lista_dfs = []
    print(f"[*] Buscando datos en {RAW_DIR}...")
    
    for fecha in fechas:
        fecha_str = fecha.strftime(formato_fecha)
        zip_local = os.path.join(RAW_DIR, f"{args.symbol}-15m-{fecha_str}.zip")
        if os.path.exists(zip_local):
            df_temp = pd.read_csv(zip_local, names=columnas, dtype=str)
            lista_dfs.append(df_temp)

    if not lista_dfs:
        print("[!] Proceso abortado: No hay datos para procesar.")
        return

    print("[*] Uniendo y limpiando impurezas...")
    df = pd.concat(lista_dfs, ignore_index=True)
    df = df[df['open_time'] != 'open_time'].copy()
    
    df['open_time'] = pd.to_numeric(df['open_time'])
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df.set_index('open_time', inplace=True)

    columnas_numericas = ['open', 'high', 'low', 'close', 'volume']
    df[columnas_numericas] = df[columnas_numericas].astype(float)

    print("[*] Comprimiendo a velas de 24H...")
    df_24h = df.resample('1D').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()

    parquet_path = os.path.join(PROCESSED_DIR, parquet_filename)
    df_24h.to_parquet(parquet_path)
    print(f"✅ Datos listos en: {parquet_path}")

if __name__ == "__main__":
    main()