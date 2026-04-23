import flet as ft
import nltk
import numpy as np
import re
from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import threading
import time

# Downloads necessários
nltk.download("punkt")
nltk.download("wordnet")
nltk.download("omw-1.4")

# Variáveis globais
lemmatizer = WordNetLemmatizer()
perguntas = []
respostas = []
arquivo = "Banco_de_dados.txt"

# Carrega modelo BERT
modelo_bert = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Carrega perguntas e respostas do arquivo
def carregar_base():
    perguntas.clear()
    respostas.clear()
    with open(arquivo, "r", encoding="utf-8") as file:
        conteudo = file.read()
        blocos = re.findall(r"Pergunta:\s*(.*?)\s*Resposta:\s*(.*?)(?=Pergunta:|$)", conteudo, re.DOTALL)
        for pergunta, resposta in blocos:
            tokens = nltk.word_tokenize(pergunta)
            pergunta_limpa = " ".join([lemmatizer.lemmatize(w.lower()) for w in tokens])
            perguntas.append(pergunta_limpa)
            respostas.append(resposta.strip())

# Vetoriza perguntas usando BERT
def vetorizar_perguntas():
    return modelo_bert.encode(perguntas, convert_to_tensor=True)

# Inicializa base e vetores
carregar_base()
vetores_perguntas = vetorizar_perguntas()

# Gera resposta com base em similaridade semântica
def gerar_resposta(pergunta):
    vetor_pergunta = modelo_bert.encode([pergunta], convert_to_tensor=True)
    similaridades = cosine_similarity(vetor_pergunta, vetores_perguntas)
    score = float(np.max(similaridades))
    idx = int(np.argmax(similaridades))

    print(f"[DEBUG BERT] Similaridade: {score:.2f}")

    if score < 0.65:
        return None
    return respostas[idx]

# Função para obter sugestões de perguntas
def gerar_sugestoes(pergunta):
    tokens = nltk.word_tokenize(pergunta)
    pergunta_limpa = " ".join([lemmatizer.lemmatize(w.lower()) for w in tokens])
    vetor_pergunta = modelo_bert.encode([pergunta_limpa], convert_to_tensor=True)
    similaridades = cosine_similarity(vetor_pergunta, vetores_perguntas)[0]
    melhores_indices = np.argsort(similaridades)[-3:][::-1]
    return [perguntas[i] for i in melhores_indices]

# Interface gráfica com Flet
def main(page: ft.Page):
    page.title = "Chatbot Inteligente"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    historico_output = ft.ListView(expand=True, auto_scroll=True, reverse=False)
    page.add(ft.Column(controls=[historico_output], alignment=ft.MainAxisAlignment.END, expand=10, width=800,))
    
    pergunta_input = ft.TextField(
        label="Digite sua pergunta...",
        width=600,
        multiline=True
    )

    btn_enviar = ft.ElevatedButton(content=ft.Icon(name=ft.icons.SEND, size=40, color="blue"))

    def mostrar_resposta_animada(resposta):
        resposta_container = ft.Container(
            content=ft.Text("", text_align=ft.TextAlign.LEFT, color="white", weight=ft.FontWeight.BOLD, selectable=True),
            bgcolor="Black", padding=15, border_radius=15, expand=False, width=400
        )

        loading_message = ft.Text(value="", expand=True, text_align=ft.TextAlign.LEFT, color="Grey11")
        icon = ft.Image(src="robo.gif", width=50, border_radius=20)
        historico_output.controls.append(ft.Row([icon, loading_message]))

        historico_output.update()
        page.update()

        for _ in range(2):
            for i in range(1):
                loading_message.value += "⬤"
                historico_output.update()
                page.update()
                time.sleep(0.1)

            for i in range(2):
                loading_message.value += "⬤"
                historico_output.update()
                page.update()
                time.sleep(0.1)

            for i in range(1):
                loading_message.value += "⬤"
                historico_output.update()
                page.update()
                time.sleep(0.1)

            for i in range(2):
                loading_message.value = loading_message.value[:-1] + "●"
                historico_output.update()
                page.update()
                time.sleep(0.1)

            for i in range(2):
                loading_message.value = loading_message.value[:+2] + "●"
                historico_output.update()
                page.update()
                time.sleep(0.1)

            for i in range(2):
                loading_message.value = loading_message.value[:+1] + "●"
                historico_output.update()
                page.update()
                time.sleep(0.1)

            loading_message.value = ""

        historico_output.controls.pop()
        historico_output.update()

        historico_output.controls.append(
            ft.Row(
                [
                    ft.Image(src='robo.gif', width=50, border_radius=20),
                    resposta_container
                ],
                alignment=ft.MainAxisAlignment.START
            )
        )

        historico_output.update()
        page.update()

        texto_atual = ""
        for palavra in resposta.split(" "):
            texto_atual += palavra + " "
            resposta_container.content.value = texto_atual
            resposta_container.update()
            time.sleep(0.005)

            if "\n" in palavra:
                historico_output.scroll_to(offset=9999)
                historico_output.update()
                page.update()

        historico_output.scroll_to(offset=9999)
        historico_output.update()
        page.update()

    import textwrap

    def formatar_texto(texto, limite=50):
        """Adiciona quebras de linha automaticamente quando o texto ultrapassa o limite de caracteres"""
        return "\n".join(textwrap.wrap(texto, width=limite))

    def enviar_mensagem(e):
        pergunta = pergunta_input.value
        if not pergunta.strip():
            return

        # Limpa o campo de digitação
        pergunta_input.value = ""
        page.update()

        # Desativa o botão de envio
        btn_enviar.disabled = True
        page.update()

        pergunta_formatada = formatar_texto(pergunta)  # Aplica a formatação da quebra de linha

        historico_output.controls.append(ft.Row([ft.Text("                                      ")]))
        historico_output.controls.append(
            ft.Row(
                [
                    ft.Container(
                        content=ft.Text(
                            value=pergunta_formatada,  # Agora exibindo com quebras de linha automáticas
                            text_align=ft.TextAlign.LEFT,
                            color="white",
                            weight=ft.FontWeight.BOLD,
                            selectable=True,
                        ),
                        bgcolor="blue",
                        padding=15,
                        border_radius=20,
                    )
                ],
                alignment=ft.MainAxisAlignment.END
            )
        )

        historico_output.controls.append(ft.Row([ft.Text("                                      ")]))

        resposta = gerar_resposta(pergunta)
        if resposta:
            mostrar_resposta_animada(resposta)
        else:
            mensagem_erro = ft.Text(
                value="Desculpe, não encontrei uma resposta adequada. Talvez você possa tentar uma destas perguntas:",
                color="red",
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.LEFT
            )

            sugestoes_perguntas = gerar_sugestoes(pergunta)

            sugestoes_botoes = [
                ft.ElevatedButton(
                    text=pergunta_sugestiva,
                    on_click=lambda e, p=pergunta_sugestiva: perguntar_novamente(p)
                )
                for pergunta_sugestiva in sugestoes_perguntas
            ]

            historico_output.controls.append(mensagem_erro)
            historico_output.controls.extend(sugestoes_botoes)
            historico_output.update()
            page.update()

        # Aguarda 5 segundos e reativa o botão de envio
        def reativar_botao():
            btn_enviar.disabled = False
            page.update()

        threading.Timer(5.0, reativar_botao).start()

    def perguntar_novamente(pergunta):
        pergunta_input.value = pergunta
        page.update()


    btn_enviar.on_click = enviar_mensagem
    page.add(ft.Row([pergunta_input, btn_enviar], alignment=ft.MainAxisAlignment.CENTER))

ft.app(target=main)