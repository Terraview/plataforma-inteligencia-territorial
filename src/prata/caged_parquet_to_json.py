import shutil
from pathlib import Path
from pyspark.sql import SparkSession

#frufu colorido pra printar mensagens de log
RED = "\033[91m"
GREEN = "\033[92m"
BOLD = "\033[1m"
RESET = "\033[0m"

def consolidate_caged_silver():
  # 1. Inicializa a sessão Spark
  spark = (
      SparkSession.builder.appName("CAGED_Silver_Consolidation")
      .config("spark.driver.memory", "4g")
      .config("spark.sql.parquet.filterPushdown", "true")
      .getOrCreate()
  )

  spark.sparkContext.setLogLevel("WARN")

  # 2. Resolução de Caminhos
  root_dir = Path(__file__).resolve().parents[2]
  silver_dir = root_dir / "Data_Silver"

  path_2019 = str(silver_dir / "caged_2019" / "*.parquet")
  path_2020_2023 = str(silver_dir / "caged_2020_2023" / "*.parquet")

  json_output_dir = root_dir / "Caged_json"
  json_output_dir.mkdir(parents=True, exist_ok=True)

  temp_output_dir = root_dir / "_temp_json_output"
  final_json_file = json_output_dir / "CAGED_2019_2023.json"

  # 3. Leitura das origens
  df_2019 = spark.read.parquet(path_2019)
  df_recent = spark.read.parquet(path_2020_2023)

  # --- VERIFICAÇÃO 1: Contagem por origem ---
  count_2019 = df_2019.count()
  count_recent = df_recent.count()
  total_esperado = count_2019 + count_recent

  print(f"{GREEN}{BOLD}[*] Registos no CAGED 2019: {count_2019:,}")
  print(f"[*] Registos no CAGED 2020-2023: {count_recent:,}")
  print(f"[*] Total esperado após união: {total_esperado:,}{RESET}")

  # 4. Unificação dos Schemas
  df_unified = df_2019.unionByName(df_recent, allowMissingColumns=True)

  # --- VERIFICAÇÃO 2: Validar total unificado ---
  total_unificado = df_unified.count()
  print(f"{GREEN}{BOLD}[*] Total unificado no Spark:{total_unificado:,}{RESET}")

  if total_unificado == total_esperado:
    print(f"{GREEN}{BOLD}[OK] Validação OK: Nenhum registo foi perdido na união!{RESET}")
  else:
    print(f"{RED}{BOLD}[!] Alerta: A contagem total difere da soma das partes!{RESET}")

  try:
    # 5. Escrita do ficheiro JSON
    df_unified.coalesce(1).write.mode("overwrite").json(str(temp_output_dir))

    part_files = list(temp_output_dir.glob("part-*.json"))

    if part_files:
      shutil.copyfile(part_files[0], final_json_file)

      # --- VERIFICAÇÃO 3: Confirmar leitura do ficheiro final gerado ---
      df_final_check = spark.read.json(str(final_json_file))
      total_no_json = df_final_check.count()

      print(
          f"\n{GREEN}[Ok] Processo Concluído!{RESET}\n"
          f"    - Ficheiro gerado: {final_json_file}\n"
          f"    - Total de linhas gravadas no JSON: {total_no_json:,}\n"
          f"    - Tamanho do ficheiro: "
          f"{final_json_file.stat().st_size / (1024*1024):.2f} MB"
      )
    else:
      print("{RED}[!] Erro: Nenhum ficheiro part-*.json foi encontrado.{RESET}")

  finally:
    if temp_output_dir.exists():
      shutil.rmtree(temp_output_dir)


if __name__ == "__main__":
  consolidate_caged_silver()