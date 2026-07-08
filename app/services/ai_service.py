import os

import requests

from app.models.inventory_model import InventoryModel
from app.models.product_translation_model import ProductTranslationModel
from app.models.setting_model import SettingModel


def _get_setting(key: str, default: str = "") -> str:
    s = SettingModel.query.filter_by(setting_key=key).first()
    return s.setting_value if s else default


def _build_context(inventory_id: int) -> dict | None:
    inv = InventoryModel.query.get(inventory_id)
    if not inv:
        return None
    prod = inv.product
    col = inv.collection
    lang = inv.language
    card_type = col.card_type if col else None

    # Find translation matching inventory language
    t_name = ''
    t_alter = ''
    if prod and prod.translations:
        match = None
        if lang:
            match = next((t for t in prod.translations if t.language_id == lang.id), None)
        t = match or prod.translations[0]
        t_name = t.name or ''
        t_alter = t.name_alter or ''

    # Build the info line: "bw9 1 アメタマ (Surskit)"
    info_parts = []
    if col and col.code:
        info_parts.append(col.code)
    if prod and prod.product_number:
        info_parts.append(prod.product_number)
    if t_name:
        info_parts.append(t_name)
    info_line = " ".join(info_parts)
    if t_alter:
        info_line += f" ({t_alter})"

    parts = []
    if info_line:
        parts.append(f"Línea de identificación: {info_line}")
    if prod:
        parts.append(f"Número de producto: {prod.product_number or ''}")
    if col:
        parts.append(f"Colección: {col.code or ''}")
    if card_type:
        parts.append(f"Tipo: {card_type.name or ''}")
    if lang:
        parts.append(f"Idioma: {lang.name or ''}")

    return {
        "info_line": info_line,
        "context_str": "\n".join(parts),
        "lang_name": lang.name if lang else "",
    }


def generate_caption(inventory_id: int) -> str:
    ctx = _build_context(inventory_id)
    print(f"[AI] CONTEXT for inventory {inventory_id}:\n{ctx}\n")
    if not ctx:
        return ""

    ig_handle = _get_setting("ai.instagram.handle", "@syndael_")

    prompt = (
        "Eres un coleccionista de Pokémon TCG. "
        "Escribe un texto para Instagram sobre el siguiente producto.\n\n"
        "Importante: NO suenes a inteligencia artificial. Escribe como una persona real, "
        "con lenguaje natural, sin frases hechas.\n\n"
        "El texto debe incluir:\n"
        "1. Presentación sencilla del producto (qué carta, de qué colección)\n"
        "2. OBLIGATORIO: un dato curioso o interés sobre el Pokémon o la carta\n"
        "3. Una línea en blanco\n"
        f"4. La línea de identificación exacta: \"{ctx['info_line']}\"\n"
        "5. Otra línea en blanco\n"
        "6. 8 hashtags variados con esta estructura obligatoria:\n"
        "   - #Pokemon (siempre)\n"
        "   - #PokemonTCG (siempre)\n"
        "   - #NombreDelPokemon (ej: #Volcarona, #Pikachu)\n"
        "   - #CodigoColeccion (ej: #bw9, #swsh1)\n"
        "   - #Idioma (ej: #Español, #Japones, #Ingles)\n"
        "   - #Coleccionismo\n"
        "   - 2 tags más libres relacionados\n\n"
        "Reglas:\n"
        "- NO añadas firma ni usuario de Instagram al final\n"
        "- NO repitas el nombre del Pokémon fuera de la línea de identificación\n"
        "- Usa el idioma del producto para la descripción\n\n"
        f"Contexto del producto:\n{ctx['context_str']}\n"
    )

    api_key = _get_setting("ai.gemini.api_key", os.environ.get("GEMINI_API_KEY", ""))
    if not api_key:
        return _fallback_text(ctx)

    try:
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.8, "maxOutputTokens": 400},
        }
        print(f"[AI] PROMPT:\n{prompt}\n")
        resp = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={api_key}",
            headers={"Content-Type": "application/json"},
            json=body,
            timeout=30,
        )
        print(f"[AI] RAW RESPONSE:\n{resp.text}\n")
        resp.raise_for_status()
        data = resp.json()
        candidate = data["candidates"][0]
        parts = candidate["content"]["parts"]
        text = parts[0]["text"].strip() if parts else ""
        print(f"[AI] PARSED TEXT: {text}")
        return text
    except Exception as e:
        print(f"[AI] Gemini error: {e}")
        return _fallback_text(ctx)


def _fallback_text(ctx: dict) -> str:
    tags = ["#PokemonTCG", "#Coleccionismo", "#TCG", "#CartaPokemon"]
    if ctx.get("lang_name") and "Español" in ctx["lang_name"]:
        tags.append("#Español")
    return (
        f"Un clásico que no podía faltar en la colección.\n\n"
        f"{ctx['info_line']}\n\n"
        f"{' '.join(tags)}"
    )
