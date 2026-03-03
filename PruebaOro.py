import flet as ft
import requests
import time

def main(page: ft.Page):
    page.title = "Joyero Pro - API Directa"
    page.theme_mode = "dark"
    page.horizontal_alignment = "center"
    page.scroll = "auto"
    page.padding = 20

    # --- TUS LEYES ORIGINALES ---
    leyes = {
        "Oro 22K": 0.9167, "Oro 21K": 0.900, "Oro 18K": 0.750, 
        "Oro 14K": 0.583, "Oro 10K": 0.4167, "Plata 980": 0.980, 
        "Plata 950": 0.950, "Plata 925": 0.925, "Plata 900": 0.900
    }

    # --- ELEMENTOS DE INTERFAZ ---
    txt_oro_raw = ft.Text("0.00", size=35, weight="bold", color="amber")
    txt_plata_raw = ft.Text("0.00", size=35, weight="bold", color="bluegrey")
    
    col_oro = ft.Column(horizontal_alignment="center")
    col_plata = ft.Column(horizontal_alignment="center")
    
    txt_status = ft.Text("Listo para consultar", size=12)

    def actualizar_interfaz(oro_base, plata_base):
        col_oro.controls.clear()
        col_plata.controls.clear()

        for nombre, mult in leyes.items():
            es_oro = "Oro" in nombre
            base = oro_base if es_oro else plata_base
            valor_final = base * mult
            color = "amber" if es_oro else "bluegrey"
            
            # Mostramos el valor directo de la API multiplicado por la ley
            texto_lista = ft.Text(f"{nombre}: {valor_final:.2f}", size=18, color=color)
            
            if es_oro:
                col_oro.controls.append(texto_lista)
            else:
                col_plata.controls.append(texto_lista)
        page.update()

    def obtener_datos(e=None):
        txt_status.value = "Consultando Oro..."
        txt_status.color = "white"
        page.update()

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': '*/*',
                'Origin': 'https://silverprice.org',
                'Referer': 'https://silverprice.org/'
            }

            # PETICIÓN 1: ORO
            res_xau = requests.get('https://data-asg.goldprice.org/GetData/USD-XAU/1', headers=headers, timeout=10)
            val_oro = float(res_xau.text.split(',')[0])
            txt_oro_raw.value = f"{val_oro:.2f}"
            
            # Separación de peticiones
            time.sleep(0.5)
            
            txt_status.value = "Consultando Plata..."
            page.update()

            # PETICIÓN 2: PLATA
            res_xag = requests.get('https://data-asg.goldprice.org/GetData/USD-XAG/1', headers=headers, timeout=10)
            val_plata = float(res_xag.text.split(',')[0])
            txt_plata_raw.value = f"{val_plata:.2f}"

            # Actualizar leyes
            actualizar_interfaz(val_oro, val_plata)
            
            txt_status.value = f"Actualizado: {time.strftime('%H:%M:%S')}"
            txt_status.color = "green"

        except Exception as ex:
            txt_status.value = "Error en la conexión con la API"
            txt_status.color = "red"
        
        page.update()

    # --- ESTRUCTURA ---
    page.add(
        ft.Text("VALORES SPOT API", size=25, weight="bold"),
        ft.Divider(),
        
        ft.Text("ORO (XAU)", size=16, color="amber"),
        txt_oro_raw,
        col_oro,
        
        ft.Divider(height=30),
        
        ft.Text("PLATA (XAG)", size=16, color="bluegrey"),
        txt_plata_raw,
        col_plata,
        
        ft.Divider(height=30),
        
        ft.ElevatedButton("ACTUALIZAR DATOS", icon="refresh", on_click=obtener_datos),
        txt_status
    )
    
    obtener_datos()

ft.app(target=main)
