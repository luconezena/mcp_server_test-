from typing import List, Tuple, Dict
from .models import Item, Parametri, TargetRange

# --- Helpers ------------------------------------------------------------------------------------
def _kg_totali(ricetta: List[Item]) -> float:
    tot = sum(i.grammi for i in ricetta) / 1000.0
    return round(tot, 3)

def _sum_by(names: List[str], lookup: Dict[str, float]) -> float:
    return sum(lookup.get(n, 0.0) for n in names)

def _map_ricetta(ricetta: List[Item]) -> Dict[str, float]:
    # normalizza i nomi a lowercase per confronto semplice
    m: Dict[str, float] = {}
    for it in ricetta:
        m[it.nome.lower()] = m.get(it.nome.lower(), 0.0) + it.grammi
    return m

# --- Calcoli (adattati da Gelato Artigianale) ---------------------------------------------------
def calcola_parametri(ricetta: List[Item]) -> Parametri:
    m = _map_ricetta(ricetta)
    totale_g = sum(m.values()) or 1.0

    saccarosio = m.get("saccarosio", 0.0)
    destrosio = m.get("destrosio", 0.0)
    glucosio = m.get("glucosio de21", 0.0) or m.get("glucosio", 0.0)
    frutta_fresca = m.get("frutta fresca", 0.0)
    frutta_secca = m.get("frutta secca", 0.0)
    latte = m.get("latte intero", 0.0)
    panna = m.get("panna 35%", 0.0)
    lsp = m.get("latte scremato in polvere", 0.0)
    # Parametri fissi (come in gelato_ui)
    perc_zucchero_frutta = 5.3
    perc_solidi_frutta = 10.0

    # Neutro 5: 5 g/kg
    neutro_5 = (totale_g / 1000.0) * 5.0

    # Zuccheri totali (g)
    zuccheri_frutta = (perc_zucchero_frutta / 100.0) * frutta_fresca
    zuccheri_g = saccarosio + destrosio + glucosio + zuccheri_frutta

    # Grassi totali (g)
    grassi_g = (latte * 0.035) + (panna * 0.35) + (frutta_secca * 0.60) + (lsp * 0.01)

    # SLM (g)
    slm_g = (latte * 0.09) + (panna * 0.06) + (lsp * 0.96)

    # Solidi totali (g)
    solidi_frutta = (perc_solidi_frutta / 100.0) * frutta_fresca
    solidi_totali_g = slm_g + zuccheri_g + grassi_g + (neutro_5 * 1.0) + solidi_frutta + (lsp * 0.97)

    # Lattosio (g) e POD/PAC
    lattosio_g = (latte * 0.045) + (panna * 0.035) + (lsp * 0.50)
    pod_g = (saccarosio * 1.0) + (destrosio * 0.7) + (glucosio * 0.21) + (lattosio_g * 0.16)
    pac_g = (saccarosio * 1.0) + (destrosio * 1.9) + (glucosio * 0.45) + (lattosio_g * 1.0)

    # Conversione in % sul totale miscela
    to_pct = lambda g: (g / totale_g) * 100.0
    return Parametri(
        zuccheri_totali_pct=round(to_pct(zuccheri_g), 3),
        grassi_totali_pct=round(to_pct(grassi_g), 3),
        slm_pct=round(to_pct(slm_g), 3),
        solidi_totali_pct=round(to_pct(solidi_totali_g), 3),
        pod_pct=round(to_pct(pod_g), 3),
        pac_pct=round(to_pct(pac_g), 3),
    )

def dentro_range_map(p: Parametri, t: TargetRange) -> Dict[str, bool]:
    def _in(val, rng): return rng[0] <= val <= rng[1]
    return {
        "zuccheri_totali_pct": _in(p.zuccheri_totali_pct, t.zuccheri_totali_pct),
        "grassi_totali_pct": _in(p.grassi_totali_pct, t.grassi_totali_pct),
        "slm_pct": _in(p.slm_pct, t.slm_pct),
        "solidi_totali_pct": _in(p.solidi_totali_pct, t.solidi_totali_pct),
        "pod_pct": _in(p.pod_pct, t.pod_pct),
        "pac_pct": _in(p.pac_pct, t.pac_pct),
    }

def dentro_range(p: Parametri, t: TargetRange) -> bool:
    m = dentro_range_map(p, t)
    return all(m.values())

def ribilancia(ricetta: List[Item], p: Parametri, t: TargetRange) -> Tuple[List[Item], list[str]]:
    # PLACEHOLDER: Regoline semplici per demo UI.
    # Esempio: se zuccheri% > max, riduci saccarosio di 5g; se < min, aumenta 5g.
    suggerimenti = []
    nuova = [Item(**i.model_dump()) for i in ricetta]

    def _find(name):
        for it in nuova:
            if it.nome.lower() == name.lower():
                return it
        return None

    def _tweak(name, delta):
        it = _find(name)
        if it:
            it.grammi = max(0, it.grammi + delta)
            return True
        return False

    # Zuccheri (usa saccarosio/destrosio in modo grossolano)
    if p.zuccheri_totali_pct > t.zuccheri_totali_pct[1]:
        if _tweak("saccarosio", -5): suggerimenti.append("Ridotto saccarosio di 5 g")
    elif p.zuccheri_totali_pct < t.zuccheri_totali_pct[0]:
        if _tweak("destrosio", +5): suggerimenti.append("Aumentato destrosio di 5 g")

    # Grassi (usa panna)
    if p.grassi_totali_pct > t.grassi_totali_pct[1]:
        if _tweak("panna 35%", -5): suggerimenti.append("Ridotta panna di 5 g")
    elif p.grassi_totali_pct < t.grassi_totali_pct[0]:
        if _tweak("panna 35%", +5): suggerimenti.append("Aumentata panna di 5 g")

    # SLM / Solidi (usa latte scremato in polvere)
    if p.slm_pct < t.slm_pct[0]:
        if _tweak("latte scremato in polvere", +3): suggerimenti.append("Aumentato LSP di 3 g")

    # Ritorna proposta (anche se magari non perfetta).
    return nuova, suggerimenti

def nota_base50(ricetta_finale: List[Item]) -> str:
    kg = _kg_totali(ricetta_finale)
    suggerita = round(kg * 5, 1)
    return f"Base 50: 5 g/kg → {suggerita} g su {kg} kg totali."

def alerts_speciali(ricetta: List[Item]) -> list[str]:
    """Avvisi speciali stile Android: LSP > 12% del peso totale."""
    m = _map_ricetta(ricetta)
    totale_g = sum(i.grammi for i in ricetta) or 1.0
    lsp = m.get("latte scremato in polvere", 0.0)
    alerts: list[str] = []
    if lsp > 0.12 * totale_g:
        alerts.append("Il latte scremato in polvere supera il 12% del peso totale")
    return alerts
