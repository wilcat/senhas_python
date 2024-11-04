-- Criação da tabela de senhas
CREATE TABLE IF NOT EXISTS senha (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero INTEGER,
    guiche INTEGER,
    servico TEXT,
    horario TEXT,
    status TEXT
);
