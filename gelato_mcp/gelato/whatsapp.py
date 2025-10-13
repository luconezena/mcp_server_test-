from .models import Item, Parametri, TargetRange

def format_whatsapp(ricetta: list[Item], p: Parametri, t: TargetRange, stile: str, lingua: str = "it") -> str:
    lines = []
    if lingua == "en":
        lines.append(f"*Artisanal Gelato – Style:* {stile}")
        lines.append("")
        lines.append("*Recipe:*")
        for it in ricetta:
            lines.append(f"- {it.nome}: {it.grammi:.1f} g")
        lines.append("")
        lines.append("*Parameters (%):*")
        lines.append(f" sugars: {p.zuccheri_totali_pct:.1f} | fats: {p.grassi_totali_pct:.1f} | MSNF: {p.slm_pct:.1f}")
        lines.append(f" total solids: {p.solidi_totali_pct:.1f} | POD: {p.pod_pct:.1f} | PAC: {p.pac_pct:.1f}")
        lines.append("")
        lines.append("*Reference ranges (%):*")
        lines.append(f" sugars: {t.zuccheri_totali_pct} | fats: {t.grassi_totali_pct} | MSNF: {t.slm_pct}")
        lines.append(f" total solids: {t.solidi_totali_pct} | POD: {t.pod_pct} | PAC: {t.pac_pct}")
    else:
        lines.append(f"*Gelato Artigianale – Stile:* {stile}")
        lines.append("")
        lines.append("*Ricetta:*")
        for it in ricetta:
            lines.append(f"- {it.nome}: {it.grammi:.1f} g")
        lines.append("")
        lines.append("*Parametri (%):*")
        lines.append(f" zuccheri: {p.zuccheri_totali_pct:.1f} | grassi: {p.grassi_totali_pct:.1f} | SLM: {p.slm_pct:.1f}")
        lines.append(f" solidi totali: {p.solidi_totali_pct:.1f} | POD: {p.pod_pct:.1f} | PAC: {p.pac_pct:.1f}")
        lines.append("")
        lines.append("*Valori di riferimento (%):*")
        lines.append(f" zuccheri: {t.zuccheri_totali_pct} | grassi: {t.grassi_totali_pct} | SLM: {t.slm_pct}")
        lines.append(f" solidi totali: {t.solidi_totali_pct} | POD: {t.pod_pct} | PAC: {t.pac_pct}")

    return "\n".join(lines)
