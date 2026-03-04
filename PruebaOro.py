import flet as ft
import requests
import time

ONZA_TROY_GR = 31.1034768

LEYES_ORO = {
    "24K": 1.000,
    "22K": 0.916,
    "21K": 0.875,
    "20K": 0.833,
    "18K": 0.750,
    "14K": 0.585,
    "12K": 0.500,
    "10K": 0.417,
    "9K": 0.375,
}

LEYES_PLATA = {
    "999": 0.999,
    "980": 0.980,
    "950": 0.950,
    "925": 0.925,
    "900": 0.900,
    "800": 0.800,
}


def main(page: ft.Page):
    page.title = "Valores Spot en CLP"
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = "center"
    page.scroll = "auto"
    page.padding = 20

    txt_usd = ft.Text("USD/CLP: --", size=14, color="green")
    txt_status = ft.Text("", size=12)

    col_oro = ft.Column(spacing=4)
    col_plata = ft.Column(spacing=4)

    def actualizar(e=None):
        try:
            txt_status.value = "Actualizando precios..."
            txt_status.color = "white"
            page.update()

            # USD/CLP
            usd = requests.get(
                "https://vsxapps.com/service/api/taxa/?m1=CLP&m2=USD&origem=android-app",
                timeout=10,
            ).json()
            usd_clp = float(usd["TaxaInvertida"])
            txt_usd.value = f"USD/CLP: {usd_clp:,.2f}"

            # ORO
            oro_usd = requests.get(
                "https://api.gold-api.com/price/XAU", timeout=10
            ).json()["price"]
            oro_clp_gr = (oro_usd * usd_clp) / ONZA_TROY_GR

            col_oro.controls.clear()
            for k, f in LEYES_ORO.items():
                valor = oro_clp_gr * f
                col_oro.controls.append(
                    ft.Text(f"Oro {k}: {valor:,.0f} CLP / g", color="amber")
                )

            # PLATA
            plata_usd = requests.get(
                "https://api.gold-api.com/price/XAG", timeout=10
            ).json()["price"]
            plata_clp_gr = (plata_usd * usd_clp) / ONZA_TROY_GR

            col_plata.controls.clear()
            for k, f in LEYES_PLATA.items():
                valor = plata_clp_gr * f
                col_plata.controls.append(
                    ft.Text(f"Plata {k}: {valor:,.0f} CLP / g", color="bluegrey")
                )

            txt_status.value = f"Actualizado: {time.strftime('%H:%M:%S')}"
            txt_status.color = "green"

        except Exception:
            txt_status.value = "Error al conectar con las APIs"
            txt_status.color = "red"

        page.update()

    page.add(
        ft.Text("VALORES SPOT EN CLP", size=22, weight="bold"),
        ft.Divider(),
        txt_usd,
        ft.Divider(),
        ft.Text("ORO - PRECIO POR GRAMO", color="amber"),
        col_oro,
        ft.Divider(),
        ft.Text("PLATA - PRECIO POR GRAMO", color="bluegrey"),
        col_plata,
        ft.Divider(),
        ft.ElevatedButton("ACTUALIZAR DATOS", on_click=actualizar),
        txt_status,
    )

    actualizar()


ft.app(target=main)
