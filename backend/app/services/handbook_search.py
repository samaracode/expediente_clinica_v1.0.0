"""Búsqueda ligera en el manual de usuario (handbook/) para el asistente.

El asistente usa esto para responder preguntas de "cómo se hace X en el sistema"
con los pasos reales de la interfaz, en vez de respuestas genéricas.

Enfoque (sin dependencias externas):
- Se cargan los .md del handbook una sola vez y se parten en secciones por
  encabezado (##, ###).
- Una búsqueda por palabras clave puntúa cada sección (coincidencias en el
  título pesan más que en el cuerpo) y devuelve las mejores.

No es un motor semántico, pero para un manual de ~16 capítulos con títulos
descriptivos en español es más que suficiente y no cuesta tokens de más.
"""

import os
import re
import unicodedata
from functools import lru_cache
from typing import List

# El manual vive dentro del backend (backend/app/handbook/) para que viaje
# con el despliegue. Este archivo está en backend/app/services/, así que el
# manual está un nivel arriba: app/handbook/.
_HANDBOOK_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),  # -> app/
    "handbook",
)

# "Stop words" en español que no aportan a la búsqueda.
_STOP = {
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "al",
    "a", "en", "y", "o", "u", "que", "como", "cómo", "para", "por", "con",
    "se", "su", "sus", "es", "son", "hago", "hacer", "puedo", "quiero",
    "necesito", "dar", "click", "clic", "donde", "dónde", "cuando", "cuándo",
    "mi", "me", "lo", "le", "les", "este", "esta", "esto", "sistema",
}


# Ruta del menú lateral por archivo del manual. Derivado de la tabla maestra
# del Capítulo 1 ("Cómo Acceder al Sistema"). Mapea cada capítulo a la opción
# del menú donde vive esa función, para que el asistente indique el módulo
# padre (p.ej. "ve a Clínica → Residentes"). Los nombres de archivo son
# estables, así que este mapa es confiable y no depende de la redacción.
_MENU_PATH_BY_FILE = {
    "02-panel-principal.md": "Panel principal (Dashboard)",
    "03-residentes.md": "Clínica → Residentes",
    "04-expediente-admision.md": "Clínica → Residentes → (abrir residente) → Admisión",
    "05-operacion-medicamentos.md": "Operación → Pase de medicamentos",
    "06-operacion-asistencia.md": "Operación → Asistencia",
    "07-operacion-ocupacion.md": "Operación → Ocupación",
    "08-operacion-turno.md": "Operación → Entrega de turno",
    "09-finanzas.md": "Finanzas → Resumen y morosidad",
    "10-reportes.md": "Reportes",
    "11-administracion-usuarios.md": "Administración → Usuarios",
    "12-administracion-profesionales.md": "Administración → Profesionales",
    "13-mi-perfil.md": "Mi perfil (menú de usuario, arriba a la derecha)",
}


class Section:
    __slots__ = ("chapter", "title", "body", "menu_path", "_tokens")

    def __init__(self, chapter: str, title: str, body: str, menu_path: str = ""):
        self.chapter = chapter
        self.title = title
        self.body = body
        self.menu_path = menu_path
        self._tokens = _tokenize(f"{title} {body}")


def _strip_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )


def _tokenize(text: str) -> set:
    text = _strip_accents(text.lower())
    words = re.findall(r"[a-z0-9]+", text)
    return {w for w in words if w not in _STOP and len(w) > 2}


@lru_cache(maxsize=1)
def _load_sections() -> List[Section]:
    """Carga y parte el handbook en secciones. Cacheado en memoria (una vez)."""
    sections: List[Section] = []
    if not os.path.isdir(_HANDBOOK_DIR):
        return sections

    for fname in sorted(os.listdir(_HANDBOOK_DIR)):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(_HANDBOOK_DIR, fname)
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except OSError:
            continue

        chapter_title = fname
        current_title = ""
        buf: List[str] = []

        # Ruta de menú del capítulo (módulo padre) según el mapa por archivo.
        chapter_menu_path = _MENU_PATH_BY_FILE.get(fname, "")

        def _flush():
            if current_title or buf:
                sections.append(
                    Section(
                        chapter_title,
                        current_title or chapter_title,
                        "\n".join(buf).strip(),
                        chapter_menu_path,
                    )
                )

        for line in text.splitlines():
            # El H1 (# ...) define el título del capítulo.
            if line.startswith("# "):
                chapter_title = line[2:].strip()
                continue
            # H2/H3 abren una nueva sección.
            if line.startswith("## ") or line.startswith("### "):
                _flush()
                current_title = line.lstrip("#").strip()
                buf = []
            else:
                buf.append(line)
        _flush()

    return sections


def search(query: str, max_results: int = 3, max_chars: int = 1500) -> List[dict]:
    """Devuelve las secciones del manual más relevantes para `query`.

    Cada resultado: {chapter, menu_path, title, content}. `menu_path` es la ruta
    del menú lateral ("Clínica → Residentes") para que el asistente indique el
    módulo padre. `content` se recorta a `max_chars` para no inflar el contexto.
    """
    q_tokens = _tokenize(query)
    if not q_tokens:
        return []

    scored = []
    for sec in _load_sections():
        title_tokens = _tokenize(sec.title)
        # Coincidencias en el título valen 3x; en el cuerpo, 1x.
        title_hits = len(q_tokens & title_tokens)
        body_hits = len(q_tokens & sec._tokens)
        score = title_hits * 3 + body_hits
        if score > 0:
            scored.append((score, sec))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for _, sec in scored[:max_results]:
        content = sec.body[:max_chars]
        if len(sec.body) > max_chars:
            content += "…"
        results.append(
            {
                "chapter": sec.chapter,
                "menu_path": sec.menu_path,
                "title": sec.title,
                "content": content,
            }
        )
    return results
