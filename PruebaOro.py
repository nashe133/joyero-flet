import flet as ft
import requests
import time

def main(page: ft.Page):
    page.title = "Joyero Pro - Control Total"
    page.theme_mode = "dark"
    page.horizontal_alignment = "center"
    page.scroll = "auto"

    # --- VARIABLES DE ESTADO ---
    state = {
        "dolar": 965.0,  # Valor inicial por defecto
        "oro_usd": 0.0,
        "plata_usd": 0.0,
        "onza": 31.1035
    }

    # --- ELEMENTOS DE UI ---
    txt_dolar_valor = ft.Text(f"${state['dolar']}", size=30, weight="bold", color="green")
    txt_oro_clp = ft.Text("$ 0", size=35, weight="bold", color="amber")
    txt_plata_clp = ft.Text("$ 0", size=35, weight="bold", color="bluegrey")
    
    status_dolar = ft.Text("Dólar estático", size=12, italic=True)
    status_metales = ft.Text("Metales sin cargar", size=12, italic=True)

    # --- LÓGICA: ACTUALIZAR INTERFAZ ---
    def refrescar_calculos():
        if state["oro_usd"] > 0:
            oro_gramo = (state["oro_usd"] * state["dolar"]) / state["onza"]
            txt_oro_clp.value = f"$ {int(oro_gramo):,}".replace(",", ".")
            
        if state["plata_usd"] > 0:
            plata_gramo = (state["plata_usd"] * state["dolar"]) / state["onza"]
            txt_plata_clp.value = f"$ {int(plata_gramo):,}".replace(",", ".")
        
        page.update()

    # --- MOTOR 1: SÓLO DÓLAR ---
    def actualizar_dolar(e):
        status_dolar.value = "Consultando dólar..."
        page.update()
        try:
            # Usamos una API de dólar que no suele dar problemas de CORS
            res = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()
            state["dolar"] = float(res['rates']['CLP'])
            txt_dolar_valor.value = f"${state['dolar']}"
            status_dolar.value = f"Dólar actualizado: {time.strftime('%H:%M')}"
            refrescar_calculos()
        except:
            status_dolar.value = "Error al traer dólar. Se mantiene valor previo."
        page.update()

    # --- MOTOR 2: SÓLO METALES (TU API DE GETDATA) ---
    def actualizar_metales(e):
        status_metales.value = "Consultando metales..."
        page.update()
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Referer': 'https://silverprice.org/'
            }
            # Plata
            r_xag = requests.get('https://data-asg.goldprice.org/GetData/USD-XAG/1', headers=headers, timeout=8)
            # Oro
            r_xau = requests.get('https://data-asg.goldprice.org/GetData/USD-XAU/1', headers=headers, timeout=8)

            state["plata_usd"] = float(r_xag.text.split(',')[0])
            state["oro_usd"] = float(r_xau.text.split(',')[0])
            
            status_metales.value = f"Metales actualizados: {time.strftime('%H:%M')}"
            refrescar_calculos()
        except:
            status_metales.value = "Error API Metales. Reintente."
        page.update()

    # --- DISEÑO ---
    page.add(
        ft.Card(
            content=ft.Container(
                padding=15,
                content=ft.Column([
                    ft.Text("VALOR DÓLAR (CLP)", size=12),
                    txt_dolar_valor,
                    ft.ElevatedButton("ACTUALIZAR DÓLAR", icon="money", on_click=actualizar_dolar),
                    status_dolar
                ], horizontal_alignment="center")
            )
        ),
        ft.Divider(height=20, color="transparent"),
        ft.Card(
            content=ft.Container(
                padding=15,
                content=ft.Column([
                    ft.Text("METALES (PRECIO GRAMO CLP)", size=12),
                    ft.Row([
                        ft.Column([ft.Text("ORO 24K", color="amber"), txt_oro_clp], horizontal_alignment="center"),
                        ft.Column([ft.Text("PLATA PURA", color="bluegrey"), txt_plata_clp], horizontal_alignment="center"),
                    ], alignment="spaceAround"),
                    ft.ElevatedButton("ACTUALIZAR METALES", icon="refresh", on_click=actualizar_metales),
                    status_metales
                ], horizontal_alignment="center")
            )
        )
    )

ft.app(target=main)
