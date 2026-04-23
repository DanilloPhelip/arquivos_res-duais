import flet as ft

def main(page: ft.Page):
    page.title = "Assistente Virtual FAPE"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Ícone na barra superior (favicon)
    page.favicon = "assets/favicon.ico"   # coloque seu ícone na pasta "assets"

    # Função chamada ao clicar no botão
    def abrir_link(e):
        page.launch_url("https://targetless-loralee-unlobed.ngrok-free.dev")

    # Ícone central na janela
    icone_central = ft.Image(
        src="assets/favicon.ico",
        width=100,
        height=100
    )

    # Botão centralizado
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

    # Adiciona ícone e botão no centro da tela
    page.add(
        icone_central,
        ft.Text("Bem-vindo ao Assistente Virtual FAPE!", size=20, weight=ft.FontWeight.BOLD),
        botao
    )

# Executa o app como web
ft.app(
    target=main,
    
)