
# Glow Branding Kit — Flask (Render Ready)

App web que gera **logos (SVG/PNG)**, **paleta de cores** e **guia de marca (PDF)** a partir de um briefing simples.

## Rodar local
```
pip install -r requirements.txt
python app.py
```

## Deploy no Render
1. Suba este projeto para um repositório no GitHub
2. Em https://render.com → New → Web Service → Conecte o repositório
3. Ambiente: Python
4. Build Command: (deixe em branco)
5. Start Command:
```
gunicorn app:app
```
6. Deploy

> Observação: este app usa `cairosvg` para converter SVG em PNG. O Render instala automaticamente as dependências via pip.
