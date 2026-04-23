import flet as ft
import nltk
import numpy as np
import re
from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import wordnet

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

# Substitui palavras por sinônimos na resposta
def substituir_por_sinonimos(texto):
    palavras = nltk.word_tokenize(texto)
    nova_resposta = []

    for palavra in palavras:
        sinonimos = wordnet.synsets(palavra)
        if sinonimos:
            # Seleciona o primeiro sinônimo encontrado
            sinonimo = sinonimos[0].lemmas()[0].name()
            nova_resposta.append(sinonimo)
        else:
            nova_resposta.append(palavra)

    return " ".join(nova_resposta)

# Gera resposta com base em similaridade semântica e sinônimos
def gerar_resposta_com_sinonimos(pergunta):
    vetor_pergunta = modelo_bert.encode([pergunta], convert_to_tensor=True)
    similaridades = cosine_similarity(vetor_pergunta, vetores_perguntas)
    score = float(np.max(similaridades))
    idx = int(np.argmax(similaridades))

    print(f"[DEBUG BERT] Similaridade: {score:.2f}")

    if score < 0.65:
        return None

    return substituir_por_sinonimos(respostas[idx])

# Função para aprendizado dinâmico
def aprender(pergunta, resposta):
    with open(arquivo, "a", encoding="utf-8") as file:
        file.write(f"\n\nPergunta: {pergunta.strip()}\nResposta: {resposta.strip()}")
    carregar_base()
    global vetores_perguntas
    vetores_perguntas = vetorizar_perguntas()

# Interface gráfica com Flet
def main(page: ft.Page):
    page.title = "Chatbot IA com BERT"
    page.scroll = "auto"

    chat = ft.Column(auto_scroll=True)
    input_field = ft.TextField(label="Digite sua pergunta...", expand=True)
    btn_send = ft.ElevatedButton("Enviar")

    def enviar_mensagem(e):
        pergunta = input_field.value
        if not pergunta.strip():
            return
        chat.controls.append(ft.Text(f"Você: {pergunta}", size=16, weight="bold"))
        resposta = gerar_resposta_com_sinonimos(pergunta)
        if resposta:
            chat.controls.append(ft.Text(f"Bot: {resposta}", size=16))
        else:
            def confirmar_resposta(ev):
                nova_resposta = ensinar_field.value
                aprender(pergunta, nova_resposta)
                chat.controls.append(ft.Text(f"Bot: Obrigado! Aprendi a resposta.", size=16))
                page.dialog.open = False
                page.update()

            ensinar_field = ft.TextField(label="Qual a resposta correta?")
            dialog = ft.AlertDialog(
                title=ft.Text("Não sei responder 😅"),
                content=ensinar_field,
                actions=[
                    ft.TextButton("Salvar", on_click=confirmar_resposta),
                ],
            )
            page.dialog = dialog
            dialog.open = True

        input_field.value = ""
        page.update()

    btn_send.on_click = enviar_mensagem
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("Chatbot Inteligente com BERT", size=24, weight="bold"),
                chat,
                ft.Row([input_field, btn_send])
            ]),
            padding=20
        )
    )

ft.app(target=main)

