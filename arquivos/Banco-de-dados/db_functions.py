
import psycopg2
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode="require" if os.getenv("DB_SSL") == "true" else "prefer"
    )

def run_query(query, params=None):
    conn = get_connection()
    try:
        df = pd.read_sql(query, conn, params=params)
    finally:
        conn.close()
    return df

def run_action(query, params=None):
    """Runs INSERT, UPDATE, DELETE"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        cur.close()
    finally:
        conn.close()

# --- BENEFICIARIES ---
def get_beneficiarios(filtro_nome=None, filtro_regiao=None):
    # CORRIGIDO: nome da tabela 'beneficiarios'
    query = "SELECT * FROM beneficiarios WHERE 1=1"
    params = []
    if filtro_nome:
        query += " AND (nome ILIKE %s OR email ILIKE %s)"
        params.extend([f"%{filtro_nome}%", f"%{filtro_nome}%"])
    if filtro_regiao and filtro_regiao != "Todas":
        query += " AND regiao = %s"
        params.append(filtro_regiao)
    query += " ORDER BY id_beneficiario DESC"
    return run_query(query, tuple(params))

def check_beneficiario_exists(nome, telefone, email):
    # Verifica se existe alguém com mesmo Nome E (Telefone OU Email)
    query = """
    SELECT id_beneficiario FROM beneficiarios 
    WHERE nome ILIKE %s 
    AND (
        (telefone = %s AND telefone <> '') 
        OR 
        (email = %s AND email <> '')
    )
    """
    # Se email/tel forem vazios, evita match falso, mas o python trata isso
    res = run_query(query, (nome, telefone, email))
    return not res.empty

def add_beneficiario(nome, idade, telefone, email, regiao):
    # (Opcional) Poderíamos checar aqui dentro também, mas vamos deixar pro frontend avisar
    query = """
    INSERT INTO beneficiarios (nome, idade, telefone, email, regiao)
    VALUES (%s, %s, %s, %s, %s)
    """
    run_action(query, (nome, idade, telefone, email, regiao))

def update_beneficiario(id_beneficiario, nome, idade, telefone, email, regiao):
    query = """
    UPDATE beneficiarios 
    SET nome=%s, idade=%s, telefone=%s, email=%s, regiao=%s
    WHERE id_beneficiario=%s
    """
    run_action(query, (nome, idade, telefone, email, regiao, id_beneficiario))

def delete_beneficiario(id_beneficiario):
    # Primeiro remove referencias em inscricoes (Constraint FK)
    # Exclui inscricoes do usuario
    run_action("DELETE FROM inscricoes WHERE id_beneficiario = %s", (id_beneficiario,))
    # Exclui o usuario
    run_action("DELETE FROM beneficiarios WHERE id_beneficiario = %s", (id_beneficiario,))

# --- EVENTOS ---
def get_eventos():
    # Retorna eventos com contagem de inscritos
    query = """
    SELECT e.id_evento, e.nome, e.data_evento, e.horario, e.local, e.descricao, e.vagas, e.status,
           COUNT(i.id_inscricao) as inscritos
    FROM eventos e
    LEFT JOIN inscricoes i ON e.id_evento = i.id_evento
    GROUP BY e.id_evento
    ORDER BY e.data_evento
    """
    return run_query(query)

def add_evento(nome, data, horario, local, descricao, vagas, status='Agendado'):
    query = """
    INSERT INTO eventos (nome, data_evento, horario, local, descricao, vagas, status)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    run_action(query, (nome, data, horario, local, descricao, vagas, status))
    
def update_evento(id_evento, nome, data, horario, local, descricao, vagas):
    query = """
    UPDATE eventos 
    SET nome=%s, data_evento=%s, horario=%s, local=%s, descricao=%s, vagas=%s 
    WHERE id_evento=%s
    """
    run_action(query, (nome, data, horario, local, descricao, vagas, id_evento))

def update_evento_status(id_evento, novo_status):
    run_action("UPDATE eventos SET status = %s WHERE id_evento = %s", (novo_status, id_evento))

def delete_evento(id_evento):
    # Remove inscrições associadas primeiro
    run_action("DELETE FROM inscricoes WHERE id_evento = %s", (id_evento,))
    # Remove o evento
    run_action("DELETE FROM eventos WHERE id_evento = %s", (id_evento,))

