import flet as ft
import requests
import json
import random

def main(page: ft.Page):
    page.title = "Joyero Pro"
    page.theme_mode = "dark"
    page.horizontal_alignment = "center"
    page.scroll = "auto"

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
    txt_oro_24 = ft.Text("$ 0", size=40, weight="bold", color="amber")
    txt_plata_pura = ft.Text("$ 0", size=40, weight="bold", color="bluegrey")
    
    col_oro = ft.Column(horizontal_alignment="center")
    col_plata = ft.Column(horizontal_alignment="center")
    
    txt_status = ft.Text("Iniciando...", size=12)

    def actualizar_interfaz():
        if precios_base["oro"] == 0: return
        
        # Actualizar los precios grandes (24K)
        txt_oro_24.value = "$ " + "{:,}".format(int(precios_base["oro"])).replace(",", ".")
        txt_plata_pura.value = "$ " + "{:,}".format(int(precios_base["plata"])).replace(",", ".")

        col_oro.controls.clear()
        col_plata.controls.clear()

        for nombre, mult in leyes.items():
            es_oro = "Oro" in nombre
            base = precios_base["oro"] if es_oro else precios_base["plata"]
            valor_gramo = int(base * mult)
            color = "amber" if es_oro else "bluegrey"
            
            texto_lista = ft.Text(nombre + ": $ " + "{:,}".format(valor_gramo).replace(",", "."), size=18, color=color)
            
            if es_oro:
                col_oro.controls.append(texto_lista)
            else:
                col_plata.controls.append(texto_lista)
        page.update()

    def obtener_datos(e=None):
        txt_status.value = "Consultando mercado..."
        page.update()

        url_target = "https://data-asg.goldprice.org/dbXRates/CLP"
        # Lista de proxies para evitar el bloqueo 403
        proxies = [
            "https://corsproxy.io/?" + url_target,
            "https://api.allorigins.win/get?url=" + url_target
        ]
        
        random.shuffle(proxies)

        for p_url in proxies:
            try:
                headers = {
                    "User-Agent": random.choice(USER_AGENTS),
                    "Referer": "https://goldprice.org/"
                }
                r = requests.get(p_url, headers=headers, timeout=12)
                
                if r.status_code == 200:
                    raw_res = r.json()
                    # Algunos proxies envuelven el JSON en 'contents'
                    data = json.loads(raw_res['contents']) if 'contents' in raw_res else raw_res
                    
                    item = data['items'][0]
                    precios_base["oro"] = item['xauPrice'] / ONZA_A_GRAMO
                    precios_base["plata"] = item['xagPrice'] / ONZA_A_GRAMO
                    
                    txt_status.value = "Actualizado: " + str(data.get('date', 'Reciente'))
                    actualizar_interfaz()
                    return 
            except:
                continue 
        
        txt_status.value = "Error. Reintenta en 1 min."
        page.update()

    # --- ESTRUCTURA ---
    page.add(
        ft.Text("PRECIOS EN VIVO (1g)", size=25, weight="bold"),
        ft.Divider(),
        
        ft.Text("ORO 24K", size=16, color="amber"),
        txt_oro_24,
        col_oro,
        
        ft.Divider(height=30),
        
        ft.Text("PLATA PURA", size=16, color="bluegrey"),
        txt_plata_pura,
        col_plata,
        
        ft.Divider(height=30),
        
        ft.ElevatedButton("ACTUALIZAR AHORA", icon="refresh", on_click=obtener_datos),
        txt_status
    )
    
    obtener_datos()

ft.app(target=main)
