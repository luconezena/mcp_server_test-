def calcola_zuccheri_totali(saccarosio, destrosio, glucosio, frutta_fresca, percentuale_zucchero_frutta):
    zuccheri_frutta = (percentuale_zucchero_frutta / 100) * frutta_fresca
    return saccarosio + destrosio + glucosio + zuccheri_frutta

def calcola_grassi_totali(latte, panna, frutta_secca, latte_scremato_polvere):
    return (latte * 0.035) + (panna * 0.35) + (frutta_secca * 0.60) + (latte_scremato_polvere * 0.01)

def calcola_slm(latte, panna, latte_scremato_polvere):
    return (latte * 0.09) + (panna * 0.06) + (latte_scremato_polvere * 0.96)

def calcola_solidi_totali(slm, zuccheri, grassi, neutro_5, frutta_fresca, percentuale_solidi_frutta, latte_scremato_polvere):
    solidi_frutta = (percentuale_solidi_frutta / 100) * frutta_fresca
    return slm + zuccheri + grassi + (neutro_5 * 1.0) + solidi_frutta + (latte_scremato_polvere * 0.97)

def calcola_pod(saccarosio, destrosio, glucosio, latte, panna, latte_scremato_polvere):
    pod_zuccheri = (saccarosio * 1.0) + (destrosio * 0.7) + (glucosio * 0.21)
    lattosio = (latte * 0.045) + (panna * 0.035) + (latte_scremato_polvere * 0.50)
    pod_lattosio = lattosio * 0.16  # Lattosio POD circa 16%
    pod_totale = pod_zuccheri + pod_lattosio
    return pod_totale

def calcola_pac(saccarosio, destrosio, glucosio, latte, panna, latte_scremato_polvere):
    pac_zuccheri = (saccarosio * 1.0) + (destrosio * 1.9) + (glucosio * 0.45)
    lattosio = (latte * 0.045) + (panna * 0.035) + (latte_scremato_polvere * 0.50)
    pac_lattosio = lattosio * 1.0  # Lattosio PAC 100% circa
    pac_totale = pac_zuccheri + pac_lattosio
    return pac_totale