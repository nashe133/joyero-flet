import flet as ft
import requests

def main(page: ft.Page):
    page.title = "Joyero Pro: Cotizador de Metales"
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    # Configuración técnica
    ONZA_A_GRAMO = 31.1035
    precios_gramo = {"oro": 0, "plata": 0}
    
    leyes = {
        "Oro 22K": 0.9167, "Oro 21K": 0.900, "Oro 18K": 0.750, 
        "Oro 14K": 0.583, "Oro 10K": 0.4167, "Plata 980": 0.980, 
        "Plata 950": 0.950, "Plata 925": 0.925, "Plata 900": 0.900
    }

    # --- ELEMENTOS DE INTERFAZ ---
    txt_oro_v = ft.Text("$ 0", size=45, weight="bold", color="amber")
    txt_plata_v = ft.Text("$ 0", size=45, weight="bold", color="bluegrey")
    
    col_kila_oro = ft.Column(horizontal_alignment="center", spacing=5)
    col_kila_plata = ft.Column(horizontal_alignment="center", spacing=5)
    
    txt_status = ft.Text("Actualizando precios...", size=12, italic=True)

    def obtener_datos(e=None):
        txt_status.value = "Consultando mercado..."
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
                    col = col_kila_oro if "Oro" in nombre else col_kila_plata
                    
                    col.controls.append(
                        ft.Container(
                            content=ft.Text(f"{nombre}: {valor}", size=18, color=color_txt, weight="w500"),
                            padding=8,
                            bgcolor="white10",
                            border_radius=10,
                            width=280,
                            alignment=ft.alignment.center
                        )
                    )
                
                txt_status.value = f"Sincronizado: {data['date']}"
            page.update()
        except Exception:
            txt_status.value = "Sin conexión: Reintenta en un momento"
            page.update()

    # --- PANELES ---
    panel_vivo = ft.Column([
        ft.Text("PRECIO 1g PURO (24K)", size=22, weight="bold"),
        ft.Divider(height=20, color="transparent"),
        ft.Icon("stars", color="amber", size=40),
        ft.Text("ORO", color="amber", size=16), 
        txt_oro_v,
        ft.Divider(height=10, color="transparent"),
        ft.Icon("monetization_on", color="bluegrey", size=40),
        ft.Text("PLATA", color="bluegrey", size=16), 
        txt_plata_v,
        ft.Divider(height=30, color="transparent"),
        ft.ElevatedButton(
            "ACTUALIZAR PRECIOS", 
            icon="refresh", 
            on_click=obtener_datos
        ),
    ], horizontal_alignment="center", visible=True)

    panel_kila = ft.Column([
        ft.Text("VALOR POR LEY", size=22, weight="bold"),
        ft.Divider(),
        ft.Text("ORO", color="amber", weight="bold", size=18),
        col_kila_oro,
        ft.Divider(height=20, color="transparent"),
        ft.Text("PLATA", color="bluegrey", weight="bold", size=18),
        col_kila_plata,
    ], horizontal_alignment="center", visible=False)

    def cambiar_tab(e):
        idx = int(e.data)
        if idx == 0:
            panel_vivo.visible, panel_kila.visible = True, False
        else:
            panel_vivo.visible, panel_kila.visible = False, True
        page.update()

    # --- SOLUCIÓN AL ERROR DE NAVIGATION ---
    # Usamos ft.NavigationBar con sus destinos corregidos
    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(icon="analytics", label="Precios"),
            ft.NavigationDestination(icon="format_list_bulleted", label="Leyes"),
        ],
        on_change=cambiar_tab,
    )

    page.add(
        ft.Container(
            content=ft.Column([
                panel_vivo,
                panel_kila,
                ft.Divider(height=30, color="transparent"),
                txt_status
            ], horizontal_alignment="center"),
            padding=15
        )
    )
    
    obtener_datos()

ft.app(target=main)
