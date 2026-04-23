import os
from openai import OpenAI
import flet as ft

# Inicializa o cliente OpenAI
# Usa variável de ambiente se existir, senão você pode colocar a chave direto
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or "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")

def main(page: ft.Page):
    page.title = "Chat com OpenAI"
    page.scroll = "auto"

    chat = ft.Column()
    user_input = ft.TextField(hint_text="Digite sua mensagem...", expand=True)
    
    def send_message(e):
        user_msg = user_input.value.strip()
        if not user_msg:
            return
        
        # Exibe mensagem do usuário
        chat.controls.append(ft.Text(f"Você: {user_msg}", color="blue"))
        page.update()

        # Chamada à API da OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_msg}]
        )

        bot_reply = response.choices[0].message.content
        chat.controls.append(ft.Text(f"Bot: {bot_reply}", color="green"))
        page.update()

        user_input.value = ""
        page.update()

    send_button = ft.ElevatedButton("Enviar", on_click=send_message)

    page.add(
        chat,
        ft.Row([user_input, send_button])
    )

# Para rodar em modo desktop:
ft.app(target=main)

# Se quiser rodar direto no navegador (modo web), troque por:
# ft.app(target=main, view=ft.AppView.WEB_BROWSER)