
import os, tempfile, datetime
from flask import Flask, render_template, request, send_file, redirect, url_for
from branding.branding_core import generate_kit_zip, KEYWORD_THEMES

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    niches = list(KEYWORD_THEMES.keys())
    return render_template("index.html", niches=niches)

@app.route("/gerar", methods=["POST"])
def gerar():
    name = request.form.get("brand_name","").strip()
    tagline = request.form.get("tagline","").strip()
    niche = request.form.get("niche","luxo")
    audience = request.form.get("audience","").strip()
    style = request.form.get("style","").strip()
    colors = request.form.get("colors","").strip()

    # Build a compact brief text for the generator
    brief_parts = []
    if name: brief_parts.append(f'"{name}"')
    if niche: brief_parts.append(niche)
    if style: brief_parts.append(style)
    if audience: brief_parts.append(f"público: {audience}")
    if colors: brief_parts.append(f"cores: {colors}")
    if tagline: brief_parts.append(f"tagline: {tagline}")
    brief = " — ".join(brief_parts) or 'Marca de luxo — tagline: Beleza com propósito'

    tmp_zip = os.path.join(tempfile.gettempdir(), f"kit_{datetime.datetime.now().timestamp()}.zip")
    zip_path, meta = generate_kit_zip(brief, tmp_zip)

    # Show result view with download link and palette preview
    return render_template("result.html", meta=meta, download_url=url_for('baixar', path=os.path.basename(zip_path)))

@app.route("/download/<path:path>")
def baixar(path):
    full = os.path.join(tempfile.gettempdir(), path)
    if not os.path.exists(full):
        return redirect(url_for("index"))
    return send_file(full, as_attachment=True, download_name="branding_kit.zip", mimetype="application/zip")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # ⚠️ usar a porta do Render
    app.run(host="0.0.0.0", port=port)
