import asyncio
import flet as ft

def main(page: ft.Page):
    page.title = "Assistente Virtual FAPE"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.colors.WHITE
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.favicon = "assets/icon.ico"
  

    # Ícone central já visível ao abrir
    icone_central = ft.Image(
        src="assets/aplash.png",
        width=200,
        height=200,
        opacity=1,              # já aparece
        scale=1.0,              # tamanho normal
        animate_opacity=800,
        animate_scale=800
    )

    texto = ft.Text(
        "Bem-vindo ao Assistente Virtual FAPE!",
        size=20,
        weight=ft.FontWeight.BOLD
    )

    async def animar():
        # Pulsa duas vezes
        for _ in range(2):
            icone_central.scale = 1.2
            await page.update_async()
            await asyncio.sleep(0.4)
            icone_central.scale = 1.0
            await page.update_async()
            await asyncio.sleep(0.4)

        # Cresce até ocupar a janela e desaparece
        icone_central.scale = 5.0   # cresce bastante
        icone_central.opacity = 0   # desaparece aos poucos
        await page.update_async()

    async def abrir_link(e):
        # Dispara animação ao clicar
        
        page.run_task(animar)
        # Abre o link
        await asyncio.sleep(2.0)
        page.launch_url("https://targetless-loralee-unlobed.ngrok-free.dev")
        await asyncio.sleep(1.0)
    botao = ft.ElevatedButton(
        text="Entrar no Assistente Virtual FAPE",
        on_click=abrir_link,
        bgcolor=ft.colors.BLUE,
        color=ft.colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=20
        )
    )

    page.add(icone_central, texto, botao)

ft.app(target=main)
