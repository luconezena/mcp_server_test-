import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from .gelato_calculations import calcola_zuccheri_totali, calcola_grassi_totali, calcola_slm, calcola_solidi_totali, calcola_pod, calcola_pac
from .traduzioni import traduzioni
from .traduzioni2 import descrizioni_ingredienti
import json
import webbrowser
import urllib.parse
import sys

class GelatoApp(toga.App):
    def startup(self):
        self.lingua_corrente = "🇮🇹 Italiano"
        self.dati_inseriti = False  # Flag per controllare se ci sono dati inseriti

        # Creazione del contenitore principale con ScrollView
        self.scroll_container = toga.ScrollContainer(style=Pack(flex=1))
        self.main_box = toga.Box(style=Pack(direction=COLUMN, padding=15, background_color="#FDF8F1"))
        self.scroll_container.content = self.main_box

        # Selezione della lingua
        self.lingua_selector = toga.Selection(
            items=list(traduzioni.keys()),
            on_change=self.cambia_lingua,
            style=Pack(margin=10)
        )
        self.main_box.add(self.lingua_selector)

        # Lista degli ingredienti
        self.ingredienti_nomi = [
            "Latte", "Panna", "Latte Scremato Polvere", "Saccarosio",
            "Destrosio", "Glucosio", "Frutta Secca", "Frutta Fresca", "Inulina"
        ]

        # Dizionari per memorizzare gli input e le label
        self.inputs = {}
        self.label_widgets = {}

        # Creazione dei campi di input per ogni ingrediente
        for ingrediente in self.ingredienti_nomi:
            box = toga.Box(style=Pack(direction=ROW, margin=10))
            label = toga.Label("", style=Pack(flex=1, font_size=14, color="#463F3A"))  # Usiamo flex=1 per la label
            input = toga.TextInput(
                placeholder=traduzioni[self.lingua_corrente]["placeholder"],
                style=Pack(width=100, margin_left=10, flex=1),
                on_change=self.controlla_dati_inseriti
            )
            
            # Aggiungi l'icona personalizzata
            icon_path = "resources/mipmap/ingredienti" if sys.platform == "android" else "resources/icons/ingredienti.png"
            icon = toga.Icon(icon_path)
            info_button = toga.Button(
                icon=icon,
                on_press=lambda widget, ingrediente=ingrediente: self.mostra_info_ingrediente(ingrediente),
                style=Pack(margin_left=5, margin_right=0, width=30, height=30)
            )
            
            # Memorizza gli input e le label nei dizionari
            self.inputs[ingrediente] = input
            self.label_widgets[ingrediente] = label
            
            # Aggiungi la label, l'input e il pulsante di informazione al box
            box.add(label)
            box.add(input)
            box.add(info_button)
            self.main_box.add(box)

        # Stile per i pulsanti
        btn_style = Pack(margin=5, padding=10, background_color="#D4A373", color="white", flex=1)

        # Creazione dei pulsanti
        self.btn_calcola = toga.Button(on_press=self.calcola, style=btn_style)
        self.btn_salva = toga.Button(on_press=self.salva_ricetta, style=btn_style, enabled=False)
        self.btn_carica = toga.Button(on_press=self.carica_ricetta, style=btn_style)
        self.btn_condividi = toga.Button(on_press=self.condividi_ricetta, style=btn_style, enabled=False)

        # Prima riga: Calcola e Condividi
        prima_riga = toga.Box(style=Pack(direction=ROW, margin=10))
        prima_riga.add(self.btn_calcola)
        prima_riga.add(self.btn_condividi)

        # Seconda riga: Salva e Carica
        seconda_riga = toga.Box(style=Pack(direction=ROW, margin=10))
        seconda_riga.add(self.btn_salva)
        seconda_riga.add(self.btn_carica)

        # Aggiungi le righe dei pulsanti al contenitore principale
        self.main_box.add(prima_riga)
        self.main_box.add(seconda_riga)

        # Area per visualizzare i risultati
        self.result_area = toga.Box(style=Pack(direction=COLUMN, margin=10, padding=10, background_color="#FFFDF9"))
        self.main_box.add(self.result_area)

        # Aggiungi un pulsante per la guida in-app
        self.btn_guida = toga.Button(
            text=traduzioni[self.lingua_corrente]["guida"],
            on_press=self.mostra_guida,
            style=Pack(margin=10, background_color="#A8D5BA", color="white")
        )
        self.main_box.add(self.btn_guida)

        # Finestra principale
        self.main_window = toga.MainWindow()
        self.main_window.content = self.scroll_container  # Usiamo ScrollContainer come contenuto principale
        self.cambia_lingua(None)  # Imposta la lingua iniziale
        self.main_window.show()

    def cambia_lingua(self, widget):
        """Cambia la lingua dell'interfaccia utente."""
        self.lingua_corrente = self.lingua_selector.value
        self.main_window.title = traduzioni[self.lingua_corrente]["titolo"]

        # Aggiorna le label degli ingredienti
        for ingrediente in self.ingredienti_nomi:
            traduzione_label = traduzioni[self.lingua_corrente]['ingredienti'][ingrediente]
            self.label_widgets[ingrediente].text = f"{traduzione_label} (g):"

        # Aggiorna i testi dei pulsanti
        self.btn_calcola.text = traduzioni[self.lingua_corrente]["calcola"]
        self.btn_salva.text = traduzioni[self.lingua_corrente]["salva_ricetta"]
        self.btn_carica.text = traduzioni[self.lingua_corrente]["carica_ricetta"]
        self.btn_condividi.text = traduzioni[self.lingua_corrente]["condividi"]
        self.btn_guida.text = traduzioni[self.lingua_corrente]["guida"]

        # Aggiorna i placeholder
        for input in self.inputs.values():
            input.placeholder = traduzioni[self.lingua_corrente]["placeholder"]

    def controlla_dati_inseriti(self, widget):
        """Abilita i pulsanti Salva e Condividi se ci sono dati inseriti."""
        self.dati_inseriti = any(float(v.value or 0) > 0 for v in self.inputs.values())
        self.btn_salva.enabled = self.dati_inseriti
        self.btn_condividi.enabled = self.dati_inseriti

    def mostra_guida(self, widget):
        """Mostra una finestra di dialogo con la guida in-app."""
        guida = traduzioni[self.lingua_corrente]["guida_testo"]
        self.main_window.info_dialog(traduzioni[self.lingua_corrente]["guida_titolo"], guida)

    def mostra_info_ingrediente(self, ingrediente):
        """Mostra una finestra di dialogo con le informazioni sull'ingrediente."""
        descrizione = descrizioni_ingredienti[self.lingua_corrente][ingrediente]
        self.main_window.info_dialog(ingrediente, descrizione)

    def calcola(self, widget):
        """Calcola il bilanciamento della ricetta."""
        try:
            valori = {k: float(v.value or 0) for k, v in self.inputs.items()}
        except ValueError:
            self.main_window.info_dialog("Errore", traduzioni[self.lingua_corrente]["errore_input"])
            return

        peso_totale = sum(valori.values())
        if peso_totale == 0:
            self.main_window.info_dialog("Errore", traduzioni[self.lingua_corrente]["errore_peso_zero"])
            return

        neutro_5 = (peso_totale / 1000) * 5

        # Controllo per il latte scremato in polvere
        latte_scremato_polvere = valori["Latte Scremato Polvere"]
        if latte_scremato_polvere > 0.12 * peso_totale:
            avviso = traduzioni[self.lingua_corrente]["avviso_latte_scremato"]
            self.main_window.info_dialog("Avviso", avviso)

        zuccheri = calcola_zuccheri_totali(valori["Saccarosio"], valori["Destrosio"], valori["Glucosio"], valori["Frutta Fresca"], 5.3)
        grassi = calcola_grassi_totali(valori["Latte"], valori["Panna"], valori["Frutta Secca"], valori["Latte Scremato Polvere"])
        slm = calcola_slm(valori["Latte"], valori["Panna"], valori["Latte Scremato Polvere"])
        solidi_totali = calcola_solidi_totali(slm, zuccheri, grassi, neutro_5, valori["Frutta Fresca"], 10, valori["Latte Scremato Polvere"])
        pac = calcola_pac(valori["Saccarosio"], valori["Destrosio"], valori["Glucosio"], valori["Latte"], valori["Panna"], valori["Latte Scremato Polvere"])
        pod = calcola_pod(valori["Saccarosio"], valori["Destrosio"], valori["Glucosio"], valori["Latte"], valori["Panna"], valori["Latte Scremato Polvere"])

        # Definizione dei range
        ranges = {
            "zuccheri_totali": (16, 22),
            "grassi_totali": (6, 12),
            "slm": (9, 11),
            "solidi_totali": (32, 42),
            "pod": (14, 21),
            "pac": (22, 27),
        }

        # Rimuovi i risultati precedenti
        self.result_area.children.clear()

        # Funzione per aggiungere un risultato con stile
        def add_result(label, value, range_min, range_max):
            result_box = toga.Box(style=Pack(direction=ROW, margin=5))
            result_text = f"{label}: {value:.2f}% (range: {range_min}-{range_max}%)"
            result_label = toga.Label(result_text, style=Pack(font_size=14, flex=1))

            if not (range_min <= value <= range_max):
                result_label.style.color = "red"

            result_box.add(result_label)
            self.result_area.add(result_box)

        # Aggiungi i risultati
        add_result(traduzioni[self.lingua_corrente]['zuccheri_totali'], zuccheri / peso_totale * 100, *ranges["zuccheri_totali"])
        add_result(traduzioni[self.lingua_corrente]['grassi_totali'], grassi / peso_totale * 100, *ranges["grassi_totali"])
        add_result(traduzioni[self.lingua_corrente]['slm'], slm / peso_totale * 100, *ranges["slm"])
        add_result(traduzioni[self.lingua_corrente]['solidi_totali'], solidi_totali / peso_totale * 100, *ranges["solidi_totali"])
        add_result(traduzioni[self.lingua_corrente]['pod'], pod / peso_totale * 100, *ranges["pod"])
        add_result(traduzioni[self.lingua_corrente]['pac'], pac / peso_totale * 100, *ranges["pac"])

        # Aggiungi il risultato di neutro_5
        neutro_box = toga.Box(style=Pack(direction=ROW, margin=5))
        neutro_label = toga.Label(f"{traduzioni[self.lingua_corrente]['neutro_5']}: {neutro_5:.2f}g (5g/kg)", style=Pack(font_size=14))
        neutro_box.add(neutro_label)
        self.result_area.add(neutro_box)

    async def salva_ricetta(self, widget):
        """Salva la ricetta in un file JSON."""
        dialog = toga.SaveFileDialog("Salva Ricetta", suggested_filename="ricetta.json")
        file_path = await self.main_window.dialog(dialog)
        if file_path:
            with open(file_path, "w") as f:
                json.dump({k: v.value for k, v in self.inputs.items()}, f)

    async def carica_ricetta(self, widget):
        """Carica una ricetta da un file JSON."""
        dialog = toga.OpenFileDialog("Carica Ricetta", file_types=["json"])
        file_path = await self.main_window.dialog(dialog)
        if file_path:
            with open(file_path, "r") as f:
                ricetta = json.load(f)
                for k, v in ricetta.items():
                    self.inputs[k].value = v

    def condividi_ricetta(self, widget):
        """Condividi la ricetta tramite WhatsApp."""
        testo = traduzioni[self.lingua_corrente]["condividi_testo_iniziale"]
        for ingrediente, input in self.inputs.items():
            testo += f"{traduzioni[self.lingua_corrente]['ingredienti'][ingrediente]}: {input.value}g\n"

        # Aggiungi i risultati al testo
        for child in self.result_area.children:
            if isinstance(child, toga.Box):
                for widget in child.children:
                    if isinstance(widget, toga.Label):
                        testo += widget.text + "\n"

        webbrowser.open(f"https://wa.me/?text={urllib.parse.quote(testo)}")

def main():
    return GelatoApp(formal_name="Il Gelato Artigianale", app_id="com.gelato.artigianale")