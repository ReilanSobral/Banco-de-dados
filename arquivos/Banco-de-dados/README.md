# 💚 Sistema de Gestão - ONG Vida Plena

![Project Status](https://img.shields.io/badge/status-concluído-brightgreen) ![Python](https://img.shields.io/badge/python-3.12-blue)

Uma aplicação visual e moderna para gestão de beneficiários e eventos sociais, com automação integrada de WhatsApp.

## 📋 Funcionalidades
*   **Dashboards Interativos:** Visualização gráfica de inscritos e ocupação.
*   **Gestão de Beneficiários:** CRUD completo com busca e filtros.
*   **Controle de Eventos:** Agenda, status de vagas e listas de presença.
*   **🤖 Automação WhatsApp:** Envio de lembretes automáticos para inscritos via Selenium/Web Scraping.

## 🛠️ Tecnologias
*   **Frontend:** Streamlit
*   **Backend/Banco:** PostgreSQL (Render Cloud)
*   **Automação:** Selenium WebDriver
*   **Linguagem:** Python

## 🚀 Como Rodar o Projeto

1.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure o Banco de Dados:**
    *   Certifique-se de ter o arquivo `.env` na pasta raiz com as credenciais do PostgreSQL.

3.  **Execute a Aplicação:**
    ```bash
    streamlit run app_ong.py
    ```

4.  **Acesse:**
    *   O navegador abrirá automaticamente em `http://localhost:8501`.

## 📸 Evidências de Integração
*   O sistema conecta-se ao banco PostgreSQL para persistência de dados.
*   O módulo `whatsapp_engine.py` integra-se ao Chrome local para automação.

---
**Curso:** Banco de Dados Visuais e Ferramentas Integradas
