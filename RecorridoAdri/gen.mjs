import { Workbook } from "https://esm.sh/exceljs@4.4.0?target=deno";
import { PDFDocument, rgb, StandardFonts } from "https://esm.sh/pdf-lib@1.17.1?target=deno";
const CORS = { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "content-type", "Access-Control-Allow-Methods": "POST, GET, OPTIONS" };
const RESEND_KEY = Deno.env.get("RESEND_API_KEY") || "re_QZq5i5qa_JuXadcavBPmGYhWWK31YWgbq";
const FROM = "Connectia <hola@connectia.mx>";
const CC = ["rhernandez@connectia.mx"];
const FN = "https://mduxlmnlwycwknyapwsx.supabase.co/functions/v1/recorrido-checkout";
const BASE = "https://connectia.mx/RecorridoAdri";
const LOGO = BASE + "/assets/connectia-white.png";
const GEO = "https://www.connectia.mx/geonexa";
const GEOROOT = "https://connectia.mx/geonexa/";
function geoPoint(lat, lng) {
  return GEOROOT + "?lat=" + lat + "&lng=" + lng + "&r=500";
}
function geoShare(d) {
  const pins = selAll(d).map((x) => POI[x.id]).filter(Boolean).map((p) => ({ t: "m", lat: p.lat, lng: p.lng, ti: p.n, c: "#6030A0" }));
  if (!pins.length) return GEOROOT;
  const lat = pins.reduce((a, b) => a + b.lat, 0) / pins.length, lng = pins.reduce((a, b) => a + b.lng, 0) / pins.length;
  return GEOROOT + "#share=" + b64utf8(JSON.stringify({ lat, lng, zoom: 12, pins }));
}
const SS = BASE + "/assets/sitios/";
const POI = {
  "EEM-0819-A": { n: "Cubo Digital Magnocentro \xB7 Interlomas", lat: 19.402051, lng: -99.271914, med: "18.7 \xD7 10 m", imp: 4e6, tipo: "Cubo digital", t: 1e6, dir: "Blvd. Magnocentro y Blvd. Interlomas, Huixquilucan", aud: "NSE ABC+ \xB7 AAA \xB7 Interlomas", niv: "Alto", ben: "Presencia Walmart en un punto de alt\xEDsimo flujo con exclusividad de categor\xEDa en Interlomas.", cad: "Walmart, City Market, Soriana y Chedraui a la redonda", wm: "assets/sitios/EEM-0819-A-wm.jpg" },
  "EEM-18177-B": { n: "Pantalla LED Toreo \xB7 Perif\xE9rico", lat: 19.460182, lng: -99.222014, med: "17.28 \xD7 8.64 m", imp: 63e5, tipo: "Pantalla LED digital", t: 65e3, dir: "Blvd. M. \xC1vila Camacho (Perif\xE9rico) y Av. Emiliano Zapata, Naucalpan", aud: "Vehicular masivo \xB7 Perif\xE9rico / Toreo", niv: "Alto", ben: "Entrada a CDMX por Perif\xE9rico: una de las vialidades con m\xE1s aforo del pa\xEDs.", cad: "Walmart, Bodega Aurrer\xE1 y Soriana a la redonda", wm: "assets/sitios/EEM-18177-B-wm.jpg" },
  "GLORIETA-LMK": { n: "Landmark Glorieta Interlomas \xB7 Walmart", lat: 19.39, lng: -99.2925, med: "Glorieta 60 \xD7 29 m \xB7 Spark 19 m \xB7 Pantalla 3D", imp: 22e5, tipo: "Landmark volum\xE9trico + 3D", t: 12e5, dir: "Glorieta Av. San Mateo Santa Rosa / Blvd. Palmas Hills, Interlomas", aud: "NSE ABC+ \xB7 coraz\xF3n de Interlomas", niv: "Alto", ben: "Dominio de marca en el punto m\xE1s ic\xF3nico de Interlomas, con producci\xF3n 3D y viralidad en redes.", cad: "Walmart, City Market y Chedraui a la redonda", wm: "assets/sitios/GLORIETA-LMK-wm.jpg" },
  "EEM-17672-A": { n: "Pantalla LED Paseo Interlomas", lat: 19.396232, lng: -99.281112, med: "15.36 \xD7 3.84 m", imp: 1835257, tipo: "Pantalla LED", t: 85e3, dir: "Vialidad frente a Paseo Interlomas, Huixquilucan", aud: "Shoppers \xB7 frente a Liverpool", niv: "Medio", ben: "Impacto directo sobre shoppers de alto poder adquisitivo en el corredor comercial.", cad: "Walmart, City Market y Chedraui a la redonda", wm: "assets/sitios/EEM-17672-A-wm.jpg" },
  "EEM-17672-B": { n: "Puente Paseo Interlomas", lat: 19.3968, lng: -99.2816, med: "15.10 \xD7 3.80 m", imp: 9e5, tipo: "Puente peatonal", t: 65e3, dir: "Frente a Hospital \xC1ngeles Interlomas, Huixquilucan", aud: "Vehicular \xB7 Hospital \xC1ngeles", niv: "T\xE1ctico", ben: "Refuerzo t\xE1ctico frente a Hospital \xC1ngeles y Paseo Interlomas.", cad: "Walmart y Chedraui a la redonda", wm: "assets/sitios/EEM-17672-B-wm.jpg" },
  "BEM-17344-A": { n: "Muro CC Interlomas", lat: 19.396262, lng: -99.288435, med: "8.00 \xD7 15.00 m", imp: 11e5, tipo: "Muro", t: 35e4, dir: "Entrada CC Interlomas, Huixquilucan", aud: "Shoppers \xB7 entrada principal", niv: "T\xE1ctico", ben: "\xDAltima impresi\xF3n antes de entrar al Centro Comercial Interlomas.", cad: "Walmart, City Market y Soriana a la redonda", wm: "assets/sitios/BEM-17344-A-wm.jpg" },
  "EEM-17427-B": { n: "Puente Hueyetlaco", lat: 19.387794, lng: -99.278823, med: "10.60 \xD7 5.20 m", imp: 85e4, tipo: "Puente peatonal", t: 12e4, dir: "Circulaci\xF3n Santa Fe hacia Interlomas, Huixquilucan", aud: "Vehicular \xB7 Santa Fe\u2013Interlomas", niv: "T\xE1ctico", ben: "Captura el flujo diario Santa Fe\u2013Interlomas.", cad: "Walmart y Bodega Aurrer\xE1 a la redonda", wm: "assets/sitios/EEM-17427-B-wm.jpg" },
  "EEM-15935-B": { n: "Unipolar Vialidad de la Barranca", lat: 19.388173, lng: -99.2786, med: "12.90 \xD7 10.80 m", imp: 14e5, tipo: "Unipolar", t: 6e4, dir: "Vialidad de la Barranca hacia Santa Fe, Huixquilucan", aud: "Alta plusval\xEDa \xB7 Bosques de las Lomas", niv: "Medio", ben: "Audiencia de alt\xEDsima plusval\xEDa rumbo a Santa Fe y Bosques.", cad: "Walmart, City Market y Soriana a la redonda", wm: "assets/sitios/EEM-15935-B-wm.jpg" }
};
const OPORT = [
  { id: "OPP-HAMB", lat: 19.42531, lng: -99.16688, n: "Landmark Hamb\xFArgo \xB7 Col. Ju\xE1rez", med: "12.9 \xD7 7.2 m \xB7 Pantalla LED", imp: 41e5, precio: "$750,000", t: 75e4, img: SS + "OPP-HAMB.jpg", dir: "Hamburgo esq. Florencia, Col. Ju\xE1rez, CDMX" },
  { id: "OPP-MEGA", lat: 19.356059, lng: -99.144004, n: "Mega Valla \xB7 Churubusco", med: "108 \xD7 3.05 m", imp: 12e5, precio: "$630,000", t: 63e4, img: SS + "MPCX-19072-A.jpg", dir: "Calz. de Tlalpan esq. R\xEDo Churubusco, Coyoac\xE1n, CDMX" },
  { id: "OPP-SAT", lat: 19.5092, lng: -99.2372, n: "Muro Galer\xEDas Sat\xE9lite \xB7 Fachada", med: "44 \xD7 8 m \xB7 3 caras", imp: 54e5, precio: "$750,000", t: 75e4, img: SS + "OPP-SAT.jpg", dir: "Perif\xE9rico Norte, Galer\xEDas Sat\xE9lite, Naucalpan" },
  { id: "OPP-TOREO", lat: 19.4598, lng: -99.2155, n: "Landmark Toreo \xB7 Perif\xE9rico", med: "Lona \xB7 43.4 \xD7 5.2 m", imp: 63e5, precio: "$1,000,000", t: 1e6, img: SS + "OPP-TOREO.jpg", dir: "Perif\xE9rico Norte, Toreo, Naucalpan" },
  { id: "OPP-GLORIETA", lat: 19.39, lng: -99.2925, n: "Landmark Glorieta Interlomas \xB7 Walmart", med: "Glorieta 60 \xD7 29 m \xB7 Spark 19 m", imp: 22e5, precio: "$1,200,000", t: 12e5, img: SS + "GLORIETA-LMK.jpg", dir: "Glorieta Av. San Mateo Santa Rosa / Blvd. Palmas Hills, Interlomas" },
  { id: "OPP-PANTALLAS", lat: 19.3958, lng: -99.281, n: "Landmark DOOH \xB7 6 Pantallas Premium", med: "6 pantallas LED \xB7 DOOH 3D", imp: 22e6, precio: "Cotizar", t: 0, img: SS + "OPP-PANTALLAS.jpg", dir: "CDMX y \xC1rea Metropolitana" }
];
const fmt = (n) => "$" + Number(n || 0).toLocaleString("es-MX");
const impf = (n) => Number(n || 0).toLocaleString("es-MX");
const impShort = (n) => n >= 1e6 ? (n / 1e6).toFixed(1).replace(".0", "") + " M" : n ? Math.round(n / 1e3) + " K" : "\u2014";
const enc = (x) => encodeURIComponent(x);
const b64 = (u8) => {
  let s = "";
  const CH2 = 8192;
  for (let i = 0; i < u8.length; i += CH2) s += String.fromCharCode(...u8.subarray(i, i + CH2));
  return btoa(s);
};
const b64utf8 = (s) => btoa(unescape(encodeURIComponent(s)));
const unb64utf8 = (s) => decodeURIComponent(escape(atob(s)));
const m2 = (med) => {
  const m = String(med).match(/([\d.]+)\s*[x×]\s*([\d.]+)/);
  return m ? (parseFloat(m[1]) * parseFloat(m[2])).toFixed(1) : "";
};
async function grab(u) {
  const r = await fetch(u);
  if (!r.ok) throw new Error("fetch " + r.status);
  return new Uint8Array(await r.arrayBuffer());
}
function selAll(d) {
  return [...(d.reservados || []).map((x) => ({ ...x, est: "RESERVADO" })), ...(d.bloqueados || []).map((x) => ({ ...x, est: "EN PROPUESTA" }))];
}
async function buildXlsx(d) {
  const wb = new Workbook();
  const ws = wb.addWorksheet("Ficha tecnica OOH", { views: [{ showGridLines: false, state: "frozen", ySplit: 5 }] });
  const cols = ["Clave", "Direcci\xF3n", "Municipio", "Entidad", "Latitud", "Longitud", "Vista", "Dimensiones", "m2", "Tipo", "Audiencia", "Impactos/mes", "Tarifa Mensual"];
  const wds = [14, 34, 18, 18, 11, 11, 10, 16, 9, 18, 26, 15, 16];
  ws.columns = cols.map((_h, i) => ({ width: wds[i] }));
  ws.getRow(2).height = 40;
  ws.getRow(3).height = 50;
  ws.getRow(4).height = 12;
  ws.getRow(5).height = 40;
  ws.mergeCells("A3:G3");
  const t = ws.getCell("A3");
  t.value = "Connectia \xD7 Walmart \xB7 Inventario OOH Interlomas";
  t.font = { name: "Inter", bold: true, size: 22, color: { argb: "FF000000" } };
  t.alignment = { vertical: "middle" };
  try {
    const cw = await grab(BASE + "/assets/connectia-violet.png");
    const id = wb.addImage({ buffer: cw, extension: "png" });
    ws.addImage(id, { tl: { col: 0, row: 1 }, ext: { width: 130, height: 34 } });
  } catch (_e) {
  }
  try {
    const wm = await grab(BASE + "/assets/walmart-full-rgba.png");
    const id = wb.addImage({ buffer: wm, extension: "png" });
    ws.addImage(id, { tl: { col: 10, row: 1 }, ext: { width: 150, height: 28 } });
  } catch (_e) {
  }
  const hr = ws.getRow(5);
  cols.forEach((h, i) => {
    const c = hr.getCell(i + 1);
    c.value = h;
    c.fill = { type: "pattern", pattern: "solid", fgColor: { argb: "FF6030A0" } };
    c.font = { name: "Inter", bold: true, size: 11, color: { argb: "FFFFFFFF" } };
    c.alignment = { horizontal: "center", vertical: "middle", wrapText: true };
  });
  const money = '"$"#,##0.00';
  const sel = selAll(d);
  sel.forEach((x, i) => {
    const p = POI[x.id] || {};
    const r = ws.getRow(6 + i);
    r.height = 17;
    const vals = [x.id, p.dir || "", p.mun || "Huixquilucan", p.ent || "Estado de M\xE9xico", p.lat || "", p.lng || "", "Natural", p.med || "", m2(p.med || ""), p.tipo || "", p.aud || "", p.imp || "", x.tarifa || 0];
    vals.forEach((v, j) => {
      const c = r.getCell(j + 1);
      c.value = v;
      c.font = { name: "Inter", bold: true, size: 11, color: { argb: "FF000000" } };
      c.fill = { type: "pattern", pattern: "solid", fgColor: { argb: "FFFFFFFF" } };
      c.alignment = { vertical: "middle", horizontal: j >= 4 && j <= 5 || j === 8 || j === 11 ? "center" : "left" };
      if (j === 12) c.numFmt = money;
      if (j === 11) c.numFmt = "#,##0";
    });
  });
  const tr = ws.getRow(6 + sel.length + 1);
  tr.height = 22;
  ws.mergeCells("A" + tr.number + ":L" + tr.number);
  const tc = tr.getCell(1);
  tc.value = "TOTAL MENSUAL";
  tc.fill = { type: "pattern", pattern: "solid", fgColor: { argb: "FF6030A0" } };
  tc.font = { name: "Inter", bold: true, size: 12, color: { argb: "FFFFFFFF" } };
  tc.alignment = { horizontal: "right", vertical: "middle" };
  const tv = tr.getCell(13);
  tv.value = d.total || 0;
  tv.fill = { type: "pattern", pattern: "solid", fgColor: { argb: "FF6030A0" } };
  tv.font = { name: "Inter", bold: true, size: 12, color: { argb: "FFFFFFFF" } };
  tv.numFmt = money;
  tv.alignment = { horizontal: "center", vertical: "middle" };
  const buf = await wb.xlsx.writeBuffer();
  return b64(new Uint8Array(buf));
}
const CI = rgb(32 / 255, 16 / 255, 64 / 255), CV = rgb(96 / 255, 48 / 255, 160 / 255), CH = rgb(123 / 255, 63 / 255, 242 / 255), CD = rgb(26 / 255, 11 / 255, 61 / 255), CW = rgb(1, 1, 1), CP = rgb(250 / 255, 250 / 255, 251 / 255), CY = rgb(1, 194 / 255, 32 / 255);
function wrap(txt, font, size, maxW) {
  const words = String(txt).split(" ");
  const lines = [];
  let cur = "";
  for (const w of words) {
    const test = cur ? cur + " " + w : w;
    if (font.widthOfTextAtSize(test, size) > maxW && cur) {
      lines.push(cur);
      cur = w;
    } else cur = test;
  }
  if (cur) lines.push(cur);
  return lines;
}
async function buildPdfDoc(d) {
  const pdf = await PDFDocument.create();
  const F = await pdf.embedFont(StandardFonts.Helvetica), FB = await pdf.embedFont(StandardFonts.HelveticaBold), FI = await pdf.embedFont(StandardFonts.HelveticaOblique);
  const W = 612, H = 792;
  const conW = await pdf.embedPng(await grab(BASE + "/assets/connectia-white.png"));
  let spark = null;
  try {
    spark = await pdf.embedPng(await grab(BASE + "/assets/walmart-spark-rgba.png"));
  } catch (_e) {
  }
  let p = pdf.addPage([W, H]);
  p.drawRectangle({ x: 0, y: 0, width: W, height: H, color: CI });
  p.drawRectangle({ x: 0, y: 0, width: W, height: H * 0.42, color: CV, opacity: 0.55 });
  p.drawRectangle({ x: 0, y: 0, width: W, height: H * 0.18, color: CH, opacity: 0.28 });
  const cwd = conW.scale(160 / conW.width);
  p.drawImage(conW, { x: 56, y: H - 74, width: cwd.width, height: cwd.height });
  if (spark) {
    const s = spark.scale(48 / spark.width);
    p.drawImage(spark, { x: W - 56 - s.width, y: H - 78, width: s.width, height: s.height });
  }
  p.drawText("CONNECTIA \xD7 WALMART \xB7 OUT OF NOISE", { x: 56, y: H - 155, size: 9, font: FB, color: CH });
  p.drawText("Connectia \xD7 Walmart", { x: 54, y: H - 215, size: 40, font: FB, color: CW });
  p.drawText("Propuesta Out of Home", { x: 56, y: H - 249, size: 16, font: F, color: CW });
  p.drawText("Recorrido Interlomas \xB7 Ficha t\xE9cnica por sitio", { x: 56, y: H - 271, size: 12, font: F, color: rgb(0.8, 0.78, 0.9) });
  p.drawText("Presencia premium en el corredor de mayor plusvalia del poniente.", { x: 56, y: 120, size: 12, font: FI, color: rgb(0.85, 0.83, 0.92) });
  for (const x of selAll(d)) {
    const pp = POI[x.id] || {};
    p = pdf.addPage([W, H]);
    p.drawRectangle({ x: 0, y: 0, width: W, height: H, color: CP });
    try {
      const img = await pdf.embedJpg(await grab(BASE + "/" + pp.wm));
      p.drawImage(img, { x: 0, y: H - 250, width: W, height: 250 });
    } catch (_e) {
      p.drawRectangle({ x: 0, y: H - 250, width: W, height: 250, color: CI });
    }
    p.drawRectangle({ x: 0, y: H - 250, width: W, height: 34, color: CI, opacity: 0.55 });
    p.drawText((x.est || "").toUpperCase(), { x: 24, y: H - 240, size: 10, font: FB, color: CY });
    let y = H - 288;
    p.drawText(((pp.tipo || "") + " \xB7 " + (pp.med || "")).toUpperCase(), { x: 44, y, size: 9, font: FB, color: CH });
    y -= 26;
    p.drawText((x.nombre || pp.n || "").slice(0, 46), { x: 42, y, size: 22, font: FB, color: CI });
    y -= 30;
    const stats = [["Tarifa mensual", x.tarifa ? fmt(x.tarifa) : "Cotizar"], ["Impactos/mes", impf(pp.imp)], ["Audiencia", pp.aud || "\u2014"], ["Nivel de impacto", pp.niv || "Alto"], ["Medidas", pp.med || "\u2014"], ["Tipo", pp.tipo || "\u2014"], ["Coordenadas", (pp.lat || "") + ", " + (pp.lng || "")], ["Disponibilidad", "Disponible"]];
    const colX = [44, 320];
    let gy = y;
    stats.forEach((s, i) => {
      const cx = colX[i % 2];
      if (i % 2 === 0 && i > 0) gy -= 46;
      p.drawText(s[0].toUpperCase(), { x: cx, y: gy, size: 8, font: F, color: rgb(0.45, 0.42, 0.5) });
      p.drawText(String(s[1]).slice(0, 30), { x: cx, y: gy - 15, size: 12, font: FB, color: i === 0 ? CV : CD });
    });
    y = gy - 40;
    p.drawText("BENEFICIO PARA WALMART", { x: 44, y, size: 9, font: FB, color: CH });
    y -= 16;
    wrap(pp.ben || "Presencia estrat\xE9gica de Walmart en un punto de alto flujo.", F, 11, W - 88).forEach((ln) => {
      p.drawText(ln, { x: 44, y, size: 11, font: F, color: CD });
      y -= 15;
    });
    y -= 12;
    p.drawText("CADENAS CERCANAS", { x: 44, y, size: 9, font: FB, color: CH });
    y -= 16;
    p.drawText(pp.cad || "Walmart y Bodega Aurrer\xE1 a la redonda", { x: 44, y, size: 11, font: FB, color: CD });
    p.drawText("Recuerda: la disponibilidad cambia dia con dia \xB7 Sujeto a confirmacion.", { x: 44, y: 46, size: 9, font: FI, color: rgb(0.6, 0.55, 0.75) });
  }
  p = pdf.addPage([W, H]);
  p.drawRectangle({ x: 0, y: 0, width: W, height: H, color: CP });
  p.drawText("RESUMEN", { x: 56, y: H - 80, size: 9, font: FB, color: CH });
  p.drawText("Total de la propuesta", { x: 54, y: H - 108, size: 26, font: FB, color: CI });
  let yy = H - 150;
  selAll(d).forEach((x) => {
    p.drawText((x.nombre || "").slice(0, 44), { x: 56, y: yy, size: 12, font: FB, color: CD });
    const tt = x.tarifa ? fmt(x.tarifa) : "Cotizar";
    p.drawText(tt, { x: W - 56 - FB.widthOfTextAtSize(tt, 12), y: yy, size: 12, font: FB, color: CV });
    yy -= 24;
  });
  p.drawRectangle({ x: 48, y: yy - 42, width: W - 96, height: 40, color: CV });
  p.drawText("TOTAL MENSUAL", { x: 64, y: yy - 28, size: 13, font: FB, color: CW });
  const gt = fmt(d.total);
  p.drawText(gt, { x: W - 64 - FB.widthOfTextAtSize(gt, 15), y: yy - 28, size: 15, font: FB, color: CW });
  p = pdf.addPage([W, H]);
  p.drawRectangle({ x: 0, y: 0, width: W, height: H, color: CI });
  const cc = conW.scale(180 / conW.width);
  p.drawImage(conW, { x: (W - cc.width) / 2, y: H / 2 + 24, width: cc.width, height: cc.height });
  const af = "\xABEl tiempo es lo mas valioso que tenemos, gracias por regalarnos un poco de el.\xBB";
  wrap(af, FI, 14, W - 120).forEach((ln, i) => {
    p.drawText(ln, { x: (W - FI.widthOfTextAtSize(ln, 14)) / 2, y: H / 2 - 12 - i * 20, size: 14, font: FI, color: CW });
  });
  return await pdf.save();
}
async function buildPdf(d) {
  return b64(await buildPdfDoc(d));
}
async function buildFichaPdf(it) {
  const d = { reservados: [{ id: it.id, nombre: it.n, tarifa: it.t || 0 }], bloqueados: [], total: it.t || 0 };
  if (!POI[it.id]) {
    POI[it.id] = { n: it.n, med: it.med, imp: it.imp, tipo: "OOH", dir: it.dir, aud: "\u2014", niv: "Alto", ben: "Oportunidad premium fuera de ruta.", cad: "Consultar cadenas a la redonda", wm: (it.img || "").replace(BASE + "/", ""), lat: "", lng: "" };
  }
  return await buildPdfDoc(d);
}
function fichaRows(items, label, color) {
  if (!items.length) return "";
  const rows = items.map((x) => {
    const p = POI[x.id] || {};
    return "<tr><td style='padding:10px 0;border-bottom:1px solid #33224f'><div style='color:#fff;font-weight:bold;font-size:14px'>" + x.nombre + "</div><div style='color:#9b8fc0;font-size:11px;margin-top:2px'>" + (p.tipo || "") + " \xB7 " + (p.med || "") + " \xB7 <b style='color:#C8FF00'>" + impf(p.imp) + " imp/mes</b></div></td><td align='right' style='border-bottom:1px solid #33224f;color:#FFC220;font-weight:bold;font-size:14px;white-space:nowrap;vertical-align:top;padding-top:10px'>" + (x.tarifa ? fmt(x.tarifa) + "/mes" : "Cotizar") + "</td></tr>";
  }).join("");
  return "<tr><td colspan='2' style='padding:14px 0 4px;color:" + color + ";font-size:11px;letter-spacing:2px;font-weight:bold'>" + label + "</td></tr>" + rows;
}
function interesCards(pool) {
  return pool.map((it) => {
    const dl = FN + "?action=ficha&id=" + enc(it.id);
    const geo = it.lat && it.lng ? geoPoint(it.lat, it.lng) : GEOROOT;
    return "<table width='100%' cellpadding='0' cellspacing='0' style='margin:12px 0;background:#1b0f38;border-radius:16px;overflow:hidden;border:1px solid #3a2568'><tr><td style='padding:0'><table width='100%' cellpadding='0' cellspacing='0'><tr><td style='width:100%;height:170px;background-image:url(" + it.img + ");background-size:cover;background-position:center center'><div style='height:170px;background:linear-gradient(180deg,rgba(20,8,40,0),rgba(20,8,40,.55))'></div></td></tr></table><div style='padding:16px 18px'><div style='color:#fff;font-weight:800;font-size:16px;line-height:1.2'>" + it.n + "</div><div style='color:#9b8fc0;font-size:12px;margin:5px 0 3px'>" + it.med + "</div><div style='margin:6px 0 10px'><span style='background:#C8FF00;color:#201040;font-weight:900;font-size:13px;padding:3px 10px;border-radius:8px'>" + impShort(it.imp) + " impactos/mes</span></div><div style='color:#FFC220;font-weight:bold;font-size:15px;margin-bottom:12px'>" + (it.precio || (it.t ? fmt(it.t) : "Cotizar")) + (it.t ? " /mes" : "") + "</div><table width='100%' cellpadding='0' cellspacing='0'><tr><td width='50%' style='padding-right:5px'><a href='" + dl + "' style='display:block;text-align:center;background:linear-gradient(135deg,#6030A0,#E01C8A);color:#fff;text-decoration:none;padding:12px;border-radius:10px;font-weight:bold;font-size:13px'>Descargar ficha</a></td><td width='50%' style='padding-left:5px'><a href='" + geo + "' style='display:block;text-align:center;background:#2a1a52;border:1px solid #6030A0;color:#cdbff0;text-decoration:none;padding:12px;border-radius:10px;font-weight:bold;font-size:13px'>Ver en mapa</a></td></tr></table></div></td></tr></table>";
  }).join("");
}
function poolInteres(d) {
  const used = new Set(selAll(d).map((x) => x.id));
  const sitios = Object.keys(POI).filter((id) => !used.has(id)).map((id) => ({ id, n: POI[id].n, med: POI[id].med, imp: POI[id].imp, t: POI[id].t, precio: POI[id].t ? fmt(POI[id].t) : "Cotizar", img: BASE + "/" + POI[id].wm, dir: POI[id].dir, lat: POI[id].lat, lng: POI[id].lng }));
  const opps = OPORT.filter((o) => !used.has(o.id));
  return sitios.concat(opps);
}
function newsletter(d) {
  const nombre = (d.nombre || (d.correo || "").split("@")[0] || "").toString();
  const saludo = nombre ? "Hola " + nombre.charAt(0).toUpperCase() + nombre.slice(1) : "Hola";
  const dparam = enc(b64utf8(JSON.stringify({ correo: d.correo, nombre: d.nombre || "", reservados: d.reservados || [], bloqueados: d.bloqueados || [], total: d.total || 0 })));
  const pdfUrl = FN + "?action=pdf&d=" + dparam, xlsUrl = FN + "?action=xlsx&d=" + dparam;
  const fichas = fichaRows(d.reservados || [], "RESERVADOS", "#7B3FF2") + fichaRows(d.bloqueados || [], "EN PROPUESTA", "#FFC220");
  return "<!DOCTYPE html><html><body style='margin:0;background:#0A0118;font-family:Arial,Helvetica,sans-serif'><table width='100%' cellpadding='0' cellspacing='0'><tr><td align='center' style='padding:28px 12px'><table width='600' cellpadding='0' cellspacing='0' style='max-width:600px'><tr><td style='background:linear-gradient(140deg,#1A0B3D 0%,#5A1B82 38%,#E01C8A 74%,#FF6A1A 100%);border-radius:22px;padding:44px 30px;text-align:center'><img src='" + LOGO + "' height='58' style='display:inline-block;margin-bottom:18px' alt='Connectia'><div style='color:rgba(255,255,255,.85);font-size:11px;letter-spacing:3px'>CONNECTIA \xD7 WALMART \xB7 OUT OF NOISE</div><h1 style='color:#fff;margin:12px 0 6px;font-size:26px'>" + saludo + ", gracias por acompa\xF1arnos</h1><div style='color:rgba(255,255,255,.92);font-size:14px'>Tu propuesta va adjunta en <b>PDF + Excel</b> con la ficha t\xE9cnica de cada sitio.</div></td></tr><tr><td style='padding:14px 6px 0;color:#6B6580;font-size:12px'>Enviado a: <b style='color:#E9E6F0'>" + d.correo + "</b></td></tr><tr><td style='padding:18px 6px 0'><div style='background:#160b31;border-radius:18px;padding:22px'><div style='color:#7B3FF2;font-size:11px;letter-spacing:2px;font-weight:bold'>TU SELECCI\xD3N \xB7 FICHA T\xC9CNICA</div><table width='100%' style='margin-top:6px'>" + fichas + "<tr><td style='padding-top:14px;color:#fff;font-weight:bold'>TOTAL MENSUAL</td><td align='right' style='padding-top:14px;color:#FFC220;font-weight:bold'>" + fmt(d.total) + "</td></tr></table><table width='100%' cellpadding='0' cellspacing='0' style='margin-top:14px'><tr><td width='50%' style='padding-right:5px'><a href='" + pdfUrl + "' style='display:block;text-align:center;background:linear-gradient(135deg,#E01C8A,#FF6A1A);color:#fff;text-decoration:none;padding:14px;border-radius:12px;font-weight:bold;font-size:13px'>\u2B07 Descargar PDF</a></td><td width='50%' style='padding-left:5px'><a href='" + xlsUrl + "' style='display:block;text-align:center;background:#0b7a3b;color:#fff;text-decoration:none;padding:14px;border-radius:12px;font-weight:bold;font-size:13px'>\u2B07 Descargar Excel</a></td></tr></table><a href='" + geoShare(d) + "' style='display:block;margin-top:10px;background:#201040;border:1px solid #6030A0;color:#cdbff0;text-decoration:none;text-align:center;padding:13px;border-radius:12px;font-weight:bold;font-size:13px'>Ver los sitios en Geonexa</a></div></td></tr><tr><td style='padding:14px 6px 0'><div style='background:#2a1030;border:1px dashed #E01C8A;border-radius:12px;padding:14px;color:#ffd9ee;font-size:12px;text-align:center'>\u26A0\uFE0F Recuerda que la disponibilidad cambia d\xEDa con d\xEDa. Todo est\xE1 sujeto a confirmaci\xF3n.</div></td></tr><tr><td style='padding:26px 6px 6px;text-align:center'><div style='color:#C8FF00;font-size:12px;letter-spacing:3px;font-weight:900'>TE PUEDE INTERESAR</div><div style='color:#9b8fc0;font-size:11px;margin:4px 0 2px'>M\xE1s sitios del recorrido y oportunidades premium para Walmart</div></td></tr><tr><td style='padding:0 6px'>" + interesCards(poolInteres(d)) + "</td></tr><tr><td style='padding:30px 20px 8px;text-align:center'><div style='background:linear-gradient(135deg,#6030A0,#E01C8A);border-radius:20px;padding:30px 24px'><div style='color:#fff;font-weight:900;font-style:italic;font-size:21px;line-height:1.35'>\xABEl tiempo es lo m\xE1s valioso que tenemos, gracias por regalarnos un poco de \xE9l.\xBB</div></div><div style='color:#6B6580;font-size:12px;margin-top:14px'>Atentamente, todo el equipo de Connectia \xB7 hola@connectia.mx</div></td></tr></table></td></tr></table></body></html>";
}
async function sendMail(body) {
  const r = await fetch("https://api.resend.com/emails", { method: "POST", headers: { Authorization: "Bearer " + RESEND_KEY, "Content-Type": "application/json" }, body: JSON.stringify(body) });
  return { ok: r.ok, txt: r.ok ? "" : await r.text() };
}
async function handle(req) {
  if (req.method === "OPTIONS") return new Response(null, { headers: CORS });
  const url = new URL(req.url);
  const action = url.searchParams.get("action");
  if (req.method === "GET" && action === "ficha") {
    const id = url.searchParams.get("id") || "";
    let it = OPORT.find((x) => x.id === id);
    if (!it && POI[id]) {
      const p = POI[id];
      it = { id, n: p.n, med: p.med, imp: p.imp, t: p.t, dir: p.dir, img: BASE + "/" + p.wm };
    }
    if (!it) return new Response("no encontrado", { status: 404, headers: CORS });
    const pdf = await buildFichaPdf(it);
    return new Response(pdf, { headers: { ...CORS, "Content-Type": "application/pdf", "Content-Disposition": 'attachment; filename="Ficha-' + id + '.pdf"' } });
  }
  if (req.method === "GET" && (action === "pdf" || action === "xlsx")) {
    try {
      const d = JSON.parse(unb64utf8(decodeURIComponent(url.searchParams.get("d") || "")));
      if (action === "pdf") {
        const bytes = await buildPdfDoc(d);
        return new Response(bytes, { headers: { ...CORS, "Content-Type": "application/pdf", "Content-Disposition": 'attachment; filename="Connectia-Walmart-Propuesta.pdf"' } });
      }
      const xb = await buildXlsx(d);
      const u8 = Uint8Array.from(atob(xb), (c) => c.charCodeAt(0));
      return new Response(u8, { headers: { ...CORS, "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "Content-Disposition": 'attachment; filename="Connectia-Walmart-Inventario.xlsx"' } });
    } catch (e) {
      return new Response("error: " + String(e), { status: 400, headers: CORS });
    }
  }
  try {
    const d = await req.json();
    if (!d.correo) throw new Error("correo requerido");
    const surl = Deno.env.get("SUPABASE_URL"), skey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
    await fetch(surl + "/rest/v1/recorrido_leads", { method: "POST", headers: { apikey: skey, Authorization: "Bearer " + skey, "Content-Type": "application/json", Prefer: "return=minimal" }, body: JSON.stringify({ correo: d.correo, reservados: d.reservados || [], bloqueados: d.bloqueados || [], total: d.total || 0 }) });
    const att = [];
    try {
      att.push({ filename: "Connectia-Walmart-Inventario-OOH.xlsx", content: await buildXlsx(d) });
    } catch (_e) {
    }
    try {
      att.push({ filename: "Connectia-Walmart-Propuesta-OOH.pdf", content: await buildPdf(d) });
    } catch (_e) {
    }
    const m = await sendMail({ from: FROM, to: [d.correo], cc: CC, reply_to: "hola@connectia.mx", subject: "Gracias por acompa\xF1arnos \xB7 Connectia \xD7 Walmart", html: newsletter(d), attachments: att });
    return new Response(JSON.stringify({ ok: true, mailed: m.ok, mailErr: m.txt, att: att.length }), { headers: { ...CORS, "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 400, headers: { ...CORS, "Content-Type": "application/json" } });
  }
}
export {
  handle
};
