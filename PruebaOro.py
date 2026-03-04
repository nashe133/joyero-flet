import flet as ft
import requests
import time

def main(page: ft.Page):
    page.title = "Joyero Pro - Valores en CLP"
    page.theme_mode = "dark"
    page.horizontal_alignment = "center"
    page.scroll = "auto"
    page.padding = 20

    # --- LEYES ---
    leyes = {
        "Oro 22K": 0.9167,
        "Oro 21K": 0.900,
        "Oro 18K": 0.750,
        "Oro 14K": 0.583,
        "Oro 10K": 0.4167,
        "Plata 980": 0.980,
        "Plata 950": 0.950,
        "Plata 925": 0.925,
        "Plata 900": 0.900
    }

    # --- UI ---
    txt_dolar = ft.Text("USD/CLP: 0", size=16, color="green")
    txt_oro_raw = ft.Text("0 CLP", size=35, weight="bold", color="amber")
    txt_plata_raw = ft.Text("0 CLP", size=35, weight="bold", color="bluegrey")

    col_oro = ft.Column(horizontal_alignment="center")
    col_plata = ft.Column(horizontal_alignment="center")

    txt_status = ft.Text("Listo", size=12)

    # --- ACTUALIZAR LISTAS ---
    def actualizar_interfaz(oro_clp, plata_clp):
        col_oro.controls.clear()
        col_plata.controls.clear()

        for nombre, mult in leyes.items():
            es_oro = "Oro" in nombre
            base = oro_clp if es_oro else plata_clp
            valor_final = base * mult
            color = "amber" if es_oro else "bluegrey"

            destino = col_oro if es_oro else col_plata
            destino.controls.append(
                ft.Text(
                    f"{nombre}: ${valor_final:,.0f} CLP",
                    size=18,
                    color=color
                )
            )

        page.update()

    # --- OBTENER DATOS ---
    def obtener_datos(e=None):
        txt_status.value = "Consultando valores..."
        txt_status.color = "white"
        page.update()

        try:
            # --- DÓLAR CLP ---
            dolar_res = requests.get(
                "https://vsxapps.com/service/api/taxa/?m1=CLP&m2=USD&origem=android-app",
                timeout=10
            )
            dolar_data = dolar_res.json()
            usd_clp = float(dolar_data["TaxaInvertida"])
            txt_dolar.value = f"USD/CLP: {usd_clp:,.2f}"

            # --- ORO (USD/ONZA → CLP) ---
            oro_res = requests.get(
                "https://api.gold-api.com/price/XAU",
                timeout=10
            )
            oro_usd = float(oro_res.json()["price"])
            oro_clp = oro_usd * usd_clp
            txt_oro_raw.value = f"${oro_clp:,.0f} CLP"

            # --- PLATA (USD/ONZA → CLP) ---
            plata_res = requests.get(
                "https://api.gold-api.com/price/XAG",
                timeout=10
            )
            plata_usd = float(plata_res.json()["price"])
            plata_clp = plata_usd * usd_clp
            txt_plata_raw.value = f"${plata_clp:,.0f} CLP"

            actualizar_interfaz(oro_clp, plata_clp)

            txt_status.value = f"Actualizado: {time.strftime('%H:%M:%S')}"
            txt_status.color = "green"

        except Exception as e:
            txt_status.value = "Error al conectar con las APIs"
            txt_status.color = "red"

        page.update()

    # --- LAYOUT ---
    page.add(
        ft.Text("VALORES SPOT EN CLP", size=25, weight="bold"),
        ft.Divider(),

        txt_dolar,
        ft.Divider(),

        ft.Text("ORO (XAU) - CLP / ONZA", size=16, color="amber"),
        txt_oro_raw,
        col_oro,

        ft.Divider(height=30),

        ft.Text("PLATA (XAG) - CLP / ONZA", size=16, color="bluegrey"),
        txt_plata_raw,
        col_plata,

        ft.Divider(height=30),

        ft.ElevatedButton(
            "ACTUALIZAR DATOS",
            icon="refresh",
            on_click=obtener_datos
        ),

        txt_status
    )

    obtener_datos()

ft.app(target=main)
