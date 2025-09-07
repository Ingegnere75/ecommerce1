from django import forms
from django.utils.safestring import mark_safe
from .colori import COLORI_NOMI  # Assicurati che il file colori.py sia nello stesso modulo

class ColoriPreviewWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ''
        selected = [v.strip() for v in value.split(',')] if isinstance(value, str) else []

        html = '<div id="color-picker" style="display:flex;flex-wrap:wrap;gap:8px; margin-bottom: 10px;">'
        for nome, hexval in COLORI_NOMI.items():
            active_class = 'selected' if nome in selected else ''
            html += f'''
                <div class="color-swatch {active_class}" data-nome="{nome}" title="{nome}"
                    style="background-color: {hexval};
                           width: 30px;
                           height: 30px;
                           border-radius: 50%;
                           cursor: pointer;
                           border: 2px solid #ccc;
                           display: inline-block;">
                </div>
            '''
        html += '</div>'

        html += f'''
        <input type="hidden" name="{name}" id="colori-hidden" value="{','.join(selected)}" />
        <script>
        document.addEventListener("DOMContentLoaded", function() {{
            const swatches = document.querySelectorAll(".color-swatch");
            const hiddenInput = document.getElementById("colori-hidden");

            swatches.forEach(swatch => {{
                swatch.addEventListener("click", () => {{
                    swatch.classList.toggle("selected");
                    const selected = Array.from(document.querySelectorAll(".color-swatch.selected"))
                                          .map(el => el.getAttribute("data-nome"));
                    hiddenInput.value = selected.join(", ");
                }});
            }});
        }});
        </script>

        <style>
            .color-swatch.selected {{
                border: 3px solid black !important;
                box-shadow: 0 0 5px black;
            }}
        </style>
        '''
        return mark_safe(html)
