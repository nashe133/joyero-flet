import flet as ft
import requests
import time

def main(page: ft.Page):
    page.title = "Joyero Pro - Live Edition"
    page.theme_mode = "dark"
    page.horizontal_alignment = "center"
    page.scroll = "auto"
    page.padding = 20

    # --- CONFIGURACIÓN ESTÁTICA ---
    ONZA_A_GRAMO = 31.1035
    leyes = {
        "Oro 22K": 0.9167, "Oro 21K": 0.900, "Oro 18K": 0.750, 
        "Oro 14K": 0.583, "Oro 10K": 0.4167, "Plata 980": 0.980, 
        "Plata 950": 0.950, "Plata 925": 0.925, "Plata 900": 0.900
    }

    # --- ELEMENTOS DE INTERFAZ ---
    txt_dolar = ft.Text("Dólar: $ 0", size=16, color="blue")
    txt_oro_24 = ft.Text("$ 0", size=40, weight="bold", color="amber")
    txt_plata_pura = ft.Text("$ 0", size=40, weight="bold", color="bluegrey")
    
    col_oro = ft.Column(horizontal_alignment="center")
    col_plata = ft.Column(horizontal_alignment="center")
    
    txt_status = ft.Text("Sincronizando mercado...", size=12, italic=True)

    def actualizar_interfaz(p_oro_oz, p_plata_oz, valor_dolar):
        # Fórmula Maestra: (Precio Onza USD * Dólar CLP) / 31.1035
        gramo_oro_clp = (p_oro_oz * valor_dolar) / ONZA_A_GRAMO
        gramo_plata_clp = (p_plata_oz * valor_dolar) / ONZA_A_GRAMO

        # Actualizar textos principales (Formato Chileno: $ 12.345)
        txt_dolar.value = f"Dólar: $ {valor_dolar:.2f}"
        txt_oro_24.value = f"$ {int(gramo_oro_clp):,}".replace(",", ".")
        txt_plata_pura.value = f"$ {int(gramo_plata_clp):,}".replace(",", ".")

        col_oro.controls.clear()
        col_plata.controls.clear()

        for nombre, mult in leyes.items():
            es_oro = "Oro" in nombre
            base = gramo_oro_clp if es_oro else gramo_plata_clp
            valor_final = int(base * mult)
            
            color = "amber" if es_oro else "bluegrey"
            texto_lista = ft.Text(f"{nombre}: $ {valor_final:,}".replace(",", "."), size=18, color=color)
            
            if es_oro:
                col_oro.controls.append(texto_lista)
            else:
                col_plata.controls.append(texto_lista)
        page.update()

    def obtener_datos(e=None):
        txt_status.value = "Consultando divisas y metales..."
        txt_status.color = "white"
        page.update()

        headers_metales = {"User-Agent": "okhttp/4.9.2"}
        headers_dolar = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6)"}

        try:
            # 1. Obtener Dólar
            res_dolar = requests.get("https://vsxapps.com/service/api/taxa/?m1=CLP&m2=USD&origem=android-app", headers=headers_dolar, timeout=10)
            data_dolar = res_dolar.json()
            valor_clp = float(data_dolar["TaxaInvertida"])

            # 2. Obtener Metales
            res_xag = requests.get("https://api.gold-api.com/price/XAG", headers=headers_metales, timeout=10)
            res_xau = requests.get("https://api.gold-api.com/price/XAU", headers=headers_metales, timeout=10)
            
            p_plata_oz = res_xag.json()["price"]
            p_oro_oz = res_xau.json()["price"]

            # 3. Calcular y Mostrar
            actualizar_interfaz(p_oro_oz, p_plata_oz, valor_clp)
            
            txt_status.value = f"Actualizado: {time.strftime('%H:%M:%S')}"
            txt_status.color = "green"

        except Exception as ex:
            txt_status.value = "Error de conexión. Reintente."
            txt_status.color = "red"
        
        page.update()

    # --- ESTRUCTURA ---
    page.add(
        ft.Text("JOYERO PRO - PRECIOS REALES", size=25, weight="bold"),
        txt_dolar,
        ft.Divider(),
        
        ft.Text("ORO 24K (Gramo)", size=16, color="amber"),
        txt_oro_24,
        col_oro,
        
        ft.Divider(height=30),
        
        ft.Text("PLATA PURA (Gramo)", size=16, color="bluegrey"),
        txt_plata_pura,
        col_plata,
        
        ft.Divider(height=30),
        
        ft.ElevatedButton("ACTUALIZAR TODO", icon="refresh", on_click=obtener_datos),
        txt_status
    )
    
    obtener_datos()

ft.app(target=main)
