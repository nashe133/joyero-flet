import flet as ft
import requests
import time

def main(page: ft.Page):
    page.title = "Joyero Pro"
    page.theme_mode = "dark"
    page.horizontal_alignment = "center"
    page.scroll = "auto"
    page.padding = 20

    # --- NO MODIFICADO: TUS LEYES ORIGINALES ---
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
    
    txt_status = ft.Text("Sincronizando...", size=12, italic=True)
    txt_info_mercado = ft.Text("", size=11, color="white60")

    def actualizar_interfaz():
        if precios_base["oro"] == 0: return
        
        # Precios grandes (Puros)
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
        txt_status.value = "Consultando valores internacionales..."
        page.update()

        try:
            # 1. Obtener Dólar en Chile (Mindicador)
            res_dolar = requests.get("https://api.mindicador.cl/dolar", timeout=10).json()
            valor_dolar = res_dolar['serie'][0]['valor']
            
            # 2. Obtener Metales en USD (Yahoo Finance - Sin bloqueo 403)
            headers = {"User-Agent": "Mozilla/5.0"}
            
            # Oro Spot USD
            res_xau = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/XAUUSD=X", headers=headers).json()
            oro_usd_onza = res_xau['chart']['result'][0]['meta']['regularMarketPrice']
            
            # Plata Spot USD
            res_xag = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/XAGUSD=X", headers=headers).json()
            plata_usd_onza = res_xag['chart']['result'][0]['meta']['regularMarketPrice']

            # 3. Transformación a CLP por Gramo
            # (Precio Onza USD * Dólar CLP) / 31.1035
            precios_base["oro"] = (oro_usd_onza * valor_dolar) / ONZA_A_GRAMO
            precios_base["plata"] = (plata_usd_onza * valor_dolar) / ONZA_A_GRAMO

            txt_info_mercado.value = f"Dólar: ${valor_dolar} | Oro: {oro_usd_onza} USD/oz | Plata: {plata_usd_onza} USD/oz"
            txt_status.value = "Sincronizado: " + time.strftime("%H:%M:%S")
            actualizar_interfaz()

        except Exception as ex:
            txt_status.value = "Error de red. Reintente."
        
        page.update()

    # --- ESTRUCTURA ---
    page.add(
        ft.Text("PRECIOS EN VIVO (1g)", size=25, weight="bold"),
        txt_info_mercado,
        ft.Divider(),
        
        ft.Text("ORO 24K", size=16, color="amber"),
        txt_oro_24,
        col_oro,
        
        ft.Divider(height=30),
        
        ft.Text("PLATA PURA", size=16, color="bluegrey"),
        txt_plata_pura,
        col_plata,
        
        ft.Divider(height=30),
        
        ft.ElevatedButton("ACTUALIZAR MERCADO", icon="refresh", on_click=obtener_datos),
        txt_status
    )
    
    obtener_datos()

ft.app(target=main)
