import os

import requests

from app.models.inventory_model import InventoryModel
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
    condition = inv.condition
    extra_type = inv.extra_type

    t_name = ''
    t_alter = ''
    if prod and prod.translations:
        match = None
        if lang:
            match = next((t for t in prod.translations if t.language_id == lang.id), None)
        t = match or prod.translations[0]
        t_name = t.name or ''
        t_alter = t.name_alter or ''

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
    if t_name:
        parts.append(f"Nombre de la carta: {t_name}")
    if t_alter:
        parts.append(f"Nombre alternativo: {t_alter}")
    if prod:
        parts.append(f"Número de producto: {prod.product_number or ''}")
    if col:
        parts.append(f"Colección: {col.code or ''} - {col.name if hasattr(col, 'name') else ''}")
    if card_type:
        parts.append(f"Juego/Tipo de carta: {card_type.name or ''}")
    if extra_type:
        parts.append(f"Variante: {extra_type.name or ''}")
    if condition:
        parts.append(f"Estado: {condition.name or ''}")
    if lang:
        parts.append(f"Idioma: {lang.name or ''}")
    if inv.is_sealed:
        parts.append("Producto sellado: Sí")
    if inv.notes and inv.notes.strip():
        parts.append(f"Notas del inventario: {inv.notes.strip()}")

    return {
        "info_line": info_line,
        "context_str": "\n".join(parts),
        "lang_name": lang.name if lang else "",
        "card_name": t_name,
        "card_name_alt": t_alter,
        "card_type_name": card_type.name if card_type else "",
        "has_card_name": bool(t_name),
    }


