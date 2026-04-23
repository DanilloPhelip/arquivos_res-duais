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

    # Carrega dados do arquivo original
    with open(arquivo, "r", encoding="utf-8") as file:
        conteudo = file.read()
        blocos = re.findall(r"Pergunta:\s*(.*?)\s*Resposta:\s*(.*?)(?=Pergunta:|$)", conteudo, re.DOTALL)
        for pergunta, resposta in blocos:
            tokens = nltk.word_tokenize(pergunta)
            pergunta_limpa = " ".join([lemmatizer.lemmatize(w.lower()) for w in tokens])
            perguntas.append(pergunta_limpa)
            respostas.append(resposta.strip())

    # Carrega dados do arquivo conversa_salva.txt
    try:
        with open("conversa_salva.txt", "r", encoding="utf-8") as file:
            conteudo = file.read()
            blocos = re.findall(r"Pergunta:\s*(.*?)\s*Resposta:\s*(.*?)(?=Pergunta:|$)", conteudo, re.DOTALL)
            for pergunta, resposta in blocos:
                tokens = nltk.word_tokenize(pergunta)
                pergunta_limpa = " ".join([lemmatizer.lemmatize(w.lower()) for w in tokens])
                perguntas.append(pergunta_limpa)
                respostas.append(resposta.strip())
    except FileNotFoundError:
        print("[AVISO] Arquivo conversa_salva.txt não encontrado. Será criado ao salvar novas conversas.")

# Vetoriza perguntas incluindo as do histórico salvo
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
        resposta = None
    else:
        resposta = respostas[idx]

    # Salva a conversa após a emissão da resposta
    salvar_conversa(pergunta, resposta)
    
    return resposta
    
def salvar_conversa(pergunta, resposta, arquivo="conversa_salva.txt"):
    with open(arquivo, "a", encoding="utf-8") as f:
        f.write(f"Pergunta: {pergunta}\n")
        f.write(f"Resposta: {resposta}\n")
        
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
    page.window_favicon = "favicon.ico"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    



    
    historico_output = ft.ListView(expand=True, auto_scroll=True, reverse=False)
    page.add(ft.Column(controls=[historico_output], alignment=ft.MainAxisAlignment.END, expand=10, width=400,))
    
    pergunta_input = ft.TextField(
        label="Digite sua pergunta...", 
        width=270,
        multiline=True,
        border=ft.colors.BLUE_500
    )

    btn_enviar = ft.ElevatedButton(content=ft.Icon(name=ft.icons.SEND, size=25, color="blue"))

    def mostrar_resposta_animada(resposta):
        resposta_container = ft.Container(
            content=ft.Text(text_align=ft.TextAlign.LEFT, color="white", weight=ft.FontWeight.BOLD, selectable=True),
            bgcolor="Black", padding=15, border_radius=15, expand=False, width=300
        )

        loading_message = ft.Text(value="", expand=True, text_align=ft.TextAlign.LEFT, color="Grey11")
        
        historico_output.controls.append(ft.Row([loading_message]))

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
                [resposta_container
                ],
                alignment=ft.MainAxisAlignment.START
            )
        )
      

        def abrir_feedback_dialog(_):
            def fechar_dialog(e):
                dialog.open = False
                page.update()

            def salvar_feedback(e):
                try:
                    # Lendo o conteúdo do arquivo conversa salva
                    with open("conversa_salva.txt", "r", encoding="utf-8") as arquivo:
                        linhas = arquivo.readlines()

                    # Obtendo a última pergunta e resposta
                    if len(linhas) >= 2:
                        ultima_pergunta = linhas[-2].strip()
                        ultima_resposta = linhas[-1].strip()
                    else:
                        print("Arquivo de conversa não contém informações suficientes.")
                        return

                    # Obtendo o motivo do feedback
                    motivo_feedback = feedback_radio_group.value if feedback_radio_group.value else "Motivo não especificado"

                    # Salvando no arquivo de feedback
                    with open("feedback_salvo.txt", "a", encoding="utf-8") as arquivo_feedback:
                        arquivo_feedback.write(f"Pergunta: {ultima_pergunta}\n")
                        arquivo_feedback.write(f"Resposta: {ultima_resposta}\n")
                        arquivo_feedback.write(f"Motivo do feedback: {motivo_feedback}\n")
                        arquivo_feedback.write("-" * 50 + "\n")  # Separador entre registros
                    
                    print("Feedback salvo com sucesso!")
                    fechar_dialog(None)  # Fecha o diálogo após salvar o feedback

                    agradecimento_dialog = ft.AlertDialog(
                title=ft.Text("Obrigado pelo seu feedback!"),
                content=ft.Text("Sua opinião nos ajuda a melhorar."),
                actions=[ft.TextButton("Fechar", on_click=lambda _: fechar_agradecimento_dialog())]
            )

                    def fechar_agradecimento_dialog():
                        agradecimento_dialog.open = False
                        page.update()

                    page.dialog = agradecimento_dialog
                    agradecimento_dialog.open = True
                    page.update()

                
                except Exception as err:
                    print(f"Erro ao salvar o feedback: {err}")

            feedback_radio_group = ft.RadioGroup(
                content=ft.Column(
                    [
                        ft.Radio(value="Resposta incorreta", label="Resposta incorreta"),
                        ft.Radio(value="Não ficou claro", label="Não ficou claro"),
                        ft.Radio(value="Faltou detalhes", label="Faltou detalhes"),
                        ft.Radio(value="Não era o que queria", label="Não era o que eu queria"),
                        ft.Radio(value="Outro motivo", label="Outro motivo"),
                    ]
                ),
                value=None  # Nenhuma opção pré-selecionada
            )

            dialog = ft.AlertDialog(
                title=ft.Text("Por que você não gostou da resposta?"),
                content=ft.Column([feedback_radio_group], alignment=ft.MainAxisAlignment.START),
                actions=[
                    ft.TextButton("Enviar", on_click=salvar_feedback),
                    ft.TextButton("Cancelar", on_click=fechar_dialog)
                ]
            )

            page.dialog = dialog
            dialog.open = True
            page.update()

        historico_output.update()
        page.update()
        historico_output.controls.append(
            ft.Row([
                ft.Text(" "), 
                ft.IconButton(icon=ft.icons.THUMB_UP, icon_size=15, on_click=lambda _: print("Usuário gostou da resposta")),
                ft.IconButton(icon=ft.icons.THUMB_DOWN, icon_size=15, on_click=abrir_feedback_dialog)
            ], alignment="START")
        )
        historico_output.update()
   




        texto_atual = ""
        for palavra in resposta.split(" "):
            texto_atual += palavra + " "
            resposta_container.content.value = texto_atual
            resposta_container.update()
            time.sleep(0.05)

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
    
    page.add(ft.Container(
        content=ft.Row([pergunta_input, btn_enviar],),
        padding=5,
        border_radius=3,
        expand=False,
        width=360,
        bgcolor=ft.colors.BLACK,  # Alterado de "background_color" para "bgcolor"
        border=ft.border.all(1, ft.colors.BLUE_500),
        shadow=ft.BoxShadow(blur_radius=4, spread_radius=5, color=ft.colors.GREY_800)
    ))

if __name__ == "__main__":

    ft.app(target=main, port=24121, assets_dir="assets", view=ft.WEB_BROWSER, host="0.0.0.0")