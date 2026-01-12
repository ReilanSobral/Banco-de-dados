# Manual do Usuário - Sistema ONG Vida Plena

## 1. Acesso ao Sistema
O sistema é uma aplicação Desktop/Web que roda localmente no computador da ONG, conectada a um banco de dados na nuvem.

### Pré-requisitos
*   Conexão com Internet (para acessar o banco de dados).
*   Navegador Google Chrome instalado (para o Robô de WhatsApp).

### Como Iniciar
1.  Abra o terminal na pasta do projeto.
2.  Execute o comando:
    ```bash
    streamlit run app_ong.py
    ```
3.  O sistema abrirá automaticamente no seu navegador padrão (geralmente `http://localhost:8501`).

---

## 2. Navegação Principal

O menu lateral esquerdo dá acesso aos 4 módulos principais:

### 📊 Dashboard
Visão geral da ONG. Use esta tela para ver estatísticas rápidas, como número total de inscritos e próximos eventos.

### 👥 Beneficiários
Gerenciamento de pessoas.
*   **Novo Cadastro:** Clique no botão azul "➕ Novo Cadastro" no topo.
*   **Busca:** Use a barra de pesquisa para filtrar por nome ou cidade.
*   **Edição/Exclusão:** Use os botões (✏️ e 🗑️) nos cartões de cada pessoa.

### 📅 Eventos
Gerenciamento da agenda.
*   **Aba Calendário:** Visualização visual dos cards de eventos.
*   **Aba Lista:** Tabela para editar ou cancelar eventos rapidamente.
*   **Aba Novo Evento:** Formulário para criar novos eventos.
    *   *Nota:* O sistema impede inscrições se as vagas do evento estiverem esgotadas.

### 📝 Inscrições
Onde a mágica acontece.
1.  **Registrar:** Selecione um Beneficiário e um Evento nos menus e clique em "Confirmar".
2.  **Lista de Presença:** Na tabela abaixo, você pode marcar se a pessoa estava "Presente" ou "Ausente".
3.  **Robô de WhatsApp:** Selecione um inscrito na lista inferior e clique em "Enviar Msg Agora" para mandar um lembrete automático.

### ⚙️ Configurações (Robô)
Para usar o envio de WhatsApp:
1.  Acesse esta tela e clique em **"Iniciar / Verificar Conexão"**.
2.  Uma janela do Chrome abrirá. **Escaneie o QR Code** com seu celular.
3.  Volte ao sistema e clique novamente no botão para confirmar que está "Conectado".
4.  Agora você pode fazer disparos em massa ou individuais nas outras telas.

---

## 3. Suporte
Em caso de erros de conexão ("Network Error"), verifique sua internet. O banco de dados está hospedado na nuvem e requer conexão ativa.
