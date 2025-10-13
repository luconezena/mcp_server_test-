async function fetchJSON(url, options) {
    const res = await fetch(url, options);
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return await res.json();
}

function qs(id) { return document.getElementById(id); }

function getTargetFromFields() {
    return {
        zuccheri_totali_pct: [parseFloat(qs('t_zuc_min').value || 0), parseFloat(qs('t_zuc_max').value || 0)],
        grassi_totali_pct: [parseFloat(qs('t_gr_min').value || 0), parseFloat(qs('t_gr_max').value || 0)],
        slm_pct: [parseFloat(qs('t_slm_min').value || 0), parseFloat(qs('t_slm_max').value || 0)],
        solidi_totali_pct: [parseFloat(qs('t_sol_min').value || 0), parseFloat(qs('t_sol_max').value || 0)],
        pod_pct: [parseFloat(qs('t_pod_min').value || 0), parseFloat(qs('t_pod_max').value || 0)],
        pac_pct: [parseFloat(qs('t_pac_min').value || 0), parseFloat(qs('t_pac_max').value || 0)],
    };
}

function setTargetFields(t) {
    qs('t_zuc_min').value = t.zuccheri_totali_pct[0];
    qs('t_zuc_max').value = t.zuccheri_totali_pct[1];
    qs('t_gr_min').value = t.grassi_totali_pct[0];
    qs('t_gr_max').value = t.grassi_totali_pct[1];
    qs('t_slm_min').value = t.slm_pct[0];
    qs('t_slm_max').value = t.slm_pct[1];
    qs('t_sol_min').value = t.solidi_totali_pct[0];
    qs('t_sol_max').value = t.solidi_totali_pct[1];
    qs('t_pod_min').value = t.pod_pct[0];
    qs('t_pod_max').value = t.pod_pct[1];
    qs('t_pac_min').value = t.pac_pct[0];
    qs('t_pac_max').value = t.pac_pct[1];
}

function getIngredients() {
    const ids = [
        ['latte intero', 'ing_latte'],
        ['panna 35%', 'ing_panna'],
        ['latte scremato in polvere', 'ing_lsp'],
        ['saccarosio', 'ing_saccarosio'],
        ['destrosio', 'ing_destrosio'],
        ['glucosio DE21', 'ing_glucosio'],
        ['frutta secca', 'ing_frutta_secca'],
        ['frutta fresca', 'ing_frutta_fresca'],
        ['inulina', 'ing_inulina'],
        ['cacao amaro', 'ing_cacao_amaro'],
    ];
    return ids.map(([nome, id]) => ({ nome, grammi: parseFloat((qs(id).value || '').trim() || 0) }));
}

async function applyPreset(name) {
    const items = await fetchJSON(`/debug/preset/${encodeURIComponent(name)}`);
    const map = Object.fromEntries(items.map(i => [i.nome.toLowerCase(), i.grammi]));
    qs('ing_latte').value = (map['latte intero'] ?? 0);
    qs('ing_panna').value = (map['panna 35%'] ?? 0);
    qs('ing_lsp').value = (map['latte scremato in polvere'] ?? 0);
    qs('ing_saccarosio').value = (map['saccarosio'] ?? 0);
    qs('ing_destrosio').value = (map['destrosio'] ?? 0);
    qs('ing_glucosio').value = (map['glucosio de21'] ?? map['glucosio'] ?? 0);
    qs('ing_frutta_secca').value = (map['frutta secca'] ?? 0);
    qs('ing_frutta_fresca').value = (map['frutta fresca'] ?? 0);
    qs('ing_inulina').value = (map['inulina'] ?? 0);
    qs('ing_cacao_amaro').value = (map['cacao amaro'] ?? 0);
}

async function suggestTargets() {
    const stile = qs('stile').value;
    const t = await fetchJSON('/debug/suggest_targets', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ stile })
    });
    setTargetFields(t);
}

