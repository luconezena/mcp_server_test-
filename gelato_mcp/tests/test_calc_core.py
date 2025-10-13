from gelato.calc_core import calcola_parametri, ribilancia
from gelato.models import Item, TargetRange

def test_ribilancia_runs():
    ricetta = [
        Item(nome="latte intero", grammi=650),
        Item(nome="panna 35%", grammi=120),
        Item(nome="saccarosio", grammi=120),
        Item(nome="destrosio", grammi=30),
        Item(nome="glucosio DE21", grammi=30),
        Item(nome="latte scremato in polvere", grammi=40),
        Item(nome="stabilizzanti", grammi=4),
    ]
    p = calcola_parametri(ricetta)
    t = TargetRange(
        zuccheri_totali_pct=[16,22], grassi_totali_pct=[6,12], slm_pct=[9,11],
        solidi_totali_pct=[32,42], pod_pct=[14,21], pac_pct=[22,27]
    )
    nuova, sugg = ribilancia(ricetta, p, t)
    assert len(nuova) == len(ricetta)
