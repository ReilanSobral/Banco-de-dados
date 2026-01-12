# Relatório Técnico: Sistema de Gestão ONG Vida Plena

**Aluno:** [Alan Ribeiro de Menezes]
  
**Disciplina:** Banco de Dados Visuais e Ferramentas Integradas  
**Data:** 10/01/2026

---

## 1. Levantamento de Requisitos
O levantamento foi realizado através da análise do fluxo de trabalho manual da ONG. Identificou-se que o uso de planilhas descentralizadas e grupos de WhatsApp gerava inconsistência de dados e dificuldade na gestão.

**Metodologia Utilizada:**
*   **Análise Documental:** Verificação das planilhas de Excel antigas para entender os dados coletados.
*   **Observação de Processo:** Mapeamento de como os voluntários confirmavam presença (manual/verbal).

**Requisitos Definidos:**
*   Necessidade de um cadastro único (sem duplicidade).
*   Visualização clara da agenda de eventos e ocupação de vagas.
*   Automação da comunicação para reduzir trabalho manual.

## 2. Raciocínio da Modelagem Visual
A modelagem partiu da necessidade de transformar dados "frios" (linhas e colunas) em informação visual "quente" (Cards, Dashboards).
*   **De Planilhas para Relacional:** Migramos de uma visão "Flat" (Tabela única com tudo misturado) para um modelo Relacional (Entidades separadas que se conversam), garantindo integridade.
*   **Interface:** O design priorizou "Cards" para beneficiários e eventos, facilitando a leitura rápida em dispositivos móveis, em vez de grades de dados densas.

## 3. Justificativa da Ferramenta (Python/Streamlit)
Embora plataformas No-Code (como Glide) sejam úteis, optou-se por uma solução **Full-Code em Python** pelas seguintes razões:
1.  **Propriedade dos Dados:** O banco de dados (PostgreSQL) é 100% controlado pela ONG, sem dependência de plataformas proprietárias que podem cobrar por linha/usuário no futuro.
2.  **Integração Ilimitada:** O uso de Python permitiu integrar um **Robô de WhatsApp (Selenium)** personalizado, funcionalidade impossível ou muito cara em ferramentas No-Code padrão.
3.  **Escalabilidade:** O sistema pode crescer para milhares de registros sem custo adicional de licença.

## 4. Estrutura Relacional
O sistema baseia-se em três entidades principais:

*   **`Beneficiários`**: 
    *   *Atributos:* ID (PK), Nome, Idade, Telefone (Chave para WhatsApp), Região.
    *   *Relacionamento:* 1:N com Inscrições.
*   **`Eventos`**: 
    *   *Atributos:* ID (PK), Nome, Data, Vagas, Status.
    *   *Relacionamento:* 1:N com Inscrições.
*   **`Inscrições` (Tabela Associativa)**: 
    *   *Função:* Resolve o relacionamento N:N entre Pessoas e Eventos.
    *   *Atributos:* ID, FK_Beneficiario, FK_Evento, Status (Presente/Ausente), Data_Inscricao.

## 5. Ética e Segurança da Informação
O desenvolvimento seguiu princípios de "Privacy by Design":

*   **Minimização de Dados (LGPD):** Coletamos apenas os dados estritamente necessários para o contato e a operação (Nome e Telefone). Dados sensíveis (como endereço exato, renda, religião) foram excluídos do escopo inicial para reduzir riscos.
*   **Segurança no Código:** As credenciais do banco de dados não estão "chumbadas" no código, sendo carregadas via variáveis de ambiente (`.env`), prevenindo vazamentos caso o código seja compartilhado.
*   **Integridade:** O banco relacional impede a exclusão acidental de eventos que possuem inscrições ativas (Foreign Key Constraints), protegendo o histórico da ONG.

---
*Este documento resume as decisões técnicas e teóricas do projeto.*
