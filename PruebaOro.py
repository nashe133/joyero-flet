import flet as ft
import requests
import json

def main(page: ft.Page):
    page.title = "Joyero Pro"
    page.theme_mode = "dark"
    page.horizontal_alignment = "center"
    page.scroll = "auto"

    ONZA_A_GRAMO = 31.1035
    
    # He reincorporado todas tus leyes originales
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

    txt_oro = ft.Text("$ 0", size=40, weight="bold", color="amber")
    txt_plata = ft.Text("$ 0", size=40, weight="bold", color="bluegrey")
    
    col_oro = ft.Column(horizontal_alignment="center", spacing=2)
    col_plata = ft.Column(horizontal_alignment="center", spacing=2)
    
    txt_status = ft.Text("Listo", size=12)

    def obtener_datos(e=None):
        txt_status.value = "Consultando mercado..."
        page.update()
        try:
            # Proxy para evitar errores CORS en versión Web
            url_original = "https://data-asg.goldprice.org/dbXRates/CLP"
            proxy_url = "https://api.allorigins.win/get?url=" + url_original
            
            r = requests.get(proxy_url, timeout=15)
            
            if r.status_code == 200:
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
                    es_oro = "Oro" in nombre
                    base = p_oro if es_oro else p_plata
                    valor = f"$ {int(base * mult):,}".replace(",", ".")
                    color = "amber" if es_oro else "bluegrey"
                    
                    texto_ley = ft.Text(f"{nombre}: {valor}", color=color, size=18)
                    
                    if es_oro:
                        col_oro.controls.append(texto_ley)
                    else:
                        col_plata.controls.append(texto_ley)
                
                txt_status.value = "Actualizado con éxito"
            page.update()
        except:
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
