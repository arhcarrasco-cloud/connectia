/* ============================================================
   Connectia · Cotizador de Proyectos  ⇄  ERP Connectia
   - Liga la sesión del cotizador a un cliente (CLI-xxxxxx) y oportunidad (OPP-xxxxx) del ERP
   - "Emitir en ERP": registra la cotización en erp.cotizacion vía la RPC
     erp.cotizacion_desde_cotizador (misma BD y mismo Supabase Auth que el ERP; aplica RLS).
   - El folio (COT-AAAA-0NNN) lo asigna SIEMPRE la base de datos (trigger trg_cot_folio),
     mismo consecutivo que el resto de cotizaciones del ERP. Aquí nunca se calcula.
   - Re-emitir: borrador -> se actualiza (mismo folio); enviada -> revisión (folio nuevo, v+1).
   Contexto desde el ERP (erp.connectia.mx/ERP/cotizaciones/proyecto):
     llega en el #fragmento junto con la sesión SSO (cx-auth.js lo pasa a sessionStorage
     'cxErpCtx' y limpia el hash). Se sigue aceptando el formato viejo en query string:
     ?origen=erp&cliente_id=…&cli=CLI-…&oportunidad_id=…&opp=OPP-…&ejecutivo_id=…
   ============================================================ */
(function (global) {
  'use strict';
  const ERP = 'https://erp.connectia.mx';
  const CTX_KEY = 'cxErpCtx';
  let link = {};            // vínculo de la sesión abierta (se guarda en data.erp)
  let rolErp = undefined;   // undefined = sin revisar, null = sin acceso
  let clientes = null;      // catálogo erp.cliente (lazy)
  let opps = {};            // cliente_id -> oportunidades
  let emitiendo = false;

  const $ = id => document.getElementById(id);
  const esc = s => String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  const money = n => '$' + Number(n || 0).toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  function sb() { return global.CXAUTH && CXAUTH.sb; }
  function erp() { return sb().schema('erp'); }

  /* ---------- contexto que llega por URL desde el ERP ---------- */
  (function leerUrl() {
    const q = new URLSearchParams(location.search);
    if (!q.get('cliente_id') && !q.get('oportunidad_id')) return;
    const ctx = {
      cliente_id: q.get('cliente_id') || '', cliente_codigo: q.get('cli') || '',
      oportunidad_id: q.get('oportunidad_id') || '', oportunidad_folio: q.get('opp') || '',
      ejecutivo_id: q.get('ejecutivo_id') || ''
    };
    sessionStorage.setItem(CTX_KEY, JSON.stringify(ctx));
    // limpia la URL (sin perder hash de recuperación de contraseña, si lo hubiera)
    history.replaceState(null, '', location.pathname + location.hash);
  })();

  /* ---------- estilos + UI ---------- */
  function estilos() {
    if ($('cxErpStyles')) return;
    const s = document.createElement('style');
    s.id = 'cxErpStyles';
    s.textContent = `
    .erp-panel{margin:14px 36px 0;padding:12px 14px;border:1px solid #e3dcf0;border-left:4px solid #6030A0;border-radius:10px;background:#faf8fe;font:400 12.5px Inter,system-ui,sans-serif;color:#241B3A}
    .erp-panel .erp-t{font:700 10.5px Inter,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#6030A0;margin-bottom:8px;display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap}
    .erp-panel .erp-row{display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end}
    .erp-panel label{display:flex;flex-direction:column;gap:3px;font:700 10px Inter,sans-serif;letter-spacing:.06em;text-transform:uppercase;color:#6b6880}
    .erp-panel input,.erp-panel select{padding:7px 9px;border:1px solid #ddd9e8;border-radius:8px;font:400 13px Inter,sans-serif;color:#1B1036;background:#fff;min-width:230px}
    .erp-panel .erp-st{margin-top:8px;display:flex;gap:12px;flex-wrap:wrap;align-items:center}
    .erp-panel .erp-folio{font:800 15px Inter,sans-serif;color:#6030A0}
    .erp-panel a{color:#6030A0;font-weight:700}
    .erp-panel .erp-warn{color:#a4262c}
    .erp-panel .erp-chip{font:700 10px Inter,sans-serif;padding:2px 8px;border-radius:20px;background:#eee6f5;color:#4d2682;text-transform:uppercase;letter-spacing:.06em}
    .btn-erp{background:#201040!important;color:#fff!important}
    .folio-input[readonly]{cursor:default}
    @media print{.erp-panel{display:none}}`;
    document.head.appendChild(s);
  }

  function montarUI() {
    estilos();
    if (!$('erpPanel')) {
      const p = document.createElement('div');
      p.id = 'erpPanel';
      p.className = 'erp-panel';
      const ancla = document.querySelector('.client-block');
      if (ancla && ancla.parentNode) ancla.parentNode.insertBefore(p, ancla.nextSibling);
    }
    if (!$('btnEmitirErp')) {
      const g = $('groupCotizador');
      if (g) {
        const b = document.createElement('button');
        b.id = 'btnEmitirErp';
        b.className = 'btn btn-export btn-erp';
        b.type = 'button';
        b.textContent = '🧾 Emitir en ERP (folio)';
        b.onclick = () => emitir();
        g.insertBefore(b, g.firstChild);
      }
    }
    const f = $('folio');
    if (f) {
      f.readOnly = true;
      f.placeholder = 'sin folio';
      f.title = 'El folio lo asigna el ERP al emitir (consecutivo único).';
    }
  }

  function render() {
    const p = $('erpPanel');
    if (!p) return;
    const f = $('folio');
    if (f) f.value = link.folio || '';
    if (rolErp === null) {
      p.innerHTML = `<div class="erp-t"><span>Vínculo ERP</span></div>
        <div class="erp-warn">Tu usuario no está dado de alta en el ERP Connectia: puedes cotizar, pero no emitir folio. Pide acceso a Dirección.</div>`;
      return;
    }
    const cl = (clientes || []).find(c => c.id === link.cliente_id);
    const cliTxt = cl ? `${cl.cliente_codigo || 'sin CLI'} · ${cl.nombre_comercial}` : (link.cliente_id ? (link.cliente_codigo || link.cliente_id) : '');
    const ops = opps[link.cliente_id] || [];
    const bloqueado = !!link.cotizacion_id && !['borrador', 'en_revision', 'lista_enviar'].includes(link.estatus || 'borrador');
    p.innerHTML = `
      <div class="erp-t"><span>Vínculo ERP · cliente y oportunidad</span>
        <span>${link.cotizacion_id ? `<span class="erp-chip">${esc((link.estatus || 'borrador').replace(/_/g, ' '))}</span>` : ''}</span></div>
      <div class="erp-row">
        <label>Cliente ERP (CLI)
          <input id="erpCliente" list="erpClientesList" placeholder="${clientes ? 'Busca por nombre o CLI-…' : 'Cargando clientes…'}" value="${esc(cliTxt)}">
          <datalist id="erpClientesList">${(clientes || []).map(c => `<option value="${esc((c.cliente_codigo || 'sin CLI') + ' · ' + c.nombre_comercial)}">${esc(c.holding || '')}</option>`).join('')}</datalist>
        </label>
        <label>Oportunidad
          <select id="erpOpp" ${link.cliente_id ? '' : 'disabled'}>
            <option value="">— Sin oportunidad —</option>
            ${ops.map(o => `<option value="${o.id}" ${o.id === link.oportunidad_id ? 'selected' : ''}>${esc((o.folio || '') + ' · ' + (o.nombre || ''))}</option>`).join('')}
            ${link.oportunidad_id && !ops.some(o => o.id === link.oportunidad_id) ? `<option value="${esc(link.oportunidad_id)}" selected>${esc(link.oportunidad_folio || link.oportunidad_id)}</option>` : ''}
          </select>
        </label>
      </div>
      <div class="erp-st">
        ${link.folio
          ? `<span>Folio ERP: <span class="erp-folio">${esc(link.folio)}</span>${link.version > 1 ? ' · v' + link.version : ''}</span>
             ${link.subtotal != null ? `<span>Subtotal ERP ${money(link.subtotal)} · Total ${money(link.total)}</span>` : ''}
             <a href="${ERP}/ERP/cotizaciones/${encodeURIComponent(link.cotizacion_id)}/pdf" target="_blank" rel="noopener">PDF oficial ↗</a>
             ${link.oportunidad_id ? `<a href="${ERP}/ERP/pipeline/${encodeURIComponent(link.oportunidad_id)}" target="_blank" rel="noopener">Oportunidad ${esc(link.oportunidad_folio || '')} ↗</a>` : ''}
             <a href="${ERP}/ERP/cotizaciones" target="_blank" rel="noopener">Cotizaciones ERP ↗</a>
             ${bloqueado ? '<span>Ya enviada: al emitir de nuevo se crea una revisión con folio nuevo.</span>' : ''}`
          : `<span>Sin folio. Al <b>Emitir en ERP</b> la base de datos asigna el siguiente consecutivo COT y la liga al cliente${link.oportunidad_id ? ' y a la oportunidad' : ''}.</span>`}
        ${link.folioAnterior ? `<span style="color:#8b88a0">Folio manual anterior (no oficial): ${esc(link.folioAnterior)}</span>` : ''}
      </div>`;
    const ic = $('erpCliente');
    if (ic) ic.onchange = () => elegirCliente(ic.value);
    const so = $('erpOpp');
    if (so) so.onchange = () => {
      const o = ops.find(x => x.id === so.value);
      link.oportunidad_id = so.value || '';
      link.oportunidad_folio = o ? o.folio : '';
      if (o && o.ejecutivo_id) link.ejecutivo_id = o.ejecutivo_id;
      render();
    };
  }

  /* ---------- catálogos (RLS del ERP) ---------- */
  async function revisarAcceso() {
    try {
      const { data, error } = await erp().rpc('my_rol');
      rolErp = error ? null : (data || null);
    } catch (e) { rolErp = null; }
  }
  async function cargarClientes() {
    if (clientes || !rolErp) return;
    // PostgREST corta en 1,000 filas: se pagina.
    const todos = [];
    for (let desde = 0; desde < 20000; desde += 1000) {
      const { data, error } = await erp().from('cliente').select('id,cliente_codigo,nombre_comercial,holding')
        .eq('archivado', false).order('nombre_comercial').order('id').range(desde, desde + 999);
      if (error || !data) break;
      todos.push(...data);
      if (data.length < 1000) break;
    }
    clientes = todos;
  }
  async function cargarOpps(cid) {
    if (!cid || opps[cid] || !rolErp) return;
    const { data } = await erp().from('oportunidad').select('id,folio,nombre,ejecutivo_id,resultado')
      .eq('cliente_id', cid).order('created_at', { ascending: false });
    opps[cid] = (data || []).filter(o => o.resultado === 'abierta' || o.id === link.oportunidad_id);
  }
  async function elegirCliente(txt) {
    const t = String(txt || '').trim().toLowerCase();
    const c = (clientes || []).find(x => ((x.cliente_codigo || 'sin CLI') + ' · ' + x.nombre_comercial).toLowerCase() === t)
      || (clientes || []).find(x => (x.cliente_codigo || '').toLowerCase() === t);
    if (!c) { render(); return; }
    if (c.id !== link.cliente_id) { link.oportunidad_id = ''; link.oportunidad_folio = ''; }
    link.cliente_id = c.id; link.cliente_codigo = c.cliente_codigo || '';
    await prellenarCliente(c);
    await cargarOpps(c.id);
    render();
  }
  // Solo llena lo que esté vacío: no pisa lo que el ejecutivo ya escribió.
  async function prellenarCliente(c) {
    if (!c) return;
    if ($('clienteNombre') && !$('clienteNombre').value) $('clienteNombre').value = c.nombre_comercial || '';
    if (($('razonSocial') && !$('razonSocial').value) || ($('direccionCliente') && !$('direccionCliente').value)) {
      const { data } = await erp().from('razon_social').select('razon_social,rfc,direccion_fiscal').eq('cliente_id', c.id);
      if (data && data.length === 1) {
        if (!$('razonSocial').value) $('razonSocial').value = data[0].razon_social || '';
        if (!$('direccionCliente').value) $('direccionCliente').value = data[0].direccion_fiscal || '';
      }
    }
  }
  // Estado vivo de la cotización en el ERP (estatus/versión pueden cambiar allá).
  async function refrescarDesdeErp() {
    if (!rolErp || !currentSessionId) return;
    const { data } = await erp().from('cotizacion').select('id,folio,version,estatus,subtotal,total')
      .eq('cx_sesion_id', currentSessionId).order('version', { ascending: false }).limit(1);
    const c = data && data[0];
    if (c) Object.assign(link, { cotizacion_id: c.id, folio: c.folio, version: c.version, estatus: c.estatus, subtotal: Number(c.subtotal), total: Number(c.total) });
    render();
  }

  /* ---------- integración con el estado del cotizador ---------- */
  const _getState = global.getState, _setState = global.setState, _newSession = global.newSession, _exportPDF = global.exportPDF;
  global.getState = function () {
    const st = _getState();
    st.erp = JSON.parse(JSON.stringify(link));
    st.header.folio = link.folio || '';
    if (link.folioAnterior) st.header.folioAnterior = link.folioAnterior;
    return st;
  };
  global.setState = function (state) {
    _setState(state);
    const h = (state && state.header) || {};
    link = JSON.parse(JSON.stringify((state && state.erp) || {}));
    // Sesiones viejas: el folio era texto libre (p. ej. COT-2026-0001). Se conserva como
    // referencia, pero el folio oficial solo lo da el ERP.
    if (!link.folio && h.folio) link.folioAnterior = h.folio;
    else if (h.folioAnterior) link.folioAnterior = h.folioAnterior;
    render();
    if (link.cliente_id) cargarOpps(link.cliente_id).then(render);
    refrescarDesdeErp();
  };
  global.newSession = function () {
    _newSession();
    const st = $('sessionStatus');
    if (st && st.textContent === 'Nueva cotización iniciada') { link = {}; render(); }
  };
  global.exportPDF = async function () {
    if (!link.folio) {
      if (rolErp && confirm('Esta cotización aún no tiene folio del ERP.\n\nAceptar = emitirla ahora (folio consecutivo) y exportar.\nCancelar = exportar como BORRADOR sin folio.')) {
        const ok = await emitir(true);
        if (!ok) return;
      } else {
        const f = $('folio'); const prev = f.value;
        f.value = 'BORRADOR (sin folio)';
        try { _exportPDF(); } finally { f.value = prev; }
        return;
      }
    }
    _exportPDF();
  };

  /* ---------- emitir ---------- */
  function partidasYcosteo() {
    const partidas = [], filas = [], faltan = [];
    let cp = 0, pc = 0, com = 0, mar = 0;
    rows.forEach(r => {
      const c = computeRow(r);
      const desc = String(r.concepto || '').trim();
      if (!desc && c.PCtotal === null) return;
      if (c.error || c.PCunit === null) { faltan.push(desc || '(sin concepto)'); return; }
      const pu = Math.round(c.PCunit * 100) / 100;
      partidas.push({ descripcion: desc || 'Concepto', cantidad: c.qty, precio_unitario: pu });
      filas.push({ concepto: desc, cantidad: c.qty, costo_unit: c.CPunit, costo_total: c.CPtotal, precio_unit: pu,
        precio_total: c.PCtotal, comisiones: c.commAmounts, margen: c.margin, margen_pct: c.marginPct });
      cp += c.CPtotal || 0; pc += c.PCtotal || 0; com += c.commSum || 0; mar += c.margin || 0;
    });
    return { partidas, faltan, costeo: { costo_proveedor: cp, precio_cliente: pc, comisiones: com, margen: mar,
      margen_pct: pc > 0 ? mar / pc * 100 : null, margen_objetivo_pct: targetPct, comisiones_generales: commissions, filas } };
  }
  function traduce(e) {
    const m = (e && e.message) || String(e || '');
    if (/row-level security/i.test(m)) return 'El ERP no te permite registrar esta cotización: la oportunidad o el cliente están asignados a otro ejecutivo. Pide a tu supervisor/Dirección que la emita o que te reasigne la oportunidad.';
    return m;
  }

  async function emitir(silencioso) {
    if (emitiendo) return false;
    if (!sb()) { alert('Inicia sesión para emitir.'); return false; }
    if (rolErp === undefined) await revisarAcceso();
    if (!rolErp) { alert('Tu usuario no tiene acceso al ERP Connectia; no se puede emitir folio.'); return false; }
    if (!link.cliente_id) { alert('Elige el cliente del ERP (CLI) en el panel "Vínculo ERP" antes de emitir.'); $('erpCliente') && $('erpCliente').focus(); return false; }
    const { partidas, faltan, costeo } = partidasYcosteo();
    if (faltan.length) { alert('Estos conceptos no tienen precio al cliente:\n• ' + faltan.join('\n• ') + '\n\nCompleta o elimina esas líneas antes de emitir.'); return false; }
    if (!partidas.length) { alert('Captura al menos un concepto con precio.'); return false; }

    const enviada = link.cotizacion_id && !['borrador', 'en_revision', 'lista_enviar'].includes(link.estatus || 'borrador');
    const msg = !link.cotizacion_id
      ? 'Se registrará la cotización en el ERP con el siguiente folio consecutivo COT (no se puede deshacer).'
      : enviada ? `La ${link.folio} ya fue enviada. Se creará una REVISIÓN con folio nuevo que la sustituye en la oportunidad.`
        : `Se actualizará la ${link.folio} en el ERP (mismo folio).`;
    if (!silencioso && !confirm(msg + '\n\n¿Continuar?')) return false;

    emitiendo = true;
    const btn = $('btnEmitirErp'); if (btn) { btn.disabled = true; btn.textContent = 'Emitiendo…'; }
    try {
      // La sesión debe existir para que el vínculo sea estable (idempotente por sesión).
      if (!currentSessionId) saveSession(fieldVal('conceptoGeneral') || fieldVal('clienteNombre') || 'Cotización');
      const payload = {
        cx_sesion_id: currentSessionId,
        cliente_id: link.cliente_id,
        oportunidad_id: link.oportunidad_id || null,
        ejecutivo_id: link.ejecutivo_id || null,
        referencia: fieldVal('conceptoGeneral') || fieldVal('referencia') || null,
        su_referencia: fieldVal('referencia') || null,
        fecha: fieldVal('fechaCotizacion') || null,
        vigencia: fieldVal('vigencia') || null,
        terminos: fieldVal('terminos') || null,
        iva_on: $('ivaToggle').checked,
        partidas, costeo
      };
      const { data, error } = await erp().rpc('cotizacion_desde_cotizador', { p: payload });
      if (error) throw error;
      Object.assign(link, {
        cotizacion_id: data.id, folio: data.folio, version: data.version, estatus: 'borrador',
        cliente_codigo: data.cliente_codigo || link.cliente_codigo, oportunidad_folio: data.oportunidad_folio || link.oportunidad_folio,
        ejecutivo_id: data.ejecutivo_id || link.ejecutivo_id, subtotal: Number(data.subtotal), total: Number(data.total),
        emitida_at: new Date().toISOString()
      });
      $('folio').value = link.folio;
      saveSessionSilent();
      render();
      const verbo = data.accion === 'actualizada' ? 'actualizada' : data.accion === 'revision' ? 'emitida como revisión' : 'emitida';
      showSessionStatus(`Cotización ${data.folio} ${verbo} en el ERP`);
      return true;
    } catch (e) {
      alert('No se pudo emitir en el ERP:\n' + traduce(e));
      return false;
    } finally {
      emitiendo = false;
      if (btn) { btn.disabled = false; btn.textContent = '🧾 Emitir en ERP (folio)'; }
    }
  }

  /* ---------- arranque (después del login) ---------- */
  async function arrancar() {
    montarUI();
    await revisarAcceso();
    render();
    if (!rolErp) return;
    await cargarClientes();
    let ctx = null;
    try { ctx = JSON.parse(sessionStorage.getItem(CTX_KEY) || 'null'); } catch (e) {}
    if (ctx && !link.cotizacion_id) {
      sessionStorage.removeItem(CTX_KEY);
      // Desde el ERP se arranca una cotización nueva con el contexto recibido.
      if (currentSessionId) { currentSessionId = null; }
      Object.assign(link, { cliente_id: ctx.cliente_id, cliente_codigo: ctx.cliente_codigo,
        oportunidad_id: ctx.oportunidad_id, oportunidad_folio: ctx.oportunidad_folio, ejecutivo_id: ctx.ejecutivo_id });
      await prellenarCliente((clientes || []).find(c => c.id === ctx.cliente_id));
      showSessionStatus('Cotización nueva desde el ERP' + (ctx.oportunidad_folio ? ' · ' + ctx.oportunidad_folio : ''));
    }
    if (link.cliente_id) await cargarOpps(link.cliente_id);
    render();
  }
  global.CXERP = { emitir, get link() { return link; }, render };
  if (global.CXAUTH && CXAUTH.cloud) CXAUTH.onReady(arrancar);
  else document.addEventListener('DOMContentLoaded', arrancar);
})(window);