async function balance() {
    const stile = qs('stile').value;
    const target = getTargetFromFields();
    const ingredienti = getIngredients();
    const out = await fetchJSON('/debug/balance_recipe', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ stile, target, ingredienti })
    });
    qs('results').textContent = JSON.stringify(out, null, 2);
    renderInfo(out);
}

// Funzione Export WhatsApp rimossa: il flusso è gestito direttamente nel pulsante Condividi

function bootstrap() {
    // Preset buttons
    qs('presetFiordipanna').addEventListener('click', () => applyPreset('fior_di_latte_base'));
    qs('presetCioccolato').addEventListener('click', () => applyPreset('cioccolato_base'));
    qs('btnCalcola').addEventListener('click', balance);
    qs('btnReset').addEventListener('click', () => {
        document.querySelectorAll('#ingGrid input').forEach(i => i.value = '');
        qs('results').textContent = '';
        qs('metrics').innerHTML = '';
        qs('alerts').innerHTML = '';
        qs('neutroVal').textContent = '0';
    });

    // Health
    const btnH = qs('btnHealth');
    const badge = qs('healthStatus');
    async function doHealth() {
        try {
            const res = await fetch('/health');
            if (res.ok) { badge.textContent = 'healthy'; badge.className = 'badge badge-ok'; }
            else { badge.textContent = 'unhealthy'; badge.className = 'badge badge-fail'; }
        } catch (e) { badge.textContent = 'offline'; badge.className = 'badge badge-fail'; }
    }
    btnH.addEventListener('click', doHealth);
    doHealth();

    // Basic translations for headings
    const UI_STRINGS = {
        it: {
            title: 'Il Gelato Artigianale Italiano', hdr1: '1) Stile e Preset', hdr2: '2) Ingredienti', hdr3: '3) Risultati',
            health: 'Health', lingua: 'Lingua:', lblStyle: 'Stile', hdrRanges: 'Range consigliati (%)',
            lblZuccheri: 'Zuccheri', lblGrassi: 'Grassi', lblSLM: 'SLM', lblSolidi: 'Solidi', lblPOD: 'POD', lblPAC: 'PAC',
            lblLatte: 'Latte (g)', lblPanna: 'Panna 35% (g)', lblLSP: 'Latte Scremato Polvere (g)', lblSaccarosio: 'Saccarosio (g)', lblDestrosio: 'Destrosio (g)', lblGlucosio: 'Glucosio DE21 (g)', lblFruttaSecca: 'Frutta Secca (g)', lblFruttaFresca: 'Frutta Fresca (g)', lblInulina: 'Inulina (g)', lblCacaoAmaro: 'Cacao Amaro (g)',
            neutro: 'Neutro 5 (Tara,Guar)',
            presetFiordipanna: 'Fiordipanna', presetCioccolato: 'Cioccolato',
            manage: 'Gestione ricetta', save: 'Salva', load: 'Carica', del: 'Elimina', share: 'Condividi', recipeName: 'Nome ricetta',
            modalClose: 'Chiudi'
        },
        en: {
            title: 'Il Gelato Artigianale Italiano', hdr1: '1) Style & Presets', hdr2: '2) Ingredients', hdr3: '3) Results',
            health: 'Health', lingua: 'Language:', lblStyle: 'Style', hdrRanges: 'Recommended ranges (%)',
            lblZuccheri: 'Sugars', lblGrassi: 'Fats', lblSLM: 'MSNF', lblSolidi: 'Solids', lblPOD: 'POD', lblPAC: 'PAC',
            lblLatte: 'Milk (g)', lblPanna: 'Cream 35% (g)', lblLSP: 'Skim Milk Powder (g)', lblSaccarosio: 'Sucrose (g)', lblDestrosio: 'Dextrose (g)', lblGlucosio: 'Glucose DE21 (g)', lblFruttaSecca: 'Nuts (g)', lblFruttaFresca: 'Fresh fruit (g)', lblInulina: 'Inulin (g)', lblCacaoAmaro: 'Cocoa powder (g)',
            neutro: 'Neutro 5 (Tara,Guar)',
            presetFiordipanna: 'Fior di latte', presetCioccolato: 'Chocolate',
            manage: 'Recipe management', save: 'Save', load: 'Load', del: 'Delete', share: 'Share', recipeName: 'Recipe name',
            modalClose: 'Close'
        },
        fr: {
            title: 'Il Gelato Artigianale Italiano', hdr1: '1) Style & Presets', hdr2: '2) Ingrédients', hdr3: '3) Résultats',
            health: 'Santé', lingua: 'Langue:', lblStyle: 'Style', hdrRanges: 'Plages recommandées (%)',
            lblZuccheri: 'Sucres', lblGrassi: 'Graisses', lblSLM: 'ESDL', lblSolidi: 'Solides', lblPOD: 'POD', lblPAC: 'PAC',
            lblLatte: 'Lait (g)', lblPanna: 'Crème 35% (g)', lblLSP: 'Lait écrémé en poudre (g)', lblSaccarosio: 'Saccharose (g)', lblDestrosio: 'Dextrose (g)', lblGlucosio: 'Glucose DE21 (g)', lblFruttaSecca: 'Fruits secs (g)', lblFruttaFresca: 'Fruits frais (g)', lblInulina: 'Inuline (g)', lblCacaoAmaro: 'Cacao en poudre (g)',
            neutro: 'Neutro 5 (Tara,Guar)',
            presetFiordipanna: 'Fior di latte', presetCioccolato: 'Chocolat',
            manage: 'Gestion de recette', save: 'Enregistrer', load: 'Charger', del: 'Supprimer', share: 'Partager', recipeName: 'Nom de la recette',
            modalClose: 'Fermer'
        },
        es: {
            title: 'Il Gelato Artigianale Italiano', hdr1: '1) Estilo y Presets', hdr2: '2) Ingredientes', hdr3: '3) Resultados',
            health: 'Salud', lingua: 'Idioma:', lblStyle: 'Estilo', hdrRanges: 'Rangos recomendados (%)',
            lblZuccheri: 'Azúcares', lblGrassi: 'Grasas', lblSLM: 'ESDL', lblSolidi: 'Sólidos', lblPOD: 'POD', lblPAC: 'PAC',
            lblLatte: 'Leche (g)', lblPanna: 'Nata 35% (g)', lblLSP: 'Leche desnatada en polvo (g)', lblSaccarosio: 'Sacarosa (g)', lblDestrosio: 'Dextrosa (g)', lblGlucosio: 'Glucosa DE21 (g)', lblFruttaSecca: 'Frutos secos (g)', lblFruttaFresca: 'Fruta fresca (g)', lblInulina: 'Inulina (g)', lblCacaoAmaro: 'Cacao en polvo (g)',
            neutro: 'Neutro 5 (Tara,Guar)',
            presetFiordipanna: 'Fiordilatte', presetCioccolato: 'Chocolate',
            manage: 'Gestión de receta', save: 'Guardar', load: 'Cargar', del: 'Eliminar', share: 'Compartir', recipeName: 'Nombre de la receta',
            modalClose: 'Cerrar'
        },
        de: {
            title: 'Il Gelato Artigianale Italiano', hdr1: '1) Stil & Presets', hdr2: '2) Zutaten', hdr3: '3) Ergebnisse',
            health: 'Health', lingua: 'Sprache:', lblStyle: 'Stil', hdrRanges: 'Empfohlene Bereiche (%)',
            lblZuccheri: 'Zucker', lblGrassi: 'Fette', lblSLM: 'MSNF', lblSolidi: 'Feststoffe', lblPOD: 'POD', lblPAC: 'PAC',
            lblLatte: 'Milch (g)', lblPanna: 'Sahne 35% (g)', lblLSP: 'Magermilchpulver (g)', lblSaccarosio: 'Saccharose (g)', lblDestrosio: 'Dextrose (g)', lblGlucosio: 'Glukose DE21 (g)', lblFruttaSecca: 'Nüsse (g)', lblFruttaFresca: 'Frisches Obst (g)', lblInulina: 'Inulin (g)', lblCacaoAmaro: 'Kakaopulver (g)',
            neutro: 'Neutro 5 (Tara,Guar)',
            presetFiordipanna: 'Fior di latte', presetCioccolato: 'Schokolade',
            manage: 'Rezeptverwaltung', save: 'Speichern', load: 'Laden', del: 'Löschen', share: 'Teilen', recipeName: 'Rezeptname',
            modalClose: 'Schließen'
        },
    };
    const uiLangSel = qs('uiLang');
    const title = qs('title');
    const hdr1 = qs('hdr1');
    const hdr2 = qs('hdr2');
    const hdr3 = qs('hdr3');
    const lblUiLang = qs('lblUiLang');
    const lblStyle = qs('lblStyle');
    const hdrRanges = qs('hdrRanges');
    const idMap = {
        lblZuccheri: 'lblZuccheri', lblGrassi: 'lblGrassi', lblSLM: 'lblSLM', lblSolidi: 'lblSolidi', lblPOD: 'lblPOD', lblPAC: 'lblPAC',
        lblLatte: 'lblLatte', lblPanna: 'lblPanna', lblLSP: 'lblLSP', lblSaccarosio: 'lblSaccarosio', lblDestrosio: 'lblDestrosio', lblGlucosio: 'lblGlucosio', lblFruttaSecca: 'lblFruttaSecca', lblFruttaFresca: 'lblFruttaFresca', lblInulina: 'lblInulina', lblCacaoAmaro: 'lblCacaoAmaro',
        lblNeutro: 'neutro', hdrManage: 'manage', btnSave: 'save', btnLoad: 'load', btnDelete: 'del', btnShare: 'share', recipeName: 'recipeName',
        presetFiordipanna: 'presetFiordipanna', presetCioccolato: 'presetCioccolato'
    };
    function applyUiLang() {
        const L = UI_STRINGS[uiLangSel.value] || UI_STRINGS.it;
        title.textContent = L.title; hdr1.textContent = L.hdr1; hdr2.textContent = L.hdr2; hdr3.textContent = L.hdr3;
        btnH.textContent = L.health; lblUiLang.textContent = L.lingua; lblStyle.textContent = L.lblStyle; hdrRanges.textContent = L.hdrRanges;
        for (const [elId, key] of Object.entries(idMap)) { const el = qs(elId) || qs(elId.replace('lbl', '')); if (el && L[key]) el.textContent = L[key]; }
        const recName = qs('recipeName'); if (recName && L.recipeName) recName.placeholder = L.recipeName;
        const infoClose = qs('infoClose'); if (infoClose && L.modalClose) infoClose.textContent = L.modalClose;
    }
    uiLangSel.addEventListener('change', applyUiLang);
    applyUiLang();

    // Aggiorna i range automaticamente quando cambia lo stile
    const stileSel = qs('stile');
    stileSel.addEventListener('change', suggestTargets);
    // Applica range iniziali
    suggestTargets();

    // Re-applica i range consigliati anche quando si applicano i preset
    document.getElementById('presetFiordipanna').addEventListener('click', suggestTargets);
    document.getElementById('presetCioccolato').addEventListener('click', suggestTargets);

    // Metrics rendering
    function renderMetrics(out) {
        const m = qs('metrics');
        const alerts = qs('alerts');
        m.innerHTML = ''; alerts.innerHTML = '';
        if (!out || !out.parametri) return;
        const p = out.parametri;
        const entro = out.entro_range || {};
        const defs = [
            { key: 'zuccheri_totali_pct', name: 'Zuccheri totali', val: p.zuccheri_totali_pct, range: entro.zuccheri_totali_pct },
            { key: 'grassi_totali_pct', name: 'Grassi totali', val: p.grassi_totali_pct, range: entro.grassi_totali_pct },
            { key: 'slm_pct', name: 'SLM', val: p.slm_pct, range: entro.slm_pct },
            { key: 'solidi_totali_pct', name: 'Solidi totali', val: p.solidi_totali_pct, range: entro.solidi_totali_pct },
            { key: 'pod_pct', name: 'POD', val: p.pod_pct, range: entro.pod_pct },
            { key: 'pac_pct', name: 'PAC', val: p.pac_pct, range: entro.pac_pct },
        ];
        for (const d of defs) {
            const bad = d.range === false;
            const div = document.createElement('div');
            div.className = 'metric' + (bad ? ' bad' : '');
            div.innerHTML = '<div class="name">' + d.name + '</div>' +
                '<div class="val">' + ((d.val ?? 0).toFixed(2)) + '%</div>' +
                '<div class="range">' + (bad ? 'Fuori range' : 'OK') + '</div>';
            m.appendChild(div);
            if (bad) {
                const al = document.createElement('div');
                al.className = 'alert';
                al.textContent = d.name + ' fuori range';
                alerts.appendChild(al);
            }
        }
    }

    function renderInfo(out) {
        if (!out) return;
        if (typeof out.neutro_5_g === 'number') qs('neutroVal').textContent = out.neutro_5_g.toFixed(3);
        // Also show alerts from backend if provided
        const alerts = qs('alerts');
        if (Array.isArray(out.alerts)) {
            for (const msg of out.alerts) {
                const al = document.createElement('div');
                al.className = 'alert';
                al.textContent = msg;
                alerts.appendChild(al);
            }
        }
    }

    // Update metrics when results change
    const resultsPre = qs('results');
    const _setText = Object.getOwnPropertyDescriptor(Node.prototype, 'textContent').set;
    Object.defineProperty(resultsPre, 'textContent', {
        set(v) { _setText.call(this, v); try { renderMetrics(JSON.parse(v || '{}')); } catch (_) { } },
        get() { return this.innerText; }
    });

    // Live thresholds on ingredient edits
    function clampIngredientInputs() {
        document.querySelectorAll('#ingGrid input[type="number"]').forEach(inp => {
            const v = Number((inp.value || '').trim());
            if (!Number.isNaN(v) && v < 0) inp.value = 0;
        });
    }
    document.querySelector('#ingGrid').addEventListener('input', async () => {
        clampIngredientInputs();
        try {
            const stile = qs('stile').value;
            const target = getTargetFromFields();
            const ingredienti = getIngredients();
            const out = await fetchJSON('/debug/balance_recipe', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ stile, target, ingredienti })
            });
            renderMetrics(out);
            renderInfo(out);
        } catch (e) { }
    });

    // Iniziale: suggerisci range consigliati
    suggestTargets();

    // Gestione ricette in localStorage
    function loadSavedList() {
        const sel = qs('savedRecipes');
        const keys = Object.keys(localStorage).filter(k => k.startsWith('ricetta:')).sort();
        sel.innerHTML = '';
        for (const k of keys) {
            const opt = document.createElement('option');
            opt.value = k; opt.textContent = k.replace('ricetta:', '');
            sel.appendChild(opt);
        }
    }
    function currentRecipeState() {
        return {
            stile: qs('stile').value,
            target: getTargetFromFields(),
            ingredienti: getIngredients()
        };
    }
    qs('btnShare').addEventListener('click', async () => {
        let text = '';
        try {
            const stile = qs('stile').value;
            const lingua = (qs('uiLang')?.value) || 'it';
            const target = getTargetFromFields();
            const ingredienti = getIngredients();
            const bal = await fetchJSON('/debug/balance_recipe', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ stile, target, ingredienti })
            });
            const parametri = bal.parametri || {};
            const ricetta = bal.ricetta_ribilanciata || ingredienti;
            const ex = await fetchJSON('/debug/export_whatsapp', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ stile, lingua, ricetta, parametri, target })
            });
            text = ex.text || '';
        } catch (_) { /* ignore */ }
        if (!text) return;
        const url = 'https://wa.me/?text=' + encodeURIComponent(text);
        window.open(url, '_blank');
    });
    qs('btnLoad').addEventListener('click', () => {
        const sel = qs('savedRecipes');
        const key = sel.value; if (!key) return;
        const data = JSON.parse(localStorage.getItem(key) || '{}');
        if (!data.ingredienti) return;
        // stile
        if (data.stile) qs('stile').value = data.stile;
        // target
        if (data.target) setTargetFields(data.target);
        // ingredienti
        const map = Object.fromEntries((data.ingredienti || []).map(i => [i.nome.toLowerCase(), i.grammi]));
        qs('ing_latte').value = (map['latte intero'] ?? 0);
        qs('ing_panna').value = (map['panna 35%'] ?? 0);
        qs('ing_lsp').value = (map['latte scremato in polvere'] ?? 0);
        qs('ing_saccarosio').value = (map['saccarosio'] ?? 0);
        qs('ing_destrosio').value = (map['destrosio'] ?? 0);
        qs('ing_glucosio').value = (map['glucosio de21'] ?? map['glucosio'] ?? 0);
        qs('ing_frutta_secca').value = (map['frutta secca'] ?? 0);
        qs('ing_frutta_fresca').value = (map['frutta fresca'] ?? 0);
        qs('ing_inulina').value = (map['inulina'] ?? 0);
        qs('ing_cacao_amaro').value = (map['cacao amaro'] ?? 0);
    });
    qs('btnDelete').addEventListener('click', () => {
        const sel = qs('savedRecipes'); const key = sel.value; if (!key) return;
        localStorage.removeItem(key); loadSavedList();
    });
    // Nota: listener btnShare già definito sopra (versione che genera testo WhatsApp). Evitiamo duplicati.
    loadSavedList();

    // Info ingredienti (dettagli stile app Android)
    const INFO_STRINGS = {
        it: {
            latte: { title: 'Latte intero', html: 'Il latte contribuisce con ~3,5% grassi e ~9% SLM. Contiene ~4,5% lattosio che influisce su dolcezza (POD) e punto di congelamento (PAC).' },
            panna: { title: 'Panna 35%', html: 'Apporta principalmente grassi (~35%) e una piccola quota di SLM. Aumenta struttura, cremosità e ricchezza.' },
            lsp: { title: 'Latte Scremato in Polvere', html: 'Incrementa gli SLM in modo efficiente (~96–97% solidi). Migliora corpo/struttura. Evitare >~12% sul totale miscela per non avere difetti.' },
            saccarosio: { title: 'Saccarosio', html: 'Zucchero comune con POD=1 e PAC=1: contribuisce a dolcezza e PAC in modo equilibrato.' },
            destrosio: { title: 'Destrosio', html: 'POD ~0,7 e PAC ~1,9: dolcifica meno del saccarosio ma abbassa maggiormente il punto di congelamento.' },
            glucosio: { title: 'Glucosio DE21', html: 'POD ~0,21 e PAC ~0,45: incide poco sulla dolcezza, utile per texture e anticristallizzazione.' },
            frutta_secca: { title: 'Frutta secca', html: 'Nocciole/mandorle: molte sostanze grasse (~60%) e solidi; intensificano sapore e cremosità.' },
            frutta_fresca: { title: 'Frutta fresca', html: 'Circa ~5,3% zuccheri e ~10% solidi: contribuisce a zuccheri/solidi totali e aroma naturale.' },
            inulina: { title: 'Inulina', html: 'Fibra solubile: aumenta solidi non zuccherini senza aumentare dolcezza; migliora corpo e cremosità.' },
            cacao: { title: 'Cacao amaro', html: 'Apporta solidi, colore e aroma; assorbe acqua, richiede bilanciamento di zuccheri/solidi.' }
        },
        en: {
            latte: { title: 'Whole milk', html: 'Contributes ~3.5% fat and ~9% MSNF. Also ~4.5% lactose, affecting sweetness (POD) and freezing point (PAC).' },
            panna: { title: 'Cream 35%', html: 'Mainly adds fat (~35%) and a little MSNF. Increases structure, creaminess and richness.' },
            lsp: { title: 'Skim milk powder', html: 'Efficiently increases MSNF (~96–97% solids); improves body/structure. Avoid >~12% of mix to prevent texture issues.' },
            saccarosio: { title: 'Sucrose', html: 'Common sugar with POD=1 and PAC=1: balanced impact on sweetness and PAC.' },
            destrosio: { title: 'Dextrose', html: 'POD ~0.7 and PAC ~1.9: less sweet than sucrose but lowers the freezing point more.' },
            glucosio: { title: 'Glucose DE21', html: 'POD ~0.21 and PAC ~0.45: little sweetness; helps texture and anticrystallization.' },
            frutta_secca: { title: 'Nuts', html: 'Hazelnuts/almonds: high fat (~60%) and solids; enhance flavor and creaminess.' },
            frutta_fresca: { title: 'Fresh fruit', html: '~5.3% sugars and ~10% solids: contributes to total sugars/solids and natural aroma.' },
            inulina: { title: 'Inulin', html: 'Soluble fiber: increases non-sugar solids without adding sweetness; improves body and creaminess.' },
            cacao: { title: 'Cocoa powder', html: 'Adds solids, color and flavor; absorbs water, requires sugar/solids balancing.' }
        },
        fr: {
            latte: { title: 'Lait entier', html: 'Apporte ~3,5% de matières grasses et ~9% d’ESDL. Environ ~4,5% de lactose, influençant la douceur (POD) et le point de congélation (PAC).' },
            panna: { title: 'Crème 35%', html: 'Apporte surtout des graisses (~35%) et un peu d’ESDL. Augmente structure, onctuosité et richesse.' },
            lsp: { title: 'Lait écrémé en poudre', html: 'Augmente efficacement l’ESDL (~96–97% de solides) ; améliore corps/structure. Éviter >~12% du mélange.' },
            saccarosio: { title: 'Saccharose', html: 'Sucre courant avec POD=1 et PAC=1 : impact équilibré sur douceur et PAC.' },
            destrosio: { title: 'Dextrose', html: 'POD ~0,7 et PAC ~1,9 : moins sucré que le saccharose, abaisse davantage le point de congélation.' },
            glucosio: { title: 'Glucose DE21', html: 'POD ~0,21 et PAC ~0,45 : peu de douceur ; aide la texture et l’anticristallisation.' },
            frutta_secca: { title: 'Fruits secs', html: 'Noisettes/amandes : riches en graisses (~60%) et solides ; intensifient saveur et onctuosité.' },
            frutta_fresca: { title: 'Fruits frais', html: '~5,3% de sucres et ~10% de solides : contribuent aux sucres/solides totaux et à l’arôme naturel.' },
            inulina: { title: 'Inuline', html: 'Fibre soluble : augmente les solides non sucrés sans ajouter de douceur ; améliore corps et onctuosité.' },
            cacao: { title: 'Cacao en poudre', html: 'Apporte solides, couleur et arôme ; absorbe l’eau, nécessite un équilibrage sucres/solides.' }
        },
        es: {
            latte: { title: 'Leche entera', html: 'Aporta ~3,5% de grasa y ~9% de sólidos no grasos. También ~4,5% de lactosa que afecta dulzor (POD) y punto de congelación (PAC).' },
            panna: { title: 'Nata 35%', html: 'Principalmente añade grasa (~35%) y algo de sólidos no grasos. Aumenta estructura, cremosidad y riqueza.' },
            lsp: { title: 'Leche desnatada en polvo', html: 'Aumenta eficientemente los sólidos no grasos (~96–97% sólidos); mejora cuerpo/estructura. Evitar >~12% de la mezcla.' },
            saccarosio: { title: 'Sacarosa', html: 'Azúcar común con POD=1 y PAC=1: impacto equilibrado en dulzor y PAC.' },
            destrosio: { title: 'Dextrosa', html: 'POD ~0,7 y PAC ~1,9: endulza menos que la sacarosa pero baja más el punto de congelación.' },
            glucosio: { title: 'Glucosa DE21', html: 'POD ~0,21 y PAC ~0,45: poca dulzura; ayuda a la textura y a la anticristalización.' },
            frutta_secca: { title: 'Frutos secos', html: 'Avellanas/almendras: alto contenido graso (~60%) y sólidos; intensifica sabor y cremosidad.' },
            frutta_fresca: { title: 'Fruta fresca', html: '~5,3% de azúcares y ~10% de sólidos: contribuye a azúcares/sólidos y al aroma natural.' },
            inulina: { title: 'Inulina', html: 'Fibra soluble: aumenta sólidos no azucarados sin añadir dulzor; mejora cuerpo y cremosidad.' },
            cacao: { title: 'Cacao en polvo', html: 'Aporta sólidos, color y sabor; absorbe agua, requiere equilibrar azúcares/sólidos.' }
        },
        de: {
            latte: { title: 'Vollmilch', html: 'Trägt ~3,5% Fett und ~9% fettfreie Trockenmasse (MSNF) bei. Zudem ~4,5% Laktose, was Süße (POD) und Gefrierpunkt (PAC) beeinflusst.' },
            panna: { title: 'Sahne 35%', html: 'Fügt hauptsächlich Fett (~35%) und etwas MSNF hinzu. Erhöht Struktur, Cremigkeit und Fülle.' },
            lsp: { title: 'Magermilchpulver', html: 'Erhöht effizient die MSNF (~96–97% Feststoffe); verbessert Körper/Struktur. Vermeide >~12% der Mischung.' },
            saccarosio: { title: 'Saccharose', html: 'Gewöhnlicher Zucker mit POD=1 und PAC=1: ausgewirkter Einfluss auf Süße und PAC.' },
            destrosio: { title: 'Dextrose', html: 'POD ~0,7 und PAC ~1,9: weniger süß als Saccharose, senkt aber den Gefrierpunkt stärker.' },
            glucosio: { title: 'Glukose DE21', html: 'POD ~0,21 und PAC ~0,45: geringe Süße; hilft bei Textur und Antikristallisation.' },
            frutta_secca: { title: 'Nüsse', html: 'Haselnüsse/Mandeln: hoher Fettgehalt (~60%) und Feststoffe; verstärken Geschmack und Cremigkeit.' },
            frutta_fresca: { title: 'Frisches Obst', html: '~5,3% Zucker und ~10% Feststoffe: trägt zu Gesamtzucker/-feststoffen und natürlichem Aroma bei.' },
            inulina: { title: 'Inulin', html: 'Lösliche Ballaststoffe: erhöht nicht-zuckerhaltige Feststoffe ohne Süße; verbessert Körper und Cremigkeit.' },
            cacao: { title: 'Kakaopulver', html: 'Liefert Feststoffe, Farbe und Aroma; nimmt Wasser auf, erfordert Ausbalancierung von Zucker/Feststoffen.' }
        }
    };

    const modal = qs('infoModal');
    const infoTitle = qs('infoTitle');
    const infoBody = qs('infoBody');
    const infoClose = qs('infoClose');
    function openInfo(key) {
        const lang = (qs('uiLang')?.value) || 'it';
        const L = INFO_STRINGS[lang] || INFO_STRINGS.it;
        const data = L[key] || INFO_STRINGS.it[key];
        if (!data) return;
        infoTitle.textContent = data.title;
        infoBody.innerHTML = data.html;
        modal.classList.remove('hidden');
    }
    function closeInfo() { modal.classList.add('hidden'); }
    infoClose.addEventListener('click', closeInfo);
    modal.addEventListener('click', (e) => { if (e.target === modal) closeInfo(); });
    document.querySelectorAll('.ing-info').forEach(btn => {
        btn.addEventListener('click', () => openInfo(btn.getAttribute('data-info')));
    });
}

document.addEventListener('DOMContentLoaded', bootstrap);
