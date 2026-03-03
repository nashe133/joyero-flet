import flet as ft
import requests
import time

def main(page: ft.Page):
    page.title = "Joyero Pro"
    page.theme_mode = "dark"
    page.horizontal_alignment = "center"
    page.scroll = "auto"

    # --- CONFIGURACIÓN ---
    ONZA_A_GRAMO = 31.1035
    DOLAR_MANUAL = 965  # <--- Cambia este valor según el dólar del día
    
    precios_base = {"oro": 0, "plata": 0}
    
    leyes = {
        "Oro 22K": 0.9167, "Oro 21K": 0.900, "Oro 18K": 0.750, 
        "Oro 14K": 0.583, "Oro 10K": 0.4167, "Plata 980": 0.980, 
        "Plata 950": 0.950, "Plata 925": 0.925, "Plata 900": 0.900
    }

    # --- UI ---
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
            valor = int(base * mult)
            
            color = "amber" if es_oro else "bluegrey"
            txt = ft.Text(f"{nombre}: $ " + "{:,}".format(valor).replace(",", "."), size=18, color=color)
            
            if es_oro: col_oro.controls.append(txt)
            else: col_plata.controls.append(txt)
        page.update()

    def obtener_datos(e=None):
        txt_status.value = "Consultando SilverPrice..."
        page.update()

        try:
            # Headers obligatorios para que la API de SilverPrice no dé Forbidden
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'referer': 'https://silverprice.org/',
                'accept': 'application/json, text/javascript, */*; q=0.01'
            }

            # Consultar Plata (XAG)
            res_xag = requests.get('https://data-asg.goldprice.org/GetData/USD-XAG/1', headers=headers, timeout=10)
            # Consultar Oro (XAU)
            res_xau = requests.get('https://data-asg.goldprice.org/GetData/USD-XAU/1', headers=headers, timeout=10)

            if res_xag.status_code == 200 and res_xau.status_code == 200:
                # La API responde "precio,precio,precio...", tomamos el primero
                plata_usd = float(res_xag.text.split(',')[0])
                oro_usd = float(res_xau.text.split(',')[0])

                # Conversión manual a CLP
                precios_base["oro"] = (oro_usd * DOLAR_MANUAL) / ONZA_A_GRAMO
                precios_base["plata"] = (plata_usd * DOLAR_MANUAL) / ONZA_A_GRAMO

                txt_status.value = "Actualizado: " + time.strftime("%H:%M:%S")
                actualizar_interfaz()
            else:
                txt_status.value = f"Error API: {res_xag.status_code}"

        except Exception as ex:
            txt_status.value = "Error de conexión o formato"
        
        page.update()

    # --- ESTRUCTURA ---
    page.add(
        ft.Text("JOYERO PRO", size=25, weight="bold"),
        ft.Text(f"Dólar base: ${DOLAR_MANUAL}", size=12, color="white60"),
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
