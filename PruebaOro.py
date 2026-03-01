import flet as ft
import requests

def main(page: ft.Page):
    page.title = "Joyero Pro"
    page.theme_mode = "dark"
    page.horizontal_alignment = "center"
    page.scroll = "auto"

    ONZA_A_GRAMO = 31.1035
    precios_gramo = {"oro": 0, "plata": 0}
    
    leyes = {
        "Oro 22K": 0.9167, "Oro 21K": 0.900, "Oro 18K": 0.750, 
        "Oro 14K": 0.583, "Oro 10K": 0.4167, "Plata 980": 0.980, 
        "Plata 950": 0.950, "Plata 925": 0.925, "Plata 900": 0.900
    }

    # --- ELEMENTOS DE INTERFAZ ---
    txt_oro_v = ft.Text("$ 0", size=40, weight="bold", color="amber")
    txt_plata_v = ft.Text("$ 0", size=40, weight="bold", color="bluegrey")
    
    col_kila_oro = ft.Column(horizontal_alignment="center")
    col_kila_plata = ft.Column(horizontal_alignment="center")
    
    txt_status = ft.Text("Cargando...", size=12)

    def obtener_datos(e=None):
        txt_status.value = "Consultando..."
        page.update()
        try:
            url = "https://data-asg.goldprice.org/dbXRates/CLP"
            headers = {'User-Agent': 'okhttp/4.12.0'}
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                item = data['items'][0]
                
                precios_gramo["oro"] = item['xauPrice'] / ONZA_A_GRAMO
                precios_gramo["plata"] = item['xagPrice'] / ONZA_A_GRAMO

                txt_oro_v.value = f"$ {int(precios_gramo['oro']):,}".replace(",", ".")
                txt_plata_v.value = f"$ {int(precios_gramo['plata']):,}".replace(",", ".")
                
                col_kila_oro.controls.clear()
                col_kila_plata.controls.clear()
                
                for nombre, mult in leyes.items():
                    base = precios_gramo["oro"] if "Oro" in nombre else precios_gramo["plata"]
                    valor = f"$ {int(base * mult):,}".replace(",", ".")
                    color_txt = "amber" if "Oro" in nombre else "bluegrey"
                    
                    col_kila_oro.controls.append(ft.Text(f"{nombre}: {valor}", color=color_txt)) if "Oro" in nombre else col_kila_plata.controls.append(ft.Text(f"{nombre}: {valor}", color=color_txt))
                
                txt_status.value = "Actualizado"
            page.update()
        except:
            txt_status.value = "Error de red"
            page.update()

    # --- PANELES ---
    panel_vivo = ft.Column([
        ft.Text("ORO 24K", color="amber"), 
        txt_oro_v,
        ft.Text("PLATA PURA", color="bluegrey"), 
        txt_plata_v,
        ft.ElevatedButton("ACTUALIZAR", on_click=obtener_datos),
    ], horizontal_alignment="center")

    panel_kila = ft.Column([
        ft.Text("ORO", weight="bold"),
        col_kila_oro,
        ft.Text("PLATA", weight="bold"),
        col_kila_plata,
    ], horizontal_alignment="center", visible=False)

    # --- NAVEGACIÓN (Sintaxis ultra-compatible) ---
    def cambiar_tab(e):
        idx = e.control.selected_index
        panel_vivo.visible = (idx == 0)
        panel_kila.visible = (idx == 1)
        page.update()

    # Cambiado 'text' por 'label' para compatibilidad antigua
    tabs = ft.Tabs(
        selected_index=0,
        on_change=cambiar_tab,
        tabs=[
            ft.Tab(label="Precios"),
            ft.Tab(label="Leyes"),
        ],
    )

    page.add(
        tabs,
        panel_vivo,
        panel_kila,
        txt_status
    )
    
    obtener_datos()

ft.app(target=main)
