from flask import Flask, render_template, request, redirect, jsonify
from datetime import datetime
import sqlite3
from gtts import gTTS
import os

app = Flask(__name__)

# Conexão com o banco de dados
def connect_db():
    conn = sqlite3.connect("chamamento.db")
    return conn

# Inicialização do banco de dados
def init_db():
    conn = connect_db()
    with conn:
        with open("schema.sql") as f:
            conn.executescript(f.read())
    conn.close()

# Rota para gerar uma nova senha
@app.route("/gerar_senha", methods=["POST"])
def gerar_senha():
    servico = request.form["servico"]
    guiche = int(request.form["guiche"])
    horario = datetime.now().strftime("%H:%M:%S")

    conn = connect_db()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(MAX(numero), 0) + 1 FROM senha")
        numero = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO senha (numero, guiche, servico, horario, status) VALUES (?, ?, ?, ?, ?)",
            (numero, guiche, servico, horario, "aguardando")
        )
    return jsonify({"numero": numero, "servico": servico, "guiche": guiche, "horario": horario})

# Rota para chamar a próxima senha
@app.route("/chamar_senha/<int:guiche>", methods=["POST"])
def chamar_senha(guiche):
    conn = connect_db()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM senha WHERE status = 'aguardando' ORDER BY id LIMIT 1")
        senha = cursor.fetchone()
        if senha:
            cursor.execute("UPDATE senha SET status = 'chamado', guiche = ? WHERE id = ?", (guiche, senha[0]))
            numero, servico = senha[1], senha[3]
            gerar_audio(numero, guiche)
            return jsonify({"numero": numero, "servico": servico, "guiche": guiche})
        return jsonify({"erro": "Nenhuma senha na fila"}), 404

# Função para gerar o áudio da chamada
def gerar_audio(numero, guiche):
    texto = f"Senha {numero}, dirigir-se ao guichê {guiche}."
    audio = gTTS(text=texto, lang="pt")
    audio.save("chamada.mp3")
    os.system("mpg321 chamada.mp3")  # Executa o áudio

# Rota para exibir o painel de senhas
@app.route("/painel")
def painel():
    conn = connect_db()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT numero, guiche FROM senha WHERE status = 'chamado' ORDER BY horario DESC LIMIT 1")
        senha_atual = cursor.fetchone()
    return render_template("painel.html", senha_atual=senha_atual)

# Página inicial de seleção de serviços
@app.route("/")
def index():
    return render_template("index.html")

# Inicialização do banco de dados na primeira execução
init_db()

if __name__ == "__main__":
    app.run(debug=True)
