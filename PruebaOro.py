import flet as ft

import requests



def main(page: ft.Page):

    page.title = "Joyero Pro: Cotizador y Calculadora"

    page.theme_mode = ft.ThemeMode.DARK

    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    page.scroll = ft.ScrollMode.AUTO

    page.padding = 20



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

    

    in_gramos = ft.TextField(label="Gramos", width=120, border_color="amber")

    dd_ley = ft.Dropdown(

        label="Ley",

        width=180,

        options=[ft.dropdown.Option(l) for l in leyes.keys()]

    )

    col_historial = ft.Column(spacing=10, width=400) # Ancho fijo para evitar texto vertical

    txt_status = ft.Text("Cargando...", size=12, italic=True)



    def obtener_datos():

        try:

            url = "https://data-asg.goldprice.org/dbXRates/CLP"

            headers = {'User-Agent': 'okhttp/4.12.0'}

            response = requests.get(url, headers=headers, timeout=10)

            

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

                    col.controls.append(ft.Text(f"{nombre} (g): {valor}", size=18, color=color_txt))

                

                txt_status.value = f"Actualizado: {data['date']}"

            page.update()

        except:

            txt_status.value = "Error de conexión"

            page.update()



    def crear_item_historial(titulo, sub, color):

        def borrar(e):

            col_historial.controls.remove(fila)

            page.update()



        # ARREGLO DEL ICONO: Usamos la propiedad 'icon' explícitamente

        fila = ft.ListTile(

            leading=ft.Icon(name=ft.icons.CIRCLE, color=color, size=15),

            title=ft.Text(titulo, size=16),

            subtitle=ft.Text(sub, weight="bold"),

            trailing=ft.IconButton(icon=ft.icons.DELETE, on_click=borrar),

            bgcolor="white10",

        )

        col_historial.controls.insert(0, fila)



    def calcular(e):

        if not in_gramos.value or not dd_ley.value: return

        try:

            peso = float(in_gramos.value.replace(",", "."))

            ley_sel = dd_ley.value

            multiplicador = leyes[ley_sel]

            base = precios_gramo["oro"] if "Oro" in ley_sel else precios_gramo["plata"]

            color_item = "amber" if "Oro" in ley_sel else "bluegrey"

            total = int(peso * base * multiplicador)

            total_str = f"$ {total:,}".replace(",", ".")

            crear_item_historial(f"{peso}g de {ley_sel}", f"Total: {total_str}", color_item)

            in_gramos.value = ""

            page.update()

        except: pass



    # --- PANELES ---

    panel_vivo = ft.Column([

        ft.Text("EN VIVO (1g PURO)", size=20, weight="bold"),

        ft.Divider(),

        ft.Text("ORO 24K", color="amber"), txt_oro_v,

        ft.Text("PLATA PURA", color="bluegrey"), txt_plata_v,

    ], horizontal_alignment="center", visible=True)



    panel_kila = ft.Column([

        ft.Text("VALOR GRAMO POR LEY", size=20, weight="bold"),

        ft.Divider(),

        col_kila_oro,

        ft.Divider(height=10, color="transparent"),

        col_kila_plata,

    ], horizontal_alignment="center", visible=False)



    panel_calc = ft.Column([

        ft.Text("CALCULADORA", size=20, weight="bold"),

        ft.Row([in_gramos, dd_ley], alignment="center"),

        ft.ElevatedButton("CALCULAR", icon=ft.icons.ADD, on_click=calcular),

        ft.Divider(),

        ft.Row([

            ft.Text("HISTORIAL"),

            ft.TextButton("Limpiar Todo", on_click=lambda _: [col_historial.controls.clear(), page.update()])

        ], alignment="spaceBetween", width=400),

        col_historial

    ], horizontal_alignment="center", visible=False)



    # NAVEGACIÓN

    def ir_vivo(e):

        panel_vivo.visible, panel_kila.visible, panel_calc.visible = True, False, False

        page.update()

    def ir_kila(e):

        panel_vivo.visible, panel_kila.visible, panel_calc.visible = False, True, False

        page.update()

    def ir_calc(e):

        panel_vivo.visible, panel_kila.visible, panel_calc.visible = False, False, True

        page.update()



    page.add(

        ft.Row([

            ft.TextButton("EN VIVO", on_click=ir_vivo),

            ft.TextButton("KILATAJE", on_click=ir_kila),

            ft.TextButton("CALCULAR", on_click=ir_calc),

        ], alignment="center"),

        ft.Divider(),

        ft.Container(panel_vivo, padding=10),

        ft.Container(panel_kila, padding=10),

        ft.Container(panel_calc, padding=10),

        txt_status

    )

    obtener_datos()



ft.app(target=main)