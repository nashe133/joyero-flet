import flet as ft
import requests
import json
import random

def main(page: ft.Page):
    page.title = "Joyero Pro: Sistema Anti-Bloqueo"
    page.theme_mode = "dark"
    page.scroll = "auto"

    datos_mercado = {"oro": 0, "plata": 0}
    historial_lote = []

    # --- LISTA DE AGENTES PARA ROTAR ---
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36"
    ]

    # --- ELEMENTOS UI ---
    in_gramos = ft.TextField(label="Gramos", value="0", width=120)
    dd_ley = ft.Dropdown(
        label="Ley", width=150,
        options=[ft.dropdown.Option("Plata 925"), ft.dropdown.Option("Plata 900"), ft.dropdown.Option("Oro 18K")],
        value="Plata 925"
    )
    col_resumen = ft.Column()
    txt_gran_total = ft.Text("$ 0", size=35, weight="bold", color="green")
    txt_status = ft.Text("Listo", size=12)

    def obtener_precios(e=None):
        txt_status.value = "Sincronizando con identidad nueva..."
        txt_status.color = "white60"
        page.update()
        
        try:
            # 1. Crear sesión para manejar cookies automáticamente
            session = requests.Session()
            
            # 2. Seleccionar un User-Agent aleatorio
            user_agent_random = random.choice(USER_AGENTS)
            
            # 3. Headers ultra-completos (Engaño total al servidor)
            headers = {
                "User-Agent": user_agent_random,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
                "Referer": "https://goldprice.org/",
                "Origin": "https://goldprice.org/",
                "DNT": "1", # Do Not Track
                "Cache-Control": "no-cache"
            }

            # 4. Probamos con el proxy alternativo rotando la identidad
            target_url = "https://data-asg.goldprice.org/dbXRates/CLP"
            # Usamos corsproxy.io que es el más permisivo actualmente
            proxy_url = f"https://corsproxy.io/?{target_url}"
            
            r = session.get(proxy_url, headers=headers, timeout=12)
            
            if r.status_code == 200:
                data = r.json()
                item = data['items'][0]
                datos_mercado["oro"] = item['xauPrice'] / 31.1035
                datos_mercado["plata"] = item['xagPrice'] / 31.1035
                txt_status.value = f"Éxito (ID: {user_agent_random[10:25]}...)"
                txt_status.color = "green"
            else:
                txt_status.value = f"Error {r.status_code}. Cambiando IP..."
                txt_status.color = "orange"
        except Exception as ex:
            txt_status.value = "Falla de red. Reintente."
            txt_status.color = "red"
        
        page.update()

    # --- LÓGICA DE CÁLCULO (Igual que antes) ---
    def calcular_lote(e):
        try:
            leyes_dict = {"Plata 925": 0.925, "Plata 900": 0.900, "Oro 18K": 0.750}
            peso = float(in_gramos.value.replace(",", "."))
            base = datos_mercado["oro"] if "Oro" in dd_ley.value else datos_mercado["plata"]
            valor = int(peso * base * leyes_dict[dd_ley.value])
            historial_lote.append(ft.Text(f"• {peso}g {dd_ley.value}: $ {valor:,}".replace(",", ".")))
            col_resumen.controls = historial_lote
            
            # Sumar total
            total = sum([int(t.value.split("$ ")[1].replace(".", "")) for t in historial_lote])
            txt_gran_total.value = f"$ {total:,}".replace(",", ".")
            in_gramos.value = "0"
            page.update()
        except: pass

    page.add(
        ft.Text("CALCULADORA ANTI-BLOQUEO", weight="bold"),
        ft.Row([in_gramos, dd_ley, ft.IconButton("add", on_click=calcular_lote)]),
        col_resumen,
        txt_gran_total,
        ft.Row([
            ft.IconButton("refresh", on_click=obtener_precios),
            txt_status
        ])
    )
    obtener_precios()

ft.app(target=main)
