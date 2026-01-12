

import streamlit as st
import pandas as pd
import plotly.express as px # RESTAURADO
import altair as alt # RESTAURADO POR PRECAUÇÃO
import psycopg2
import time
from datetime import datetime, time as dt_time
import os
from dotenv import load_dotenv
import base64
from db_functions import (
    get_beneficiarios, add_beneficiario, update_beneficiario, delete_beneficiario,
    get_eventos, add_evento, update_evento, delete_evento,
    get_inscricoes_detalhadas, get_dashboard_stats, update_inscricao_status,
    get_eventos_por_regiao, confirmar_inscricao, check_beneficiario_exists
)

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="ONG Vida Plena | Sistema de Gestão",
    page_icon="💚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS CUSTOMIZADO (MODERNO - TEMA EMERALD) ---
st.markdown("""
<style>
    /* Esconder botão DEPLOY e Menu */
    .stDeployButton {display:none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Fundo Global */
    .stApp {
        background-color: #f8fafc; /* Slate-50 */
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Cards de Estatísticas */
    .metric-card {
        background-color: white;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        color: #1e293b;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2.25rem;
        font-weight: 700;
        margin-top: 8px;
    }
    .metric-label {
        color: #64748b;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    /* Card de Usuário (Novo Layout) */
    .user-card {
        background-color: white;
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #e2e8f0;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: all 0.2s;
    }
    .user-card:hover {
        border-color: #10b981;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .avatar-circle {
        width: 48px;
        height: 48px;
        background-color: #dcfce7;
        color: #166534;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1.1rem;
        margin-right: 16px;
    }
    
    /* Botões */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        border: none;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
    }
    
    /* Cores de Utilitário */
    .bg-green-500 {background-color: #10b981;}
    .bg-yellow-500 {background-color: #f59e0b;}
    .bg-red-500 {background-color: #ef4444;}
    
    /* Botão Primário */
    button[kind="primary"] {
        background-color: #059669; 
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("💚 Vida Plena")
    st.caption("Sistema de Gestão Social")
    st.markdown("---")
    
    # Lógica de Navegação Forçada (Redirecionamento)
    nav_options = ["📊 Dashboard", "👥 Beneficiários", "📅 Eventos", "📝 Inscrições", "⚙️ Configurações"]
    default_index = 0
    
    if 'force_nav_to' in st.session_state:
        target = st.session_state['force_nav_to']
        if target in nav_options:
            default_index = nav_options.index(target)
        del st.session_state['force_nav_to'] # Limpa para não travar
    
    selected_page = st.radio(
        "Navegação", 
        nav_options,
        index=default_index
    )
    
    st.markdown("---")
    st.info(f"📅 Data: {datetime.now().strftime('%d/%m/%Y')}")
    st.caption("Conectado ao PostgreSQL (Render)")

# --- PAGINA: CONFIGURACOES (NOVA) ---
# --- PAGINA: CONFIGURACOES (NOVA) ---
# --- PAGINA: CONFIGURACOES (COM MOTOR SELENIUM) ---
if selected_page == "⚙️ Configurações":
    st.title("⚙️ Painel de Configurações")
    
    import whatsapp_engine as wa
    
    st.info("ℹ️ O sistema executa o WhatsApp em segundo plano (modo oculto). Use o painel abaixo para monitorar.")

    # --- BLOCO 1: CONEXÃO COM QR CODE NA TELA ---
    with st.container():
        st.subheader("1. Conexão WhatsApp Integrada")
        
        c_qr, c_status = st.columns([1, 2])
        
        # Verificar Status
        status_msg = st.empty()
        qr_place = c_qr.empty()
        
        # Botões de Controle
        with c_status:
            st.markdown("### Controle do Robô")
            
            if st.button("🔄 Iniciar / Verificar Conexão"):
                with st.spinner("Iniciando motor gráfico..."):
                    status, data = wa.get_qr_code_status()
                    
                    if status == 'connected':
                        st.success("✅ **WhatsApp CONECTADO!**")
                        st.session_state['wa_status'] = True
                        qr_place.markdown("""
                        <div style="text-align:center; padding:30px; background:#dcfce7; border-radius:10px;">
                            <h1>📲</h1>
                            <p>Sincronizado</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    elif status == 'qr':
                        st.session_state['wa_status'] = False
                        # Mostrar QR Code decodificado
                        qr_place.image(base64.b64decode(data), caption="Escaneie este QR Code com seu celular", width=250)
                        st.info("Aguardando leitura do QR Code... Clique no botão novamente após escanear.")
                        
                    elif status == 'loading':
                        st.warning("⏳ Carregando WhatsApp Web... Tente novamente em 5 segundos.")
                    
                    elif status == 'error':
                        st.error(f"Erro no driver: {data}")

            if st.button("🛑 Desligar Motor"):
                wa.close_driver()
                st.session_state['wa_status'] = False
                st.success("Motor desligado.")

    st.divider()

    # --- BLOCO 2: REGRAS DE DISPARO ---
    st.subheader("2. Regras de Disparo Automático")
    st.markdown("Defina abaixo quando o robô deve enviar as mensagens.")
    
    c_day, c_time = st.columns(2)
    with c_day:
        dias_antes = st.number_input("Enviar mensagem faltando quantos dias?", min_value=1, max_value=30, value=2)
    with c_time:
        hora_envio = st.time_input("Horário de verificação diária:", value=dt_time(9, 0))
    
    # Preview
    msg_preview = f"Olá [Nome], faltam *{dias_antes} dias* para o evento [Evento]! Contamos com você."
    st.markdown(f"**Prévia da Mensagem:**")
    st.code(msg_preview, language="markdown")
    
    st.divider()
    
    # --- BLOCO 3: EXECUÇÃO EM MASSA VIA ENGINE ---
    st.subheader("3. Disparo em Massa")
    
    if st.button("🚀 INICIAR DISPAROS (Motor Selenium)", type="primary"):
        # Verificação proativa de conexão antes de iniciar
        with st.spinner("Verificando conexão com WhatsApp..."):
            status_now, _ = wa.get_qr_code_status()
            if status_now == 'connected':
                st.session_state['wa_status'] = True
            
        if not st.session_state.get('wa_status', False):
            st.error("❌ O WhatsApp não parece conectado. Certifique-se de ter escaneado o QR Code e clique em 'Verificar Conexão' novamente se necessário.")
        else:
            bar = st.progress(0)
            txt = st.empty()
            
            df_ins = get_inscricoes_detalhadas().head(3) # Limitado para demo
            total = len(df_ins)
            
            for i, row in df_ins.iterrows():
                nome = row['beneficiario'].split()[0]
                tel = str(row['telefone'])
                msg = f"Olá {nome}, faltam {dias_antes} dias para o evento {row['evento']}!"
                
                txt.text(f"Enviando para {nome}...")
                success, resp = wa.send_message_selenium(tel, msg)
                
                if success:
                    st.toast(f"✅ Enviado: {nome}")
                else:
                    st.toast(f"❌ Erro {nome}: {resp}")
                    
                bar.progress(int(((i+1)/total)*100))
                
            st.success("Ciclo finalizado!")

# --- PAGINA: DASHBOARD ---
elif selected_page == "📊 Dashboard":
    st.title("📊 Painel Dashboard")
    st.caption("Visão geral de impacto e atividades da ONG.")
    
    st.markdown("<br>", unsafe_allow_html=True) # Spacer
    
    try:
        stats = get_dashboard_stats()
        
        # --- CARDS DE MÉTRICAS (KPIs) ---
        c1, c2, c3, c4 = st.columns(4)
        
        def kpi_card(value, label, icon, color):
            return f"""
            <div class="metric-card" style="border-left: 4px solid {color}; text-align:center;">
                <div style="font-size: 2rem; margin-bottom: 5px;">{icon}</div>
                <div class="metric-value" style="color: {color}; margin:0;">{value}</div>
                <div class="metric-label" style="font-size:0.8rem; margin-top:5px;">{label}</div>
            </div>
            """
            
        with c1:
            st.markdown(kpi_card(stats.get('total_beneficiarios', 0), "Beneficiários", "👥", "#10b981"), unsafe_allow_html=True)
            
        with c2:
            st.markdown(kpi_card(stats.get('eventos_ativos', 0), "Eventos Ativos", "📅", "#3b82f6"), unsafe_allow_html=True)
            
        with c3:
            st.markdown(kpi_card(stats.get('total_inscricoes', 0), "Inscrições", "📝", "#8b5cf6"), unsafe_allow_html=True)
            
        with c4:
            total_insc = stats.get('total_inscricoes', 1)
            presencas = stats.get('presencas', 0)
            taxa = int((presencas / total_insc) * 100) if total_insc > 0 else 0
            st.markdown(kpi_card(f"{taxa}%", "Taxa de Presença", "📈", "#f59e0b"), unsafe_allow_html=True)
            
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # --- GRÁFICOS E LISTAS ---
        g1, g2 = st.columns([1.5, 1])
        
        # Gráfico 1: Barras ou Pizza por Região/Cidade
        with g1:
            st.subheader("📍 Distribuição Geográfica")
            df_regiao = get_eventos_por_regiao()
            
            if not df_regiao.empty:
                # Gráfico de Rosca (Donut) é mais bonito para distribuição
                fig = px.pie(
                    df_regiao, 
                    names='regiao', 
                    values='count', 
                    hole=0.6,
                    color_discrete_sequence=px.colors.sequential.Teal
                )
                fig.update_layout(
                    showlegend=True,
                    legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="right", x=1.2),
                    margin=dict(t=0, b=0, l=0, r=0),
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("Cadastre beneficiários e cidades para ver a distribuição geográfica.")
                
        # Lista de Próximos Eventos (Design Clean)
        with g2:
            st.subheader("🚀 Próximos Eventos")
            df_eventos = get_eventos()
            
            if not df_eventos.empty:
                # Filtrar apenas futuros (simulado por slice para demo)
                df_futuros = df_eventos.tail(4) # Exemplo: apenas os 4 ultimos (futuros se ordenado por data)
                
                for i, row in df_futuros.iterrows():
                    st.markdown(f"""
                    <div style="background: white; padding: 12px; border-radius: 8px; border: 1px solid #f1f5f9; margin-bottom: 8px; display: flex; align-items: center;">
                        <div style="background: #ecfdf5; color: #059669; padding: 8px 12px; border-radius: 6px; font-weight: bold; text-align: center; margin-right: 12px; min-width: 60px;">
                            <div style="font-size:0.7rem;">DEZ</div>
                            <div style="font-size:1.1rem;">{str(row['data_evento']).split('-')[-1] if '-' in str(row['data_evento']) else 'DIA'}</div>
                        </div>
                        <div>
                            <div style="font-weight: 600; color: #334155; font-size: 0.95rem;">{row['nome']}</div>
                            <div style="font-size: 0.8rem; color: #64748b;">📍 {row['local']} • {row['vagas']} vagas</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                if st.button("Ver Agenda Completa", use_container_width=True):
                    st.session_state['force_nav_to'] = "📅 Eventos"
                    st.rerun()
            else:
                 st.info("Nenhum evento agendado.")
                
    except Exception as e:
        st.error(f"Erro ao carregar dashboard: {e}")

# --- PAGINA: BENEFICIARIOS ---
elif selected_page == "👥 Beneficiários":
    st.title("👥 Painel de Beneficiários")
    
    col_tools, col_add = st.columns([3, 1])
    
    with col_tools:
        # Filtros Avançados
        with st.expander("🔍 Filtros de Busca", expanded=True):
            c_ft1, c_ft2 = st.columns(2)
            search_term = c_ft1.text_input("Buscar por Nome ou Email", placeholder="Ex: Maria...")
            # CIDADES (Mudança de Zonas para Cidades conforme pedido)
            cidades_fixas = ["Todas", "São Paulo", "Osasco", "Guarulhos", "Barueri", "Campinas", "Outra"]
            city_filter = c_ft2.selectbox("Cidade", cidades_fixas)
    
    with col_add:
        st.markdown("<br>", unsafe_allow_html=True) 
        # Botão que ativa o form de cadastro
        if st.button("➕ Novo Cadastro", type="primary", use_container_width=True):
             st.session_state['show_add_modal'] = True

    # --- NOVO CADASTRO (Expander) ---
    if st.session_state.get('show_add_modal'):
        with st.container():
            st.markdown("### ✨ Novo Beneficiário")
            with st.form("new_ben_form"):
                c1, c2 = st.columns(2)
                novo_nome = c1.text_input("Nome Completo*")
                nova_idade = c2.number_input("Idade", min_value=0, max_value=120)
                novo_tel = c1.text_input("Telefone/WhatsApp*", placeholder="(11) 99999-9999")
                novo_email = c2.text_input("Email")
                
                # Lógica de Cidade Personalizada
                # Usamos um selectbox com opção 'Outra (Digitar...)'
                lista_cidades = ["São Paulo", "Osasco", "Guarulhos", "Barueri", "Campinas", "Carapicuíba", "Outra (Digitar...)"]
                sel_cidade = st.selectbox("Cidade", lista_cidades)
                custom_cidade = None
                if sel_cidade == "Outra (Digitar...)":
                    custom_cidade = st.text_input("Digite o nome da cidade:")
                
                c_submit, c_cancel = st.columns([1, 4])
                
                if c_submit.form_submit_button("Salvar"):
                    # Determinar cidade final
                    cidade_final = custom_cidade if sel_cidade == "Outra (Digitar...)" and custom_cidade else sel_cidade
                    if cidade_final == "Outra (Digitar...)": cidade_final = None # Evitar salvar o placeholder se não digitou nada
                    
                    if novo_nome and novo_tel and cidade_final:
                        # 1. Checar Duplicidade
                        if check_beneficiario_exists(novo_nome, novo_tel, novo_email):
                            st.error(f"⚠️ Atenção: Já existe um beneficiário cadastrado como '{novo_nome}' com este telefone ou email.")
                        else:
                            # 2. Salvar
                            add_beneficiario(novo_nome, int(nova_idade), novo_tel, novo_email, cidade_final)
                            st.success(f"Cadastro de {novo_nome} realizado com sucesso!")
                            st.session_state['show_add_modal'] = False
                            st.rerun()
                    else:
                        st.warning("Preencha Nome, Telefone e Cidade corretamente.")
                
            if st.button("Cancelar Cadastro"):
                st.session_state['show_add_modal'] = False
                st.rerun()
            st.divider()

    # --- LISTAGEM (CARDS) ---
    df_users = get_beneficiarios(filtro_nome=search_term, filtro_regiao=city_filter)
    
    if not df_users.empty:
        st.markdown(f"**{len(df_users)} beneficiários encontrados**")
        
        for index, row in df_users.iterrows():
            # Container do Card
            with st.container():
                cols = st.columns([0.5, 3, 1])
                
                # 1. Avatar
                with cols[0]:
                    iniciais = "".join([n[0] for n in row['nome'].split()[:2]]).upper() if row['nome'] else "?"
                    st.markdown(f"""
                        <div class="avatar-circle">{iniciais}</div>
                    """, unsafe_allow_html=True)
                
                # 2. Dados Principais
                with cols[1]:
                    st.markdown(f"<h4 style='margin:0; padding:0;'>{row['nome']}</h4>", unsafe_allow_html=True)
                    st.caption(f"📍 {row['regiao']}  •  📞 {row.get('telefone', '-')}")
                
                # 3. Ações
                with cols[2]:
                    if st.button("✏️", key=f"btn_edit_{row['id_beneficiario']}", help="Editar"):
                        # Toggle Edit State
                        state_key = f"edit_mode_{row['id_beneficiario']}"
                        st.session_state[state_key] = not st.session_state.get(state_key, False)
                    
                    if st.button("🗑️", key=f"btn_del_{row['id_beneficiario']}", help="Excluir"):
                         # Toggle Delete Confirm
                         del_key = f"del_mode_{row['id_beneficiario']}"
                         st.session_state[del_key] = True

            # --- MODO EDIÇÃO (Expander condicional) ---
            if st.session_state.get(f"edit_mode_{row['id_beneficiario']}", False):
                with st.form(f"edit_form_{row['id_beneficiario']}"):
                    st.write(f"✏️ Editando: {row['nome']}")
                    ec1, ec2 = st.columns(2)
                    e_nome = ec1.text_input("Nome", value=row['nome'])
                    e_idade = ec2.number_input("Idade", value=row['idade'] or 0)
                    e_tel = ec1.text_input("Telefone", value=row.get('telefone', ''))
                    e_email = ec2.text_input("Email", value=row['email'] or '')
                    # Pegar cidade atual
                    e_cidade = st.text_input("Cidade", value=row['regiao'])
                    
                    c_save, c_del = st.columns([1, 1])
                    if c_save.form_submit_button("💾 Salvar Alterações"):
                        update_beneficiario(row['id_beneficiario'], e_nome, e_idade, e_tel, e_email, e_cidade)
                        st.success("Atualizado!")
                        st.session_state[f"edit_mode_{row['id_beneficiario']}"] = False
                        st.rerun()

            # --- CONFIRMAÇÃO DE EXCLUSÃO ---
            if st.session_state.get(f"del_mode_{row['id_beneficiario']}", False):
                st.warning(f"Tem certeza que deseja excluir {row['nome']}?")
                col_yes, col_no = st.columns(2)
                if col_yes.button("Sim, Excluir", key=f"yes_del_{row['id_beneficiario']}"):
                    delete_beneficiario(row['id_beneficiario'])
                    st.success(f"{row['nome']} excluído.")
                    st.session_state[f"del_mode_{row['id_beneficiario']}"] = False
                    st.rerun()
                
                if col_no.button("Cancelar", key=f"no_del_{row['id_beneficiario']}"):
                    st.session_state[f"del_mode_{row['id_beneficiario']}"] = False
                    st.rerun()
                    
            st.markdown("<hr style='margin: 8px 0; opacity: 0.1;'>", unsafe_allow_html=True)

    else:
        st.warning("Nenhum beneficiário encontrado com esses filtros.")

# --- PAGINA: EVENTOS ---
elif selected_page == "📅 Eventos":
    st.title("📅 Painel de Eventos")
    
    tab_cal, tab_lista, tab_novo = st.tabs(["📅 Calendário", "📋 Lista Detalhada", "➕ Novo Evento"])
    
    with tab_cal:
        st.info("Visualização em grade dos próximos eventos.")
        df_evts = get_eventos()
        if not df_evts.empty:
            cols = st.columns(3)
            for i, row in df_evts.iterrows():
                # Card de Evento
                with cols[i % 3]:
                    # Status vem do banco agora ('Agendado', etc)
                    st_val = row['status']
                    status_color = "🟢" if st_val == "Agendado" else "🔴" if st_val == "Concluído" else "🟡"
                    
                    inscritos = row.get('inscritos', 0)
                    vagas = row['vagas']
                    ocupacao = min(100, int((inscritos / vagas) * 100)) if vagas > 0 else 0
                    
                    # Cor da barra
                    bar_class = "bg-green-500"
                    if ocupacao >= 90: bar_class = "bg-red-500"
                    elif ocupacao >= 60: bar_class = "bg-yellow-500"

                    desc_short = row.get('descricao', '') or ''
                    if len(desc_short) > 90: desc_short = desc_short[:87] + "..."

                    st.markdown(f"""
<div class="metric-card" style="padding: 15px; margin-bottom: 10px;">
<div style="display:flex; justify-content:space-between;">
<h4 style="margin:0;">{row['nome']}</h4>
<span style="font-size:0.8rem; background:#f1f5f9; padding:2px 6px; border-radius:4px;">{st_val}</span>
</div>
<small style="color:#64748b;">{row['data_evento']} | {row['horario']}</small>
<p style="margin-top:5px; margin-bottom:5px; font-size:0.9rem;">📍 {row['local']}</p>
<p style="font-size:0.85rem; color:#475569; margin-bottom:10px; line-height:1.4;">{desc_short}</p>
<div style="margin-top:10px;">
<div style="display:flex; justify-content:space-between; font-size:0.75rem; margin-bottom:2px;">
<span><b>{inscritos}/{vagas}</b> ocupados</span>
<span>{ocupacao}%</span>
</div>
<div style="width:100%; background:#e2e8f0; height:6px; border-radius:3px;">
<div style="width:{ocupacao}%; height:100%; border-radius:3px; transition:width 0.5s;" class="{bar_class}"></div>
</div>
</div>
</div>
""", unsafe_allow_html=True)
                    
                    if st_val == "Agendado":
                         if st.button("Inscrever Alguém", key=f"ins_{row['id_evento']}"):
                             st.toast("Vá para a aba 'Inscrições'!", icon="ℹ️")
        else:
            st.info("Agenda vazia.")
            
    with tab_lista:
        df_evts = get_eventos()
        if not df_evts.empty:
            st.markdown(f"**{len(df_evts)} eventos cadastrados**")
            
            for i, row in df_evts.iterrows():
                with st.container():
                    # Layout: Status Icon | Nome/Data | Status Select | Excluir
                    c_icon, c_info, c_status, c_del = st.columns([0.5, 3, 2, 0.5])
                    
                    # Definir cor e ícone baseados no status
                    status_colors = {
                        "Agendado": "#10b981", # Verde
                        "Em Andamento": "#3b82f6", # Azul
                        "Concluído": "#64748b", # Cinza
                        "Cancelado": "#ef4444"  # Vermelho
                    }
                    st_cor = status_colors.get(row['status'], "#64748b")
                    
                    with c_icon:
                        st.markdown(f"""
                        <div style="height: 40px; width: 8px; background-color: {st_cor}; border-radius: 4px;"></div>
                        """, unsafe_allow_html=True)
                        
                    with c_info:
                        st.markdown(f"**{row['nome']}**")
                        st.caption(f"📅 {row['data_evento']} • {row['horario']} • 📍 {row['local']}")
                        
                    with c_status:
                        # Selectbox para mudar status rápido
                        novo_st = st.selectbox(
                            "Status", 
                            ["Agendado", "Em Andamento", "Concluído", "Cancelado"],
                            index=["Agendado", "Em Andamento", "Concluído", "Cancelado"].index(row['status']) if row['status'] in ["Agendado", "Em Andamento", "Concluído", "Cancelado"] else 0,
                            key=f"st_sel_{row['id_evento']}",
                            label_visibility="collapsed"
                        )
                        if novo_st != row['status']:
                            update_evento_status(row['id_evento'], novo_st)
                            st.toast(f"Status atualizado para {novo_st}!")
                            # st.rerun() # Opcional: rerun imediato ou deixa pro usuario dar F5 se quiser ver cor mudar
                            
                    with c_del:
                        if st.button("✏️", key=f"edit_evt_{row['id_evento']}", help="Editar Evento"):
                             st_key = f"mode_edit_evt_{row['id_evento']}"
                             st.session_state[st_key] = not st.session_state.get(st_key, False)
                             
                        if st.button("🗑️", key=f"del_evt_{row['id_evento']}", help="Excluir Evento"):
                            st.session_state[f"confirm_del_evt_{row['id_evento']}"] = True
                
                # --- MODO EDIÇÃO EVENTO ---
                if st.session_state.get(f"mode_edit_evt_{row['id_evento']}", False):
                    with st.form(f"form_edit_evt_{row['id_evento']}"):
                        st.markdown(f"**Editando: {row['nome']}**")
                        enome = st.text_input("Nome", value=row['nome'])
                        c1, c2 = st.columns(2)
                        edata = c1.date_input("Data", value=row['data_evento'] if row['data_evento'] else datetime.today())
                        ehorario = c2.time_input("Horário", value=datetime.strptime(str(row['horario']), '%H:%M:%S').time() if row['horario'] else time(9,0))
                        
                        elocal = st.text_input("Local", value=row['local'])
                        evagas = st.number_input("Vagas", value=int(row['vagas']), min_value=1)
                        edesc = st.text_area("Descrição", value=row['descricao'] if row['descricao'] else "")
                        
                        if st.form_submit_button("💾 Salvar Alterações"):
                            update_evento(row['id_evento'], enome, edata, ehorario, elocal, edesc, evagas)
                            st.success("Evento atualizado!")
                            st.session_state[f"mode_edit_evt_{row['id_evento']}"] = False
                            st.rerun()

                # Confirmação de Exclusão
                if st.session_state.get(f"confirm_del_evt_{row['id_evento']}", False):
                    st.warning(f"Excluir evento '{row['nome']}' e todas suas inscrições?")
                    co1, co2 = st.columns(2)
                    if co1.button("Sim, Excluir", key=f"yes_evt_{row['id_evento']}"):
                        delete_evento(row['id_evento'])
                        st.success("Evento excluído!")
                        st.session_state[f"confirm_del_evt_{row['id_evento']}"] = False
                        st.rerun()
                    if co2.button("Cancelar", key=f"no_evt_{row['id_evento']}"):
                        st.session_state[f"confirm_del_evt_{row['id_evento']}"] = False
                        st.rerun()
                        
                st.markdown("<hr style='margin: 8px 0; opacity: 0.1;'>", unsafe_allow_html=True)
            
        else:
            st.info("Nenhum evento cadastrado.")
            
    with tab_novo:
        with st.form("form_evento"):
            st.subheader("Criar Novo Evento")
            nome = st.text_input("Nome do Evento")
            c1, c2 = st.columns(2)
            data = c1.date_input("Data", min_value=datetime.today())
            horario = c2.time_input("Horário", value=dt_time(9, 0))
            local = st.text_input("Local")
            vagas = st.number_input("Número de Vagas", min_value=1, value=30)
            desc = st.text_area("Descrição")
            
            if st.form_submit_button("Agendar Evento"):
                if nome and data and local and vagas:
                    try:
                        add_evento(nome, data, horario, local, desc, int(vagas), status="Agendado")
                        st.success("Evento criado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar evento: {e}")
                else:
                    st.warning("Preencha os campos obrigatórios (Nome, Data, Local, Vagas).")

# --- PAGINA: INSCRICOES ---
elif selected_page == "📝 Inscrições":
    st.title("📝 Painel de Inscrições")
    st.caption("Registre um beneficiário em um evento.")
    
    # --- SOLUÇÃO DEFINITIVA PARA LARGURA: LAYOUT VERTICAL ---
    # 1. Formulário em Expander para não ocupar espaço lateral
    with st.expander("➕ Registrar no Evento (Clique para abrir)", expanded=True):
        c_form1, c_form2, c_btn = st.columns([2, 2, 1])
        
        # Dropdowns
        df_ben = get_beneficiarios()
        df_evt = get_eventos()
        
        if not df_ben.empty and not df_evt.empty:
            map_ben = {f"{row['nome']} (ID: {row['id_beneficiario']})": row['id_beneficiario'] for i, row in df_ben.iterrows()}
            df_evt_futuros = df_evt[df_evt['status'].isin(['Agendado', 'Em Andamento'])] if 'status' in df_evt.columns else df_evt
            map_evt = {f"{row['nome']} | {row['data_evento']}": row['id_evento'] for i, row in df_evt_futuros.iterrows()}
            
            if map_evt:
                with c_form1:
                    sel_ben = st.selectbox("Beneficiário", list(map_ben.keys()))
                with c_form2:
                    sel_evt = st.selectbox("Evento", list(map_evt.keys()))
                with c_btn:
                    st.write("") # Spacer
                    st.write("")
                    confirm = st.button("✅ Confirmar", type="primary", use_container_width=True)
                
                if confirm:
                    id_b = map_ben[sel_ben]
                    id_e = map_evt[sel_evt]
                    success, msg = confirmar_inscricao(id_b, id_e)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            else:
                st.warning("Sem eventos.")
        else:
            st.warning("Cadastre dados.")

    # 2. Tabela ocupando 100% da largura da tela e com textos truncados
    st.markdown("### Histórico")
    
    filtro_evt_nome = st.selectbox("Filtrar por Evento", ["Todos"] + list(df_evt['nome'].unique()) if not df_evt.empty else [])
    df_insc = get_inscricoes_detalhadas(filtro_evento=filtro_evt_nome if filtro_evt_nome != "Todos" else None)
    
    if not df_insc.empty:
        # TRUNCAMENTO DE TEXTO PARA CABER (Solução agressiva para scrollbar)
        df_insc['beneficiario'] = df_insc['beneficiario'].apply(lambda x: x[:25] + '...' if len(x) > 25 else x)
        df_insc['evento'] = df_insc['evento'].apply(lambda x: x[:25] + '...' if len(x) > 25 else x)
        
        edited_df = st.data_editor(
            df_insc,
            column_config={
                "id_inscricao": None, # ESCONDIDO TOTALMENTE
                "beneficiario": st.column_config.TextColumn("Nome", disabled=True, width="medium"),
                "telefone": st.column_config.TextColumn("Tel", disabled=True, width="small"), 
                "evento": st.column_config.TextColumn("Evento", disabled=True, width="medium"),
                "data_evento": st.column_config.DateColumn("Data", disabled=True, width="small", format="DD/MM"), 
                "status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Confirmada", "Pendente", "Cancelada", "Presente", "Ausente"],
                    required=True,
                    width="small"
                ),
                "data_inscricao": st.column_config.DatetimeColumn("Cadastro", format="DD/MM", disabled=True, width="small")
            },
            hide_index=True,
            use_container_width=True,
            key="editor_inscricoes"
        )
            
        # Detectar mudanças e salvar
        if edited_df is not None:
            # Compara o DataFrame editado com o original para achar mudanças
            changes = []
            for index, row in edited_df.iterrows():
                original_row = df_insc.iloc[index]
                if row['status'] != original_row['status']:
                    changes.append((row['id_inscricao'], row['status']))
            
            if changes:
                if st.button(f"💾 Salvar {len(changes)} alterações de status", type="primary"):
                    for id_ins, novo_st in changes:
                        update_inscricao_status(id_ins, novo_st)
                    st.success("Status atualizados com sucesso!")
                    st.rerun()

        # --- ENVIO INDIVIDUAL VIA ROBÔ (Conectado na Config) ---
        st.divider()
        st.subheader("🤖 Envio Rápido via Robô")
        st.caption("Use esta opção para enviar mensagens automáticas sem abrir novas abas manualmente.")
        
        c_sel, c_btn = st.columns([3, 1])
        with c_sel:
            # Montar lista de opções: "Nome (Evento)" 
            opts = df_insc.apply(lambda x: f"{x['id_inscricao']} - {x['beneficiario']} ({x['evento']})", axis=1).tolist()
            selection = st.selectbox("Selecione o Inscrito para notificar:", opts)
        
        with c_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Enviar Msg Agora 📤"):
                # Tentativa de Auto-Recuperação do Status
                if not st.session_state.get('wa_status', False):
                    try:
                        import whatsapp_engine as wa
                        # Verifica se o driver existe e está vivo
                        if wa.init_driver() is not None:
                            # Checagem rápida (sem forçar nova janela se já existir)
                            st.session_state['wa_status'] = True
                    except:
                        pass

                if not st.session_state.get('wa_status', False):
                    st.error("Erro: Robô desconectado! Vá em Configurações > Confirmar Conexão.")
                    st.info("Dica: Se o navegador já estiver aberto, vá em Configurações e clique em 'Iniciar/Verificar' para reconectar o sistema.")
                else:
                    # Extrair ID
                    sel_id = int(selection.split(' - ')[0])
                    row = df_insc[df_insc['id_inscricao'] == sel_id].iloc[0]
                    
                    nome = row['beneficiario'].split()[0]
                    tel_raw = "".join([c for c in str(row['telefone']) if c.isdigit()])
                    evento = row['evento']
                    
                    if len(tel_raw) >= 10:
                        if not tel_raw.startswith("55"): tel_raw = "55" + tel_raw
                        
                        import whatsapp_engine as wa
                        
                        st.toast(f"Enviando para {nome}...", icon="🤖")
                        msg = f"Olá {nome}, confirmamos sua inscrição no evento {evento}! Tudo certo."
                        
                        success, text_resp = wa.send_message_selenium(tel_raw, msg)
                        
                        if success:
                            st.success(f"✅ Mensagem enviada para {nome}!")
                        else:
                            st.error(f"❌ Falha: {text_resp}")
                            
                    else:
                        st.warning("Telefone inválido (curto demais).")

    else:
        st.info("Nenhuma inscrição encontrada.")
