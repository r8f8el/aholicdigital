#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conectar Conta do Instagram para o Prospector de Sites.
Abre o Google Chrome real para você fazer login.
Salva a sessão em config/instagram_session.json.
"""
import asyncio, os, sys
from playwright.async_api import async_playwright

WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_DIR = os.path.join(WORKSPACE, "config")
SESSION_FILE = os.path.join(CONFIG_DIR, "instagram_session.json")
os.makedirs(CONFIG_DIR, exist_ok=True)

async def conectar():
    print("=" * 60)
    print("🔑 CONECTAR INSTAGRAM NO PROSPECTOR")
    print("=" * 60)
    print("[*] Abrindo o Google Chrome na tela de login do Instagram...")
    print("[*] Faça login com sua conta (usuário e senha).")
    print("[*] Assim que você entrar no Instagram, a sessão será salva automaticamente!")
    print("=" * 60)

    async with async_playwright() as p:
        # Abre o Google Chrome instalado
        try:
            browser = await p.chromium.launch(headless=False, channel="chrome")
        except Exception:
            browser = await p.chromium.launch(headless=False)
            
        context = await browser.new_context(
            locale="pt-BR",
            viewport={"width": 1280, "height": 900}
        )
        page = await context.new_page()

        await page.goto("https://www.instagram.com/accounts/login/")

        # Aguarda login do usuário (até 5 minutos)
        logado = False
        print("\n>> Aguardando você fazer login na janela do Chrome...")
        for seg in range(300):
            await asyncio.sleep(1)
            cookies = await context.cookies()
            cookie_names = [c["name"] for c in cookies]
            
            # Se encontrou o cookie sessionid, o usuário logou!
            if "sessionid" in cookie_names:
                logado = True
                print("\n[+] SUCESSO! Login autenticado detectado!")
                await asyncio.sleep(2)
                break

        if logado:
            await context.storage_state(path=SESSION_FILE)
            print(f"[+] Sessão salva em: {SESSION_FILE}")
            print("[+] Agora o robô consegue rolar infinitos posts e ver o perfil completo!")
            print("=" * 60)
            await asyncio.sleep(3)
        else:
            print("\n[-] Tempo limite atingido sem login.")

        await browser.close()

if __name__ == '__main__':
    asyncio.run(conectar())