def generate_caption(inventory_id: int, user_text: str = "") -> str:
    ctx = _build_context(inventory_id)
    print(f"[AI] CONTEXT for inventory {inventory_id}:\n{ctx}\n")
    if not ctx:
        return ""

    if user_text:
        prompt = (
            "Eres un experto en TCG y coleccionismo. Tu trabajo es COMPLEMENTAR el texto "
            "del usuario con un dato curioso, relevante o interesante sobre la carta o Pokémon "
            "en cuestión. NO repitas lo que ya dice el usuario.\n\n"
            f"El usuario ha escrito:\n\"{user_text}\"\n\n"
            "Basándote en el contexto del producto, genera:\n"
            "1. Un complemento breve (2-3 líneas máximo) que aporte un dato curioso o relevante: "
            "puede ser sobre el Pokémon (lore, rareza, historia competitiva, diseño, aparición en "
            "anime/juegos), sobre la carta en sí (valor, rareza, colección), o sobre el estado "
            "del producto si es relevante.\n"
            "2. NO uses frases genéricas como 'ideal para coleccionistas'.\n"
            "3. Sé dinámico: si es un Pokémon habla del Pokémon, si es un objeto/trainer/energy "
            "habla de su uso en el juego, si es sellado menciónalo.\n\n"
            "Después del complemento, añade una línea en blanco y copia EXACTAMENTE "
            f"esta línea tal cual, sin modificar nada:\n\"{ctx['info_line']}\"\n"
            "Luego añade otra línea en blanco y genera 7-9 hashtags.\n"
            "Los hashtags DEBEN incluir:\n"
            f"  - #Syndael_ (OBLIGATORIO, siempre al final)\n"
            "  - #Pokemon o el hashtag del juego según corresponda\n"
            "  - #PokemonTCG si es Pokémon\n"
            "  - #NombreDelPokemon si hay un Pokémon (ej: #Pikachu, #Volcarona)\n"
            "  - #CodigoColeccion (ej: #bw9, #swsh1)\n"
            "  - #Idioma (ej: #Español, #Japones, #Ingles)\n"
            "  - #Coleccionismo\n\n"
            "Reglas de formato IMPORTANTÍSIMAS:\n"
            "- NO incluyas el texto del usuario en tu respuesta.\n"
            "- NO uses prefijos como 'Complemento:' o 'Dato curioso:'.\n"
            "- La primera línea de tu respuesta será el complemento directamente.\n"
            "- NO uses emojis.\n"
            "- Escribe en el idioma correspondiente al producto.\n\n"
            f"Contexto del producto:\n{ctx['context_str']}\n"
        )
    else:
        prompt = (
            "Eres un experto en TCG y coleccionismo. Genera una sugerencia breve "
            "para acompañar una publicación de Instagram sobre el siguiente producto.\n\n"
            "Genera:\n"
            "1. Un texto breve (2-3 líneas máximo) con un dato curioso o relevante "
            "sobre la carta/Pokémon: lore del personaje, rareza, historia competitiva, "
            "diseño, aparición en anime/juegos, valor de colección, o estado del producto.\n"
            "2. NO uses frases genéricas como 'ideal para coleccionistas'.\n"
            "3. Sé dinámico según el tipo de producto: Pokémon, Trainer, Energy, sellado, etc.\n\n"
            "Después del texto, añade una línea en blanco y copia EXACTAMENTE "
            f"esta línea tal cual, sin modificar nada:\n\"{ctx['info_line']}\"\n"
            "Luego añade otra línea en blanco y genera 7-9 hashtags.\n"
            "Los hashtags DEBEN incluir:\n"
            f"  - #Syndael_ (OBLIGATORIO, siempre al final)\n"
            "  - #Pokemon o el hashtag del juego según corresponda\n"
            "  - #PokemonTCG si es Pokémon\n"
            "  - #NombreDelPokemon si hay un Pokémon (ej: #Pikachu, #Volcarona)\n"
            "  - #CodigoColeccion (ej: #bw9, #swsh1)\n"
            "  - #Idioma (ej: #Español, #Japones, #Ingles)\n"
            "  - #Coleccionismo\n\n"
            "Reglas de formato IMPORTANTÍSIMAS:\n"
            "- La primera línea de tu respuesta será la sugerencia directamente.\n"
            "- NO uses prefijos como 'Sugerencia:' o 'Dato curioso:'.\n"
            "- NO uses emojis.\n"
            "- Escribe en el idioma correspondiente al producto.\n\n"
            f"Contexto del producto:\n{ctx['context_str']}\n"
        )

    api_key = _get_setting("ai.gemini.api_key", os.environ.get("GEMINI_API_KEY", ""))
    if not api_key:
        return _fallback_text(ctx, user_text)

    try:
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.8, "maxOutputTokens": 400},
        }
        print(f"[AI] PROMPT:\n{prompt}\n")
        resp = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={api_key}",
            headers={"Content-Type": "application/json"},
            json=body,
            timeout=30,
        )
        print(f"[AI] RAW RESPONSE:\n{resp.text}\n")
        resp.raise_for_status()
        data = resp.json()
        candidate = data["candidates"][0]
        parts = candidate["content"]["parts"]
        ai_text = parts[0]["text"].strip() if parts else ""
        print(f"[AI] PARSED TEXT: {ai_text}")

        if user_text:
            return f"{user_text}\n\nIA:\n{ai_text}"
        return f"IA:\n{ai_text}"
    except Exception as e:
        print(f"[AI] Gemini error: {e}")
        return _fallback_text(ctx, user_text)


def _fallback_text(ctx: dict, user_text: str = "") -> str:
    tags = ["#PokemonTCG", "#Coleccionismo", "#TCG", "#Syndael_"]
    if ctx.get("lang_name") and "Español" in ctx["lang_name"]:
        tags.append("#Español")
    if ctx.get("has_card_name") and ctx["card_name"]:
        name_tag = ctx["card_name"].replace(" ", "").replace("-", "").replace(".", "")
        tags.insert(2, f"#{name_tag}")
    suggestion = "Una carta con gran valor para cualquier colección."
    if ctx.get("card_name"):
        suggestion = f"Un dato curioso sobre {ctx['card_name']}: esta carta pertenece a una de las colecciones más icónicas del TCG."

    info_line = ctx.get("info_line", "")

    if user_text:
        return f"{user_text}\n\nIA:\n{suggestion}\n\n{info_line}\n\n{' '.join(tags)}"
    return f"IA:\n{suggestion}\n\n{info_line}\n\n{' '.join(tags)}"
