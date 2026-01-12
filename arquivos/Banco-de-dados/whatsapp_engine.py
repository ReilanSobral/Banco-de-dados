
import time
import os
import base64
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import streamlit as st

def init_driver():
    """Inicia o navegador Chrome controlado"""
    # Garantir que existe no session_state (mesmo após F5)
    if 'wa_driver' not in st.session_state:
        st.session_state.wa_driver = None

    if st.session_state.wa_driver is not None:
        try:
            # Testa se ainda está vivo
            st.session_state.wa_driver.title
            return st.session_state.wa_driver
        except:
            st.session_state.wa_driver = None

    options = Options()
    options.add_argument("--headless") # Executar em background (sem janela visivel)
    options.add_argument("--window-size=1920,1080") # Importante para garantir renderização no headless
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Argumentos Críticos para Estabilidade no Windows Headless
    options.add_argument("--disable-gpu") 
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--remote-debugging-port=9222") # Ajuda no erro DevToolsActivePort
    
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # Cache do diretório de usuário para manter login e evitar desconexão com o celular
    base_path = os.getcwd()
    options.add_argument(f"user-data-dir={base_path}/wa_session_cache") 

    # Tenta usar o gerenciador nativo do Selenium 4 (mais robusto)
    try:
        # Modo simples: Deixa o Selenium achar o driver sozinho
        driver = webdriver.Chrome(options=options)
    except Exception as e_native:
        # Fallback: Se o nativo falhar, tenta o webdriver_manager como última opção
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            
            # Tenta forçar a busca pela versão correta
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        except Exception as e_manager:
            raise Exception(f"Erro ao iniciar Chrome. Nativo: {e_native} | Manager: {e_manager}")

    driver.get("https://web.whatsapp.com")
    st.session_state.wa_driver = driver
    return driver

def get_qr_code_status():
    """
    Retorna:
    - ('connected', None): Se já estiver logado
    - ('qr', image_base64): Se tiver um QR code na tela
    - ('loading', None): Se estiver carregando
    - ('error', error_message): Se houver erro
    """
    try:
        driver = init_driver()
        
        # Aguarda um pouco para a página carregar
        time.sleep(2)
        
        # 1. Verificar se já está logado (procura pelo painel de chat ou foto de perfil)
        # Elemento comum no painel logado: id side ou o canvas de chat
        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, '//div[@id="side"]'))
            )
            return 'connected', None
        except:
            pass

        # 2. Tentar pegar o QR Code - Estratégia Robusta (Screenshot do Elemento)
        try:
            # O container do QR code geralmente tem o atributo data-ref
            qr_container = WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-ref]'))
            )
            
            # Espera um momento de estabilização
            time.sleep(1)
            
            # Pega o screenshot apenas do container do QR code
            # O Selenium retorna BASE64 limpo (sem header data:image)
            qr_base64 = qr_container.screenshot_as_base64
            
            if qr_base64:
                return 'qr', qr_base64
                
        except Exception as e:
            # Fallback: Tenta pegar o canvas se o container falhar
            try:
                qr_canvas = driver.find_element(By.TAG_NAME, "canvas")
                qr_b64_js = driver.execute_script("""
                    var canvas = document.querySelector('canvas');
                    if (canvas) return canvas.toDataURL('image/png').substring(22);
                    return null;
                """)
                if qr_b64_js:
                    return 'qr', qr_b64_js
            except:
                pass

        return 'loading', None

    except Exception as e:
        return 'error', str(e)

from selenium.webdriver.common.keys import Keys

def send_message_selenium(phone_number, message):
    """
    Envia mensagem via WhatsApp Web usando Selenium
    
    Args:
        phone_number: Número de telefone (com ou sem DDI)
        message: Mensagem a ser enviada
    
    Returns:
        (success: bool, message: str)
    """
    driver = init_driver()
    try:
        # Formata número de telefone
        phone_clean = ''.join(filter(str.isdigit, phone_number))
        
        # Adiciona DDI do Brasil se necessário
        if not phone_clean.startswith("55") and len(phone_clean) >= 10:
            phone_clean = "55" + phone_clean
        
        # Codifica a mensagem
        import urllib.parse
        message_encoded = urllib.parse.quote(message)
        
        link = f"https://web.whatsapp.com/send?phone={phone_clean}&text={message_encoded}"
        driver.get(link)
        
        # Aguarda carregamento inicial da página de chat
        # Aumentamos o tempo pois o carregamento inicial do WA Web pode ser lento
        time.sleep(8)
        
        # 1. Verifica erro de número inválido
        try:
            error_elements = driver.find_elements(By.XPATH, 
                '//div[contains(text(), "número de telefone")] | '
                '//div[contains(text(), "inválido")] | '
                '//div[contains(text(), "invalid")]'
            )
            if error_elements:
                return False, "Número de telefone inválido ou não possui WhatsApp."
        except:
            pass

        # 2. Tenta encontrar a caixa de texto (Input Principal)
        # Isso confirma que o chat carregou
        input_box = None
        try:
            input_box = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[contenteditable="true"][data-tab]'))
            )
            # Dá foco na caixa
            input_box.click() 
            time.sleep(1)
        except:
             # Se não achou a caixa, pode ser que ainda não tenha carregado ou deu erro
             pass

        # 3. Tenta CLICAR no botão enviar (Método Clássico)
        clicked_button = False
        try:
            send_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
            )
            send_btn.click()
            clicked_button = True
        except:
            # Fallback de botão para versões diferentes
            try:
                send_btn = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Enviar"]')
                send_btn.click()
                clicked_button = True
            except:
                pass

        # 4. Se botão falhar, tenta ENTER na caixa de texto (Método Robusto)
        if not clicked_button and input_box:
            try:
                input_box.send_keys(Keys.ENTER)
                time.sleep(1)
                clicked_button = True
            except Exception as e_enter:
                return False, f"Falha ao enviar via Enter: {e_enter}"
            
        if clicked_button:
            time.sleep(2)  # Wait for send animation
            return True, "Mensagem enviada com sucesso"
        else:
            return False, "Não foi possível encontrar o botão de envio nem usar Enter. Verifique se está logado."
            
    except Exception as e:
        return False, f"Erro ao enviar mensagem: {str(e)}"

def close_driver():
    if st.session_state.wa_driver:
        st.session_state.wa_driver.quit()
        st.session_state.wa_driver = None
