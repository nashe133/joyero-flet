import flet as ft
import requests
import json
import random

def main(page: ft.Page):
    page.title = "Joyero Pro: Cotizador Realtime"
    page.theme_mode = "dark"
    page.horizontal_alignment = "center"
    page.scroll = "auto"
    page.padding = 20

    # --- CONFIGURACIÓN TÉCNICA ---
    ONZA_A_GRAMO = 31.1035
    precios_base = {"oro": 0, "plata": 0}
    
    leyes = {
        "Oro 22K": 0.9167, "Oro 21K": 0.900, "Oro 18K": 0.750, 
        "Oro 14K": 0.583, "Oro 10K": 0.4167, "Plata 980": 0.980, 
        "Plata 950": 0.950, "Plata 925": 0.925, "Plata 900": 0.900
    }

    # Lista de identidades para rotar
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.164 Mobile Safari/537.36"
    ]

    # --- ELEMENTOS DE INTERFAZ ---
    in_gramos = ft.TextField(
        label="Gramos", value="1", width=150, text_align="center",
        keyboard_type="number", on_change=lambda _: actualizar_interfaz()
    )

    in_margen = ft.TextField(
        label="Ajuste %", value="0", width=120, text_align="center",
        suffix_text="%", on_change=lambda _: actualizar_interfaz()
    )

    col_oro = ft.Column(horizontal_alignment="center", spacing=8)
    col_plata = ft.Column(horizontal_alignment="center", spacing=8)
    txt_status = ft.Text("Iniciando...", size=12, italic=True, color="white60")

    def actualizar_interfaz():
        if precios_base["oro"] == 0: return
        
        try:
            gramos = float(in_gramos.value.replace(",", ".") or 0)
            margen = 1 + (float(in_margen.value or 0) / 100)
        except:
            gramos, margen = 0, 1

        col_oro.controls.clear()
        col_plata.controls.clear()

        for nombre, mult in leyes.items():
            es_oro = "Oro" in nombre
            base = precios_base["oro"] if es_oro else precios_base["plata"]
            total = int(base * mult * gramos * margen)
            color = "amber" if es_oro else "bluegrey"
            
            col = col_oro if es_oro else col_plata
            col.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(nombre, weight="bold", size=14),
                            ft.Text(f"{gramos}g", size=11, color="white60"),
                        ], spacing=2),
                        ft.Text(f"$ {total:,}".replace(",", "."), size=20, color=color, weight="bold")
                    ], alignment="spaceBetween"),
                    padding=15, bgcolor="white10", border_radius=12, width=350,
                    border=ft.border.all(1, "white10")
                )
            )
        page.update()

    def obtener_datos(e=None):
        txt_status.value = "Rotando identidad y consultando..."
        txt_status.color = "amber"
        page.update()

        url_target = "https://data-asg.goldprice.org/dbXRates/CLP"
        # Proxies disponibles para redundancia
        proxies = [
            f"https://api.allorigins.win/get?url={url_target}",
            f"https://corsproxy.io/?{url_target}"
        ]
        
        # Mezclamos los proxies para no usar siempre el mismo al inicio
        random.shuffle(proxies)

        for p_url in proxies:
            try:
                headers = {
                    "User-Agent": random.choice(USER_AGENTS),
                    "Referer": "https://goldprice.org/",
                    "Cache-Control": "no-cache"
                }
                
                r = requests.get(p_url, headers=headers, timeout=12)
                
                if r.status_code == 200:
                    # AllOrigins devuelve un JSON con el campo 'contents'
                    if "allorigins" in p_url:
                        res_json = r.json()
                        data = json.loads(res_json['contents'])
                    else:
                        # Corsproxy devuelve el JSON directo
                        data = r.json()
                    
                    item = data['items'][0]
                    precios_base["oro"] = item['xauPrice'] / ONZA_A_GRAMO
                    precios_base["plata"] = item['xagPrice'] / ONZA_A_GRAMO
                    
                    txt_status.value = f"Sincronizado: {data['date']}"
                    txt_status.color = "green"
                    actualizar_interfaz()
                    return # Si tuvo éxito, salimos del bucle de proxies
            except Exception as ex:
                continue # Si falla un proxy, intenta con el siguiente
        
        txt_status.value = "Error: Servidores saturados. Reintenta en 1 min."
        txt_status.color = "red"
        page.update()

    # --- ESTRUCTURA ---
    page.add(
        ft.Text("JOYERO PRO", size=28, weight="black", color="amber"),
        ft.Text("MODO COMPRA / VENTA", size=12, color="white60"),
        ft.Divider(height=10, color="transparent"),
        
        ft.Row([
            in_gramos, 
            in_margen,
            ft.IconButton(ft.icons.REFRESH_ROUNDED, on_click=obtener_datos, icon_color="amber")
        ], alignment="center"),
        
        ft.Divider(height=20, color="white10"),
        
        ft.Text("ORO", size=16, weight="bold", color="amber"),
        col_oro,
        
        ft.Divider(height=20, color="transparent"),
        
        ft.Text("PLATA", size=16, weight="bold", color="bluegrey"),
        col_plata,
        
        ft.Divider(height=20),
        txt_status
    )
    
    obtener_datos()

ft.app(target=main)
