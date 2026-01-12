from db_functions import run_action
try:
    run_action("UPDATE inscricoes SET status = 'Confirmada' WHERE status = 'Confirmado'")
    print("Status corrigidos com sucesso.")
except Exception as e:
    print(f"Erro: {e}")
