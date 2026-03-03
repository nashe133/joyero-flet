import flet as ft
import requests
import json
import time

def main(page: ft.Page):
    page.title = "Joyero Pro - SilverPrice API"
    page.theme_mode = "dark"
    page.horizontal_alignment = "center"
    page.scroll = "auto"
    page.padding = 20

    # --- TUS LEYES ORIGINALES (Mantenidas estrictamente) ---
    ONZA_A_GRAMO = 31.1035
    precios_base = {"oro": 0, "plata": 0}
    
    leyes = {
        "Oro 22K": 0.9167, "Oro 21K": 0.900, "Oro 18K": 0.750, 
        "Oro 14K": 0.583, "Oro 10K": 0.4167, "Plata 980": 0.980, 
        "Plata 950": 0.950, "Plata 925": 0.925, "Plata 900": 0.900
    }

    # --- ELEMENTOS DE INTERFAZ ---
    txt_oro_24 = ft.Text("$ 0", size=40, weight="bold", color="amber")
    txt_plata_pura = ft.Text("$ 0", size=40, weight="bold", color="bluegrey")
    
    col_oro = ft.Column(horizontal_alignment="center")
    col_plata = ft.Column(horizontal_alignment="center")
    
    txt_status = ft.Text("Listo", size=12, italic=True)

    def actualizar_interfaz():
        if precios_base["oro"] == 0: return
        
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
        txt_status.value = "Consultando SilverPrice API..."
        page.update()

        try:
            # 1. Primero necesitamos el valor del Dólar para convertir el USD de la API a CLP
            # Usamos una fuente rápida y sin bloqueos
            res_d = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()
            valor_dolar = res_d['rates']['CLP']

            # 2. Consultar la nueva API de SilverPrice (Plata)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'referer': 'https://silverprice.org/'
            }
            
            # API Plata (USD/oz)
            res_xag = requests.get('https://data-asg.goldprice.org/GetData/USD-XAG/1', headers=headers, timeout=10)
            # La API devuelve algo como "90.11,89.50,..." tomamos el primer valor
            plata_usd_onza = float(res_xag.text.split(',')[0])

            # API Oro (USD/oz) - Usamos la misma ruta pero para Oro
            res_xau = requests.get('https://data-asg.goldprice.org/GetData/USD-XAU/1', headers=headers, timeout=10)
            oro_usd_onza = float(res_xau.text.split(',')[0])

            # 3. Cálculo: (Precio USD * Dólar CLP) / Gramos Onza
            precios_base["oro"] = (oro_usd_onza * valor_dolar) / ONZA_A_GRAMO
            precios_base["plata"] = (plata_usd_onza * valor_dolar) / ONZA_A_GRAMO

            txt_status.value = f"Sincronizado (Dólar: ${valor_dolar})"
            actualizar_interfaz()

        except Exception as ex:
            txt_status.value = "Error: La API requiere Proxy o está saturada"
        
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
        ft.ElevatedButton("ACTUALIZAR", icon="refresh", on_click=obtener_datos),
        txt_status
    )
    
    obtener_datos()

ft.app(target=main)
