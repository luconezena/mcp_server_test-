from typing import Dict, List
from .models import Item

# Preset semplici per test. In futuro potresti caricarli da file/json.
PRESETS: Dict[str, List[Item]] = {
    "fior_di_latte_base": [
        Item(nome="latte intero", grammi=650),
        Item(nome="panna 35%", grammi=120),
        Item(nome="saccarosio", grammi=120),
        Item(nome="destrosio", grammi=30),
        Item(nome="glucosio DE21", grammi=30),
        Item(nome="latte scremato in polvere", grammi=40),
        Item(nome="stabilizzanti", grammi=4),
    ],
    "cioccolato_base": [
        Item(nome="latte intero", grammi=500),
        Item(nome="panna 35%", grammi=140),
        Item(nome="saccarosio", grammi=110),
        Item(nome="destrosio", grammi=40),
        Item(nome="glucosio DE21", grammi=30),
        Item(nome="latte scremato in polvere", grammi=30),
        Item(nome="cacao amaro", grammi=60),
        Item(nome="stabilizzanti", grammi=4),
    ],
}
