import argparse
import subprocess
import sys
import os
import pandas as pd
import mplfinance as mpf
import warnings

# Silenciar advertencias tipográficas de matplotlib
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib.font_manager")

def run_step(command, step_name):
    """Ejecuta un script externo y detiene el proceso si falla."""
    print(f"\n{'='*55}\n🚀 INICIANDO FASE: {step_name}\n{'='*55}")
    result = subprocess.run(command)
    if result.returncode != 0:
        print(f"\n[!] ERROR FATAL: La fase '{step_name}' falló. Abortando pipeline.")
        sys.exit(1)
    print(f"✅ FASE '{step_name}' COMPLETADA CON ÉXITO.")

def main():
    parser = argparse.ArgumentParser(description="Orquestador Maestro del Pipeline ETL")
    parser.add_argument("--anio", type=int, default=2024)
    parser.add_argument("--semestre", type=int, choices=[1, 2], default=1)
    parser.add_argument("--symbol", type=str, default="BTCUSDT")
    parser.add_argument("--actual", action="store_true", help="Ejecutar pipeline para el mes en curso")
    args = parser.parse_args()

    # Bifurcación en el Orquestador
    if args.actual:
        cmd_downloader = ["python", "src/downloader.py", "--actual", "--symbol", args.symbol]
        cmd_processor = ["python", "src/processor.py", "--actual", "--symbol", args.symbol]
        parquet_path = f"data/processed/{args.symbol}_24h_{pd.Timestamp.now().strftime('%Y_%m')}_ACTUAL.parquet"
    else:
        cmd_downloader = ["python", "src/downloader.py", "--anio", str(args.anio), "--semestre", str(args.semestre), "--symbol", args.symbol]
        cmd_processor = ["python", "src/processor.py", "--anio", str(args.anio), "--semestre", str(args.semestre), "--symbol", args.symbol]
        parquet_path = f"data/processed/{args.symbol}_24h_{args.anio}_S{args.semestre}.parquet"

    # Ejecución
    run_step(cmd_downloader, "Extracción de Datos de Binance")
    run_step(cmd_processor, "Limpieza y Transformación (24H)")

    # Generación de gráficos
    print(f"\n{'='*55}\n📊 INICIANDO FASE: Generación de Reportes Visuales\n{'='*55}")
    
    reports_dir = "data/reports"
    os.makedirs(reports_dir, exist_ok=True)

    if not os.path.exists(parquet_path):
        print(f"[!] Error: No se encontró el archivo procesado: {parquet_path}")
        sys.exit(1)

    print(f"[*] Leyendo base de datos columnar desde {parquet_path}...")
    df_24h = pd.read_parquet(parquet_path)

    for mes_timestamp, df_mes_grafico in df_24h.groupby(pd.Grouper(freq='ME')):
        if not df_mes_grafico.empty:
            mes_str = mes_timestamp.strftime("%Y-%m")
            output_filename = os.path.join(reports_dir, f"{args.symbol}_{mes_str}_report.png")
            
            print(f"  - Renderizando gráfico de {mes_str}...")
            mpf.plot(
                df_mes_grafico, 
                type='candle',
                style='charles',
                title=f'Tendencia {args.symbol} - {mes_str}',
                ylabel='Precio (USD)',
                volume=True,
                figratio=(12, 4),
                savefig=output_filename
            )
            
    print(f"\n🎉 ¡PIPELINE FINALIZADO EXITOSAMENTE! 🎉\n")

if __name__ == "__main__":
    main()