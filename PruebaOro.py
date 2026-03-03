import flet as ft
import requests
import time

def main(page: ft.Page):
    # --- VARIABLES DE CONTROL ---
    DOLAR_MANUAL = 960.0 
    ONZA_A_GRAMO = 31.1035

    # --- UI ---
    txt_oro = ft.Text("$ 0", size=35, color="amber", weight="bold")
    txt_plata = ft.Text("$ 0", size=35, color="bluegrey", weight="bold")
    txt_status = ft.Text("Listo para actualizar", size=12)

    def actualizar_metales_por_separado(e):
        txt_status.value = "Petición 1: Obteniendo Oro..."
        txt_status.color = "white"
        page.update()

        try:
            # HEADERS LIMPIOS PARA CADA PETICIÓN
            header_base = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': '*/*'
            }

            # --- PETICIÓN 1: ORO (XAU) ---
            # Se ejecuta, se cierra y se procesa antes de empezar la siguiente
            res_oro = requests.get(
                'https://data-asg.goldprice.org/GetData/USD-XAU/1', 
                headers=header_base, 
                timeout=10
            )
            oro_usd = float(res_oro.text.split(',')[0])
            
            # Pausa técnica de milisegundos para asegurar separación de hilos
            time.sleep(0.5)

            txt_status.value = "Petición 2: Obteniendo Plata..."
            page.update()

            # --- PETICIÓN 2: PLATA (XAG) ---
            # Petición nueva, sin conexión previa con la de oro
            res_plata = requests.get(
                'https://data-asg.goldprice.org/GetData/USD-XAG/1', 
                headers=header_base, 
                timeout=10
            )
            plata_usd = float(res_plata.text.split(',')[0])

            # --- CÁLCULOS FINALES ---
            oro_clp = (oro_usd * DOLAR_MANUAL) / ONZA_A_GRAMO
            plata_clp = (plata_usd * DOLAR_MANUAL) / ONZA_A_GRAMO

            txt_oro.value = f"$ {int(oro_clp):,}".replace(",", ".")
            txt_plata.value = f"$ {int(plata_clp):,}".replace(",", ".")
            
            txt_status.value = f"Actualizado: {time.strftime('%H:%M:%S')}"
            txt_status.color = "green"

        except Exception as ex:
            txt_status.value = "Error en la secuencia de peticiones"
            txt_status.color = "red"
        
        page.update()

    # Botón independiente para el Dólar (puedes añadir su lógica aparte)
    btn_dolar = ft.ElevatedButton("DÓLAR (MANUAL: 960)", icon="money_off", disabled=True)

    page.add(
        ft.Column([
            ft.Text("ACTUALIZACIÓN SECUENCIAL", weight="bold"),
            btn_dolar,
            ft.Divider(),
            ft.Row([
                ft.Column([ft.Text("ORO"), txt_oro], horizontal_alignment="center"),
                ft.Column([ft.Text("PLATA"), txt_plata], horizontal_alignment="center"),
            ], alignment="spaceAround"),
            ft.ElevatedButton("ACTUALIZAR METALES (1 a 1)", icon="refresh", on_click=actualizar_metales_por_separado),
            txt_status
        ], horizontal_alignment="center", spacing=20)
    )

ft.app(target=main)
