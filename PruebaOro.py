import flet as ft
import requests
import json
import random

def main(page: ft.Page):
    page.title = "Joyero Pro"
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

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.164 Mobile Safari/537.36"
    ]

    # --- ELEMENTOS DE INTERFAZ ---
    # Eliminado 'suffix_text' para evitar el error de versión
    in_gramos = ft.TextField(
        label="Gramos", value="1", width=140, text_align="center",
        on_change=lambda _: actualizar_interfaz()
    )

    in_margen = ft.TextField(
        label="Ajuste %", value="0", width=140, text_align="center",
        on_change=lambda _: actualizar_interfaz()
    )

    col_oro = ft.Column(horizontal_alignment="center", spacing=8)
    col_plata = ft.Column(horizontal_alignment="center", spacing=8)
    txt_status = ft.Text("Iniciando...", size=12, italic=True)

    def actualizar_interfaz():
        if precios_base["oro"] == 0: return
        
        try:
            gramos_val = in_gramos.value.replace(",", ".")
            gramos = float(gramos_val if gramos_val else 0)
            
            margen_val = in_margen.value.replace(",", ".")
            margen = 1 + (float(margen_val if margen_val else 0) / 100)
        except:
            gramos, margen = 0, 1

        col_oro.controls.clear()
        col_plata.controls.clear()

        for nombre, mult in leyes.items():
            es_oro = "Oro" in nombre
            base = precios_base["oro"] if es_oro else precios_base["plata"]
            total = int(base * mult * gramos * margen)
            color = "amber" if es_oro else "bluegrey"
            
            card = ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text(nombre, weight="bold", size=14),
                        ft.Text(f"{gramos}g", size=11),
                    ], spacing=2),
                    ft.Text(f"$ {total:,}".replace(",", "."), size=20, color=color, weight="bold")
                ], alignment="spaceBetween"),
                padding=15, bgcolor="white10", border_radius=12, width=340
            )
            
            if es_oro: col_oro.controls.append(card)
            else: col_plata.controls.append(card)
        page.update()

    def obtener_datos(e=None):
        txt_status.value = "Actualizando mercado..."
        page.update()

        url_target = "https://data-asg.goldprice.org/dbXRates/CLP"
        proxies = [
            f"https://corsproxy.io/?{url_target}",
            f"https://api.allorigins.win/get?url={url_target}"
        ]
        
        random.shuffle(proxies)

        for p_url in proxies:
            try:
                headers = {"User-Agent": random.choice(USER_AGENTS), "Referer": "https://goldprice.org/"}
                r = requests.get(p_url, headers=headers, timeout=12)
                
                if r.status_code == 200:
                    # Detectar si el proxy envolvió el JSON o no
                    raw_res = r.json()
                    data = json.loads(raw_res['contents']) if 'contents' in raw_res else raw_res
                    
                    item = data['items'][0]
                    precios_base["oro"] = item['xauPrice'] / ONZA_A_GRAMO
                    precios_base["plata"] = item['xagPrice'] / ONZA_A_GRAMO
                    
                    txt_status.value = "Sincronizado"
                    actualizar_interfaz()
                    return 
            except:
                continue 
        
        txt_status.value = "Error. Reintenta en 1 min."
        page.update()

    # --- ESTRUCTURA ---
    page.add(
        ft.Text("JOYERO PRO", size=26, weight="black", color="amber"),
        ft.Row([
            in_gramos, 
            in_margen,
            ft.IconButton(ft.icons.REFRESH, on_click=obtener_datos)
        ], alignment="center"),
        ft.Divider(height=20),
        ft.Text("ORO", weight="bold", color="amber"),
        col_oro,
        ft.Text("PLATA", weight="bold", color="bluegrey"),
        col_plata,
        txt_status
    )
    
    obtener_datos()

ft.app(target=main)
