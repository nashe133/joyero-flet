import flet as ft
import requests
import time

def main(page: ft.Page):
    page.title = "Joyero Pro - Gold API Edition"
    page.theme_mode = "dark"
    page.horizontal_alignment = "center"
    page.scroll = "auto"
    page.padding = 20

    # --- CONFIGURACIÓN ---
    # Por ahora en 1 para que veas el valor USD directo
    VALOR_DOLAR = 1 
    ONZA_A_GRAMO = 31.1035
    
    # Tus leyes originales
    leyes = {
        "Oro 22K": 0.9167, "Oro 21K": 0.900, "Oro 18K": 0.750, 
        "Oro 14K": 0.583, "Oro 10K": 0.4167, "Plata 980": 0.980, 
        "Plata 950": 0.950, "Plata 925": 0.925, "Plata 900": 0.900
    }

    # --- ELEMENTOS DE INTERFAZ ---
    txt_oro_24 = ft.Text("USD 0", size=40, weight="bold", color="amber")
    txt_plata_pura = ft.Text("USD 0", size=40, weight="bold", color="bluegrey")
    
    col_oro = ft.Column(horizontal_alignment="center")
    col_plata = ft.Column(horizontal_alignment="center")
    
    txt_status = ft.Text("Listo para consultar", size=12, italic=True)

    def actualizar_interfaz(p_oro_oz, p_plata_oz):
        # Conversión a gramo (puedes cambiar VALOR_DOLAR cuando quieras)
        gramo_oro = (p_oro_oz * VALOR_DOLAR) / ONZA_A_GRAMO
        gramo_plata = (p_plata_oz * VALOR_DOLAR) / ONZA_A_GRAMO

        # Mostrar valores principales
        txt_oro_24.value = f"USD {gramo_oro:.2f}"
        txt_plata_pura.value = f"USD {gramo_plata:.2f}"

        col_oro.controls.clear()
        col_plata.controls.clear()

        for nombre, mult in leyes.items():
            es_oro = "Oro" in nombre
            base = gramo_oro if es_oro else gramo_plata
            valor_final = base * mult
            
            color = "amber" if es_oro else "bluegrey"
            # Formateo a 2 decimales para USD
            texto_lista = ft.Text(f"{nombre}: USD {valor_final:.2f}", size=18, color=color)
            
            if es_oro:
                col_oro.controls.append(texto_lista)
            else:
                col_plata.controls.append(texto_lista)
        page.update()

    def obtener_datos(e=None):
        txt_status.value = "Consultando gold-api.com..."
        page.update()

        headers = {
            "User-Agent": "okhttp/4.9.2",
            "Accept": "application/json"
        }

        try:
            # Petición para Plata (XAG)
            res_xag = requests.get("https://api.gold-api.com/price/XAG", headers=headers, timeout=10)
            data_xag = res_xag.json()
            precio_plata_oz = data_xag["price"]

            # Petición para Oro (XAU)
            res_xau = requests.get("https://api.gold-api.com/price/XAU", headers=headers, timeout=10)
            data_xau = res_xau.json()
            precio_oro_oz = data_xau["price"]

            actualizar_interfaz(precio_oro_oz, precio_plata_oz)
            txt_status.value = f"Actualizado: {data_xag['updatedAtReadable']}"
            txt_status.color = "green"

        except Exception as ex:
            txt_status.value = "Error al conectar con la API"
            txt_status.color = "red"
        
        page.update()

    # --- ESTRUCTURA ---
    page.add(
        ft.Text("PRECIOS INTERNACIONALES (1g)", size=25, weight="bold"),
        ft.Divider(),
        
        ft.Text("ORO (XAU)", size=16, color="amber"),
        txt_oro_24,
        col_oro,
        
        ft.Divider(height=30),
        
        ft.Text("PLATA (XAG)", size=16, color="bluegrey"),
        txt_plata_pura,
        col_plata,
        
        ft.Divider(height=30),
        
        ft.ElevatedButton("ACTUALIZAR", icon="refresh", on_click=obtener_datos),
        txt_status
    )
    
    obtener_datos()

ft.app(target=main)
