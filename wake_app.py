from playwright.sync_api import sync_playwright
import os
import sys

url = os.environ.get("STREAMLIT_URL", "https://feathertranskriptweb.streamlit.app/")

def wake_up():
    with sync_playwright() as p:
        # Lança Chromium com argumentos para evitar detecção
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
        )
        page = browser.new_page()
        # Define um user-agent real
        page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        print(f"Acessando {url} ...")
        page.goto(url, timeout=180000)  # 3 minutos
        
        # Aguarda a página carregar completamente
        page.wait_for_load_state("networkidle")
        
        # Procura pelo botão de "Yes, get this app back up" de várias formas
        try:
            # Seletor mais abrangente: qualquer elemento que contenha o texto exato
            wake_link = page.locator("text=Yes, get this app back up").first
            if wake_link.count() > 0:
                wake_link.click()
                print("✅ Botão 'Yes, get this app back up' clicado!")
                # Aguarda o app iniciar
                page.wait_for_timeout(60000)
            else:
                # Tenta por seletor de botão com texto aproximado
                fallback = page.locator("button:has-text('Yes, get this app back')").first
                if fallback.count() > 0:
                    fallback.click()
                    print("✅ Botão alternativo clicado!")
                    page.wait_for_timeout(60000)
                else:
                    # Se não encontrar, talvez o app já esteja ativo
                    print("✅ Nenhum botão de acordar encontrado. App já ativo?")
        except Exception as e:
            print(f"⚠️ Não foi possível clicar no botão: {e}")
            # Tenta novamente com JavaScript direto
            try:
                page.evaluate('''
                    const btn = [...document.querySelectorAll('*')].find(el => el.innerText === 'Yes, get this app back up!');
                    if (btn) btn.click();
                ''')
                print("✅ Clique via JavaScript executado.")
                page.wait_for_timeout(60000)
            except:
                print("❌ Falha ao acordar via JS também.")
                sys.exit(1)
        
        browser.close()

if __name__ == "__main__":
    wake_up()
    sys.exit(0)
