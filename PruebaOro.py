import flet as ft
import requests

def main(page: ft.Page):
    page.title = "Joyero Pro"
    page.theme_mode = "dark"
    page.horizontal_alignment = "center"
    page.scroll = "auto"

    ONZA_A_GRAMO = 31.1035
    
    leyes = {
        "Oro 22K": 0.9167, "Oro 18K": 0.750, "Oro 14K": 0.583, 
        "Plata 950": 0.950, "Plata 925": 0.925
    }

    txt_oro = ft.Text("$ 0", size=40, weight="bold", color="amber")
    txt_plata = ft.Text("$ 0", size=40, weight="bold", color="bluegrey")
    
    col_oro = ft.Column(horizontal_alignment="center")
    col_plata = ft.Column(horizontal_alignment="center")
    
    txt_status = ft.Text("Listo para cotizar", size=12)

    def obtener_datos(e=None):
        txt_status.value = "Consultando mercado..."
        page.update()
        try:
            # URL original + Proxy para evitar el bloqueo CORS en la web
            url_original = "https://data-asg.goldprice.org/dbXRates/CLP"
            proxy_url = "https://api.allorigins.win/get?url=" + url_original
            
            r = requests.get(proxy_url, timeout=15)
            
            if r.status_code == 200:
                # El proxy mete la respuesta en un campo 'contents' como texto
                import json
                raw_data = r.json()
                data = json.loads(raw_data['contents'])
                
                item = data['items'][0]
                
                p_oro = item['xauPrice'] / ONZA_A_GRAMO
                p_plata = item['xagPrice'] / ONZA_A_GRAMO

                txt_oro.value = f"$ {int(p_oro):,}".replace(",", ".")
                txt_plata.value = f"$ {int(p_plata):,}".replace(",", ".")
                
                col_oro.controls.clear()
                col_plata.controls.clear()
                
                for nombre, mult in leyes.items():
                    base = p_oro if "Oro" in nombre else p_plata
                    valor = f"$ {int(base * mult):,}".replace(",", ".")
                    color = "amber" if "Oro" in nombre else "bluegrey"
                    
                    if "Oro" in nombre:
                        col_oro.controls.append(ft.Text(f"{nombre}: {valor}", color=color, size=18))
                    else:
                        col_plata.controls.append(ft.Text(f"{nombre}: {valor}", color=color, size=18))
                
                txt_status.value = "Actualizado con éxito"
            page.update()
        except Exception as ex:
            txt_status.value = "Error: Intente de nuevo"
            page.update()

    page.add(
        ft.Text("PRECIOS EN VIVO (1g)", size=25, weight="bold"),
        ft.Divider(),
        ft.Text("ORO 24K", size=16, color="amber"),
        txt_oro,
        col_oro,
        ft.Divider(height=30),
        ft.Text("PLATA PURA", size=16, color="bluegrey"),
        txt_plata,
        col_plata,
        ft.Divider(height=30),
        ft.ElevatedButton("ACTUALIZAR AHORA", on_click=obtener_datos),
        txt_status
    )
    
    obtener_datos()

ft.app(target=main)
