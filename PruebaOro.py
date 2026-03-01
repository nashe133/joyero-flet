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

    # --- ELEMENTOS DE INTERFAZ ---
    txt_oro = ft.Text("$ 0", size=40, weight="bold", color="amber")
    txt_plata = ft.Text("$ 0", size=40, weight="bold", color="bluegrey")
    
    # Contenedores para las listas
    col_oro = ft.Column(horizontal_alignment="center")
    col_plata = ft.Column(horizontal_alignment="center")
    
    txt_status = ft.Text("Actualizando...", size=12)

    def obtener_datos(e=None):
        txt_status.value = "Consultando..."
        page.update()
        try:
            url = "https://data-asg.goldprice.org/dbXRates/CLP"
            headers = {'User-Agent': 'okhttp/4.12.0'}
            r = requests.get(url, headers=headers, timeout=15)
            
            if r.status_code == 200:
                data = r.json()
                item = data['items'][0]
                
                # Precios base
                p_oro = item['xauPrice'] / ONZA_A_GRAMO
                p_plata = item['xagPrice'] / ONZA_A_GRAMO

                txt_oro.value = f"$ {int(p_oro):,}".replace(",", ".")
                txt_plata.value = f"$ {int(p_plata):,}".replace(",", ".")
                
                col_oro.controls.clear()
                col_plata.controls.clear()
                
                # Llenar listas
                for nombre, mult in leyes.items():
                    base = p_oro if "Oro" in nombre else p_plata
                    valor = f"$ {int(base * mult):,}".replace(",", ".")
                    color = "amber" if "Oro" in nombre else "bluegrey"
                    
                    if "Oro" in nombre:
                        col_oro.controls.append(ft.Text(f"{nombre}: {valor}", color=color, size=18))
                    else:
                        col_plata.controls.append(ft.Text(f"{nombre}: {valor}", color=color, size=18))
                
                txt_status.value = "Sincronizado correctamente"
            page.update()
        except:
            txt_status.value = "Error de conexión"
            page.update()

    # --- CONSTRUCCIÓN DE LA PANTALLA ÚNICA ---
    page.add(
        ft.Text("PRECIOS EN VIVO (1g)", size=25, weight="bold"),
        ft.Divider(),
        
        # Bloque Oro
        ft.Text("ORO 24K", size=16, color="amber"),
        txt_oro,
        col_oro,
        
        ft.Divider(height=30),
        
        # Bloque Plata
        ft.Text("PLATA PURA", size=16, color="bluegrey"),
        txt_plata,
        col_plata,
        
        ft.Divider(height=30),
        
        ft.ElevatedButton("ACTUALIZAR AHORA", on_click=obtener_datos),
        txt_status
    )
    
    obtener_datos()

ft.app(target=main)
