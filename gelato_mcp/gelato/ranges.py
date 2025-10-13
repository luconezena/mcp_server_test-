from .models import TargetRange

DEFAULT_SOFT = TargetRange(
    zuccheri_totali_pct=[16, 22],
    grassi_totali_pct=[6, 12],
    slm_pct=[9, 11],
    solidi_totali_pct=[32, 42],
    pod_pct=[14, 21],
    pac_pct=[22, 27],
)

DEFAULT_CLASSICO = DEFAULT_SOFT  # puoi differenziare in futuro