# --- INSCRICOES ---
def get_inscricoes_detalhadas(filtro_evento=None):
    # join com tabelas corretas
    query = """
    SELECT 
        i.id_inscricao,
        b.nome AS beneficiario,
        b.telefone,
        e.nome AS evento,
        e.data_evento,
        i.status,
        i.data_inscricao
    FROM inscricoes i
    JOIN beneficiarios b ON i.id_beneficiario = b.id_beneficiario
    JOIN eventos e ON i.id_evento = e.id_evento
    WHERE 1=1
    """
    params = []
    if filtro_evento:
        query += " AND e.nome = %s"
        params.append(filtro_evento)
        
    query += " ORDER BY i.data_inscricao DESC"
    return run_query(query, tuple(params))

def confirm_inscricao_simples(id_beneficiario, id_evento, status="Confirmada"):
    query = """
    INSERT INTO inscricoes (id_beneficiario, id_evento, status)
    VALUES (%s, %s, %s)
    ON CONFLICT (id_beneficiario, id_evento) DO UPDATE SET status = EXCLUDED.status
    """
    run_action(query, (id_beneficiario, id_evento, status))

def confirmar_inscricao(id_beneficiario, id_evento):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Check vagas (only active confirmed subscriptions count)
        cur.execute("SELECT COUNT(*) FROM inscricoes WHERE id_evento = %s AND status = 'Confirmada'", (id_evento,))
        count = cur.fetchone()[0]
        
        # Get Evento Info for Denormalization
        cur.execute("SELECT nome, data_evento, local, vagas FROM eventos WHERE id_evento = %s", (id_evento,))
        row_evt = cur.fetchone()
        if not row_evt: return False, "Evento não encontrado!"
        nome_evt, data_evt, local_evt, vagas = row_evt
        
        # Get Beneficiario Info for Denormalization
        cur.execute("SELECT nome, email, telefone FROM beneficiarios WHERE id_beneficiario = %s", (id_beneficiario,))
        row_ben = cur.fetchone()
        if not row_ben: return False, "Beneficiário não encontrado!"
        nome_ben, email_ben, tel_ben = row_ben
        
        if count >= vagas:
            return False, "Evento Esgotado! (Sem vagas disponíveis)"
            
        # Upsert with Denormalization
        cur.execute("""
            INSERT INTO inscricoes (
                id_beneficiario, id_evento, status,
                beneficiario_nome, beneficiario_email, beneficiario_telefone,
                evento_nome, evento_data, evento_local
            )
            VALUES (%s, %s, 'Confirmada', %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id_beneficiario, id_evento) 
            DO UPDATE SET status = 'Confirmada', data_inscricao = CURRENT_TIMESTAMP
        """, (
            id_beneficiario, id_evento, 
            nome_ben, email_ben, tel_ben,
            nome_evt, data_evt, local_evt
        ))
        
        conn.commit()
        return True, "Inscrição realizada com sucesso!"
    except Exception as e:
        return False, str(e)
    finally:
        cur.close()
        conn.close()

def update_inscricao_status(id_inscricao, novo_status):
    query = "UPDATE inscricoes SET status = %s WHERE id_inscricao = %s"
    run_action(query, (novo_status, id_inscricao))

# --- DASHBOARD ---
def get_dashboard_stats():
    conn = get_connection()
    cur = conn.cursor()
    stats = {}
    
    cur.execute("SELECT COUNT(*) FROM beneficiarios")
    stats['total_beneficiarios'] = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM eventos WHERE data_evento >= CURRENT_DATE")
    stats['eventos_ativos'] = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM inscricoes WHERE status = 'Confirmada'")
    stats['total_inscricoes'] = cur.fetchone()[0]
    
    # Taxa de presença (simulada baseada em status 'Presente')
    cur.execute("SELECT COUNT(*) FROM inscricoes WHERE status = 'Presente'")
    presentes = cur.fetchone()[0]
    stats['presencas'] = presentes
    
    cur.close()
    conn.close()
    return stats

def get_eventos_por_regiao():
    query = """
    SELECT b.regiao, COUNT(*) as count 
    FROM beneficiarios b
    JOIN inscricoes i ON b.id_beneficiario = i.id_beneficiario
    GROUP BY b.regiao
    ORDER BY count DESC
    """
    return run_query(query)
