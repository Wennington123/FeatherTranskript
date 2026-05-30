# wake_app.py
from playwright.sync_api import sync_playwright
import os
import sys

url = os.environ.get("STREAMLIT_URL", "https://feathertranskriptweb.streamlit.app/")

try:
    with sync_playwright() as p:
        # Lança o Chromium em modo headless (sem interface gráfica)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"Acessando {url} ...")
        page.goto(url, timeout=120000)  # 120 segundos para carregar
        
        # Verifica se apareceu o botão de "acordar" (caso o app esteja dormindo)
        try:
            wake_button = page.locator("button:has-text('Yes, get this app back up')")
            if wake_button.count() > 0:
                wake_button.click()
                print("✅ Botão 'Acordar' clicado. Aguardando 60s...")
                page.wait_for_timeout(60000)
            else:
                print("✅ App já estava ativo (nenhum botão de acordar encontrado).")
        except Exception as e:
            # Se não encontrar o botão, provavelmente o app já está acordado
            print(f"Info: {e} - App já ativo.")
        
        browser.close()
        sys.exit(0)
except Exception as e:
    print(f"❌ Erro ao tentar acordar o app: {e}")
    sys.exit(1)
