import { Workbook } from "https://esm.sh/exceljs@4.4.0?target=deno";
import { PDFDocument, rgb, StandardFonts } from "https://esm.sh/pdf-lib@1.17.1?target=deno";
const CORS = { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "content-type", "Access-Control-Allow-Methods": "POST, GET, OPTIONS" };
const RESEND_KEY = Deno.env.get("RESEND_API_KEY") || "re_QZq5i5qa_JuXadcavBPmGYhWWK31YWgbq";
const FROM = "Connectia <hola@connectia.mx>";
const CC = ["rhernandez@connectia.mx"];
const AVISO = "rhernandez@connectia.mx";
const FN = "https://mduxlmnlwycwknyapwsx.supabase.co/functions/v1/recorrido-checkout";
const BASE = "https://connectia.mx/RecorridoAdri";
const LOGO = BASE + "/assets/connectia-white.png";
const POI = {
  "EEM-0819-A": { n: "Cubo Digital Magnocentro \xB7 Interlomas", lat: 19.402051, lng: -99.271914, med: "18.7 \xD7 10 m", imp: 4e6, tipo: "Cubo digital", t: 1e6, dir: "Blvd. Magnocentro y Blvd. Interlomas", col: "Interlomas", mun: "Huixquilucan", ent: "Estado de M\xE9xico", cp: "52760", wm: "assets/sitios/EEM-0819-A-wm.jpg" },
  "EEM-18177-B": { n: "Pantalla LED Toreo \xB7 Perif\xE9rico", lat: 19.460182, lng: -99.222014, med: "17.28 \xD7 8.64 m", imp: 0, tipo: "Pantalla LED digital", t: 0, dir: "Blvd. M. \xC1vila Camacho (Perif\xE9rico) y Av. Emiliano Zapata", col: "San Francisco Cuautlalpan", mun: "Naucalpan de Ju\xE1rez", ent: "Estado de M\xE9xico", cp: "53569", wm: "assets/sitios/EEM-18177-B-wm.jpg" },
  "GLORIETA-LMK": { n: "Landmark Glorieta Interlomas \xB7 Walmart", lat: 19.39, lng: -99.2925, med: "Glorieta 60 \xD7 29 m \xB7 Spark 19 m", imp: 22e5, tipo: "Landmark volum\xE9trico + Pantalla 3D", t: 12e5, dir: "Glorieta Av. San Mateo Santa Rosa / Blvd. Palmas Hills", col: "Interlomas", mun: "Huixquilucan", ent: "Estado de M\xE9xico", cp: "52786", wm: "assets/sitios/GLORIETA-LMK-wm.jpg" },
  "EEM-17672-A": { n: "Pantalla LED Paseo Interlomas", lat: 19.396232, lng: -99.281112, med: "15.36 \xD7 3.84 m", imp: 1835257, tipo: "Pantalla LED", t: 48e4, dir: "Vialidad frente a Paseo Interlomas", col: "Interlomas", mun: "Huixquilucan", ent: "Estado de M\xE9xico", cp: "52760", wm: "assets/sitios/EEM-17672-A-wm.jpg" },
  "EEM-17672-B": { n: "Puente Paseo Interlomas", lat: 19.3968, lng: -99.2816, med: "15.10 \xD7 3.80 m", imp: 9e5, tipo: "Puente peatonal", t: 32e4, dir: "Frente a Hospital \xC1ngeles Interlomas", col: "Interlomas", mun: "Huixquilucan", ent: "Estado de M\xE9xico", cp: "52760", wm: "assets/sitios/EEM-17672-B-wm.jpg" },
  "BEM-17344-A": { n: "Muro CC Interlomas", lat: 19.396262, lng: -99.288435, med: "8.00 \xD7 15.00 m", imp: 11e5, tipo: "Muro", t: 35e4, dir: "Entrada CC Interlomas", col: "Interlomas", mun: "Huixquilucan", ent: "Estado de M\xE9xico", cp: "52760", wm: "assets/sitios/BEM-17344-A-wm.jpg" },
  "EEM-17427-B": { n: "Puente Hueyetlaco", lat: 19.387794, lng: -99.278823, med: "10.60 \xD7 5.20 m", imp: 85e4, tipo: "Puente peatonal", t: 28e4, dir: "Circulaci\xF3n Santa Fe hacia Interlomas", col: "Hueyetlaco", mun: "Huixquilucan", ent: "Estado de M\xE9xico", cp: "52765", wm: "assets/sitios/EEM-17427-B-wm.jpg" },
  "EEM-15935-B": { n: "Unipolar Vialidad de la Barranca", lat: 19.388173, lng: -99.2786, med: "12.90 \xD7 10.80 m", imp: 14e5, tipo: "Unipolar", t: 42e4, dir: "Vialidad de la Barranca hacia Santa Fe", col: "Bosques de las Lomas", mun: "Huixquilucan", ent: "Estado de M\xE9xico", cp: "52786", wm: "assets/sitios/EEM-15935-B-wm.jpg" }
};
const SS = BASE + "/assets/sitios/";
const INTERES = [
  { id: "LMK-HAMB", n: "Landmark Hamb\xFArgo \xB7 Col. Ju\xE1rez", med: "16 \xD7 6.5 m \xB7 Pantalla LED", imp: 21e5, precio: "$550,000", t: 55e4, img: SS + "CXCX-19000-A.jpg" },
  { id: "LMK-CUBO", n: "Landmark Cubo + Naming \xB7 Interlomas", med: "4 caras \xB7 18.7 \xD7 10 m", imp: 62e5, precio: "$1,000,000", t: 1e6, img: SS + "EEM-0819-A.jpg" },
  { id: "LMK-MEGA", n: "Mega Valla Churubusco \xB7 CDMX", med: "108 \xD7 3.05 m", imp: 5e6, precio: "Cotizar", t: 0, img: SS + "MPCX-19072-A.jpg" },
  { id: "MURO-TLA1", n: "Muro Tlalnepantla \xB7 \xC1vila Camacho 2610", med: "71 \xD7 26 m", imp: 62e5, precio: "$1,116,000", t: 1116e3, img: SS + "LMK-p3.jpg" },
  { id: "MURO-TLA2", n: "Muro Tlalnepantla 2610-B", med: "48 \xD7 25 m", imp: 62e5, precio: "$369,230", t: 369230, img: SS + "LMK-p4.jpg" },
  { id: "MURO-SAT1", n: "Muro Galer\xEDas Sat\xE9lite \xB7 Fachada", med: "44 \xD7 8 m", imp: 54e5, precio: "$750,000", t: 75e4, img: SS + "LMK-p5.jpg" },
  { id: "MURO-SAT2", n: "Muro Galer\xEDas Sat\xE9lite 2150-A", med: "24.6 \xD7 7.3 m", imp: 54e5, precio: "$207,296", t: 207296, img: SS + "LMK-p6.jpg" },
  { id: "MURO-SAT3", n: "Muro Galer\xEDas Sat\xE9lite 2150-B", med: "15 \xD7 10 m", imp: 54e5, precio: "$207,692", t: 207692, img: SS + "LMK-p7.jpg" },
  { id: "MURO-NAU", n: "Muro Naucalpan \xB7 \xC1vila Camacho 495", med: "12 \xD7 12 m", imp: 42e5, precio: "Cotizar", t: 0, img: SS + "LMK-p8.jpg" }
];
const fmt = (n) => "$" + Number(n || 0).toLocaleString("es-MX");
const impf = (n) => Number(n || 0).toLocaleString("es-MX");
const enc = (x) => encodeURIComponent(x);
const b64 = (u8) => {
  let s = "";
  const CH2 = 8192;
  for (let i = 0; i < u8.length; i += CH2) s += String.fromCharCode(...u8.subarray(i, i + CH2));
  return btoa(s);
};
const m2 = (med) => {
  const m = String(med).match(/([\d.]+)\s*[x×]\s*([\d.]+)/);
  return m ? (parseFloat(m[1]) * parseFloat(m[2])).toFixed(1) : "";
};
async function grab(u) {
  const r = await fetch(u);
  if (!r.ok) throw new Error("fetch " + r.status);
  return new Uint8Array(await r.arrayBuffer());
}
function pick3() {
  const a = INTERES.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a.slice(0, 3);
}
function selAll(d) {
  return [...(d.reservados || []).map((x) => ({ ...x, est: "RESERVADO" })), ...(d.bloqueados || []).map((x) => ({ ...x, est: "EN PROPUESTA" }))];
}
function mapsUrl(d) {
  const pts = selAll(d).map((x) => POI[x.id]).filter(Boolean).map((p) => p.lat + "," + p.lng);
  if (!pts.length) return BASE + "/?view=mapa";
  if (pts.length === 1) return "https://www.google.com/maps/search/?api=1&query=" + pts[0];
  return "https://www.google.com/maps/dir/" + pts.join("/");
}
async function buildXlsx(d) {
  const wb = new Workbook();
  const ws = wb.addWorksheet("Ficha tecnica OOH", { views: [{ showGridLines: false, state: "frozen", ySplit: 5 }] });
  const cols = ["Clave", "Direcci\xF3n", "Colonia", "Municipio", "Entidad", "C.P.", "Latitud", "Longitud", "Vista", "Dimensiones", "m2", "Tipo de estructura", "Tipo de lona", "Impactos/mes", "Tarifa Mensual"];
  const wds = [14, 30, 16, 16, 18, 8, 11, 11, 12, 14, 9, 18, 14, 14, 16];
  ws.columns = cols.map((_h, i) => ({ width: wds[i] }));
  ws.getRow(2).height = 40;
  ws.getRow(3).height = 50;
  ws.getRow(4).height = 12;
  ws.getRow(5).height = 40;
  ws.mergeCells("A3:H3");
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
    ws.addImage(id, { tl: { col: 12, row: 1 }, ext: { width: 150, height: 28 } });
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
    const vals = [x.id, p.dir || "", p.col || "", p.mun || "", p.ent || "", p.cp || "", p.lat || "", p.lng || "", "Natural", p.med || "", m2(p.med || ""), p.tipo || "", "Lona/Digital", p.imp || "", x.tarifa || 0];
    vals.forEach((v, j) => {
      const c = r.getCell(j + 1);
      c.value = v;
      c.font = { name: "Inter", bold: true, size: 11, color: { argb: "FF000000" } };
      c.fill = { type: "pattern", pattern: "solid", fgColor: { argb: "FFFFFFFF" } };
      c.alignment = { vertical: "middle", horizontal: j >= 6 && j <= 7 || j === 10 || j === 13 ? "center" : "left" };
      if (j === 14) c.numFmt = money;
      if (j === 13) c.numFmt = "#,##0";
    });
  });
  const tr = ws.getRow(6 + sel.length + 1);
  tr.height = 22;
  ws.mergeCells("A" + tr.number + ":N" + tr.number);
  const tc = tr.getCell(1);
  tc.value = "TOTAL MENSUAL";
  tc.fill = { type: "pattern", pattern: "solid", fgColor: { argb: "FF6030A0" } };
  tc.font = { name: "Inter", bold: true, size: 12, color: { argb: "FFFFFFFF" } };
  tc.alignment = { horizontal: "right", vertical: "middle" };
  const tv = tr.getCell(15);
  tv.value = d.total || 0;
  tv.fill = { type: "pattern", pattern: "solid", fgColor: { argb: "FF6030A0" } };
  tv.font = { name: "Inter", bold: true, size: 12, color: { argb: "FFFFFFFF" } };
  tv.numFmt = money;
  tv.alignment = { horizontal: "center", vertical: "middle" };
  const buf = await wb.xlsx.writeBuffer();
  return b64(new Uint8Array(buf));
}
const CI = rgb(32 / 255, 16 / 255, 64 / 255), CV = rgb(96 / 255, 48 / 255, 160 / 255), CH = rgb(123 / 255, 63 / 255, 242 / 255), CD = rgb(26 / 255, 11 / 255, 61 / 255), CW = rgb(1, 1, 1), CP = rgb(250 / 255, 250 / 255, 251 / 255);
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
  const cwd = conW.scale(150 / conW.width);
  p.drawImage(conW, { x: 56, y: H - 70, width: cwd.width, height: cwd.height });
  if (spark) {
    const s = spark.scale(46 / spark.width);
    p.drawImage(spark, { x: W - 56 - s.width, y: H - 74, width: s.width, height: s.height });
  }
  p.drawText("CONNECTIA \xD7 WALMART \xB7 OUT OF NOISE", { x: 56, y: H - 150, size: 9, font: FB, color: CH });
  p.drawText("Connectia \xD7 Walmart", { x: 54, y: H - 210, size: 40, font: FB, color: CW });
  p.drawText("Propuesta Out of Home", { x: 56, y: H - 244, size: 16, font: F, color: CW });
  p.drawText("Recorrido Interlomas \xB7 Estado de M\xE9xico", { x: 56, y: H - 266, size: 12, font: F, color: rgb(0.8, 0.78, 0.9) });
  p.drawText("Presencia premium en el corredor de mayor plusvalia del poniente.", { x: 56, y: 120, size: 12, font: FI, color: rgb(0.85, 0.83, 0.92) });
  p = pdf.addPage([W, H]);
  p.drawRectangle({ x: 0, y: 0, width: W, height: H, color: CP });
  p.drawText("INVENTARIO PROPUESTO", { x: 56, y: H - 56, size: 9, font: FB, color: CH });
  p.drawText("Sitios seleccionados", { x: 54, y: H - 84, size: 26, font: FB, color: CI });
  let y = H - 120;
  for (const x of selAll(d)) {
    const pp = POI[x.id] || {};
    if (y < 180) {
      p = pdf.addPage([W, H]);
      p.drawRectangle({ x: 0, y: 0, width: W, height: H, color: CP });
      y = H - 70;
    }
    const cardH = 150, cardY = y - cardH;
    p.drawRectangle({ x: 48, y: cardY, width: W - 96, height: cardH, color: CW, borderColor: CV, borderWidth: 0.7 });
    try {
      const img = await pdf.embedJpg(await grab(BASE + "/" + pp.wm));
      p.drawImage(img, { x: 58, y: cardY + 10, width: 200, height: cardH - 20 });
    } catch (_e) {
    }
    const tx = 276;
    p.drawText((x.nombre || pp.n || "").slice(0, 42), { x: tx, y: cardY + cardH - 30, size: 15, font: FB, color: CI });
    const meta = [["Tipo", pp.tipo || ""], ["Medidas", pp.med || ""], ["Impactos/mes", impf(pp.imp)], ["Coordenadas", pp.lat + ", " + pp.lng], ["Estatus", x.est]];
    let my = cardY + cardH - 56;
    meta.forEach((mm) => {
      p.drawText(mm[0], { x: tx, y: my, size: 9, font: F, color: rgb(0.4, 0.4, 0.45) });
      p.drawText(String(mm[1]), { x: tx + 90, y: my, size: 9, font: FB, color: CD });
      my -= 15;
    });
    p.drawText(fmt(x.tarifa) + " /mes", { x: tx, y: cardY + 14, size: 15, font: FB, color: CV });
    y = cardY - 16;
  }
  if (y < 90) {
    p = pdf.addPage([W, H]);
    p.drawRectangle({ x: 0, y: 0, width: W, height: H, color: CP });
    y = H - 90;
  }
  p.drawRectangle({ x: 48, y: y - 38, width: W - 96, height: 38, color: CV });
  p.drawText("TOTAL MENSUAL", { x: 64, y: y - 25, size: 13, font: FB, color: CW });
  const tt = fmt(d.total);
  p.drawText(tt, { x: W - 64 - FB.widthOfTextAtSize(tt, 14), y: y - 25, size: 14, font: FB, color: CW });
  p = pdf.addPage([W, H]);
  p.drawRectangle({ x: 0, y: 0, width: W, height: H, color: CI });
  const cc = conW.scale(180 / conW.width);
  p.drawImage(conW, { x: (W - cc.width) / 2, y: H / 2 + 20, width: cc.width, height: cc.height });
  const af = "\xABEl tiempo es lo mas valioso que tenemos, gracias por regalarnos un poco de el.\xBB";
  p.drawText(af, { x: (W - FI.widthOfTextAtSize(af, 12)) / 2, y: H / 2 - 20, size: 12, font: FI, color: rgb(0.85, 0.83, 0.92) });
  const dis = "Recuerda que la disponibilidad cambia dia con dia \xB7 Sujeto a confirmacion";
  p.drawText(dis, { x: (W - F.widthOfTextAtSize(dis, 9)) / 2, y: 60, size: 9, font: F, color: rgb(0.6, 0.55, 0.75) });
  return await pdf.save();
}
async function buildPdf(d) {
  return b64(await buildPdfDoc(d));
}
async function buildFichaPdf(it) {
  const pdf = await PDFDocument.create();
  const F = await pdf.embedFont(StandardFonts.Helvetica), FB = await pdf.embedFont(StandardFonts.HelveticaBold), FI = await pdf.embedFont(StandardFonts.HelveticaOblique);
  const W = 612, H = 792;
  const p = pdf.addPage([W, H]);
  p.drawRectangle({ x: 0, y: 0, width: W, height: H, color: CP });
  p.drawRectangle({ x: 0, y: H - 110, width: W, height: 110, color: CI });
  try {
    const conW = await pdf.embedPng(await grab(BASE + "/assets/connectia-white.png"));
    const s = conW.scale(140 / conW.width);
    p.drawImage(conW, { x: 56, y: H - 74, width: s.width, height: s.height });
  } catch (_e) {
  }
  p.drawText("FICHA T\xC9CNICA", { x: 56, y: H - 150, size: 9, font: FB, color: CH });
  p.drawText((it.n || "").slice(0, 44), { x: 54, y: H - 180, size: 22, font: FB, color: CI });
  if (it.img) {
    try {
      const img = await pdf.embedJpg(await grab(it.img));
      p.drawImage(img, { x: 56, y: H - 400, width: 300, height: 190 });
    } catch (_e) {
    }
  }
  let y = H - 230;
  const tx = 380;
  const rows = [["Clave", it.id || "-"], ["Medidas", it.med || "-"], ["Impactos/mes", impf(it.imp)], ["Tarifa mensual", it.precio || fmt(it.t)]];
  if (it.lat) rows.push(["Coordenadas", it.lat + ", " + it.lng]);
  rows.forEach((r) => {
    p.drawText(r[0], { x: tx, y, size: 10, font: F, color: rgb(0.4, 0.4, 0.45) });
    p.drawText(String(r[1]), { x: tx, y: y - 15, size: 13, font: FB, color: CD });
    y -= 44;
  });
  const dis = "Recuerda que la disponibilidad cambia dia con dia \xB7 Sujeto a confirmacion";
  p.drawText(dis, { x: 56, y: 60, size: 9, font: FI, color: rgb(0.6, 0.55, 0.75) });
  return await pdf.save();
}
function fichaRows(items, label, color) {
  if (!items.length) return "";
  const rows = items.map((x) => {
    const p = POI[x.id] || {};
    return "<tr><td style='padding:10px 0;border-bottom:1px solid #33224f'><div style='color:#fff;font-weight:bold;font-size:14px'>" + x.nombre + "</div><div style='color:#9b8fc0;font-size:11px;margin-top:2px'>" + (p.tipo || "") + " \xB7 " + (p.med || "") + " \xB7 " + impf(p.imp) + " imp/mes \xB7 " + (p.lat || "") + ", " + (p.lng || "") + "</div></td><td align='right' style='border-bottom:1px solid #33224f;color:#FFC220;font-weight:bold;font-size:14px;white-space:nowrap;vertical-align:top;padding-top:10px'>" + fmt(x.tarifa) + "/mes</td></tr>";
  }).join("");
  return "<tr><td colspan='2' style='padding:14px 0 4px;color:" + color + ";font-size:11px;letter-spacing:2px;font-weight:bold'>" + label + "</td></tr>" + rows;
}
function interesCards(pool, correo, nombre) {
  return pool.map((it) => {
    const rv = FN + "?action=reservar&item=" + enc(it.n) + "&id=" + enc(it.id) + "&precio=" + enc(it.precio) + "&correo=" + enc(correo) + "&nombre=" + enc(nombre);
    const dl = FN + "?action=ficha&id=" + enc(it.id);
    return "<table width='100%' cellpadding='0' cellspacing='0' style='margin:10px 0;background:#1b0f38;border-radius:16px;overflow:hidden;border:1px solid #33224f'><tr><td style='padding:0'><img src='" + it.img + "' width='100%' style='display:block;width:100%;max-height:150px;object-fit:cover' alt='" + it.n + "'><div style='padding:14px 16px'><div style='color:#fff;font-weight:bold;font-size:15px'>" + it.n + "</div><div style='color:#9b8fc0;font-size:12px;margin:4px 0 2px'>" + it.med + " \xB7 " + impf(it.imp) + " imp/mes</div><div style='color:#FFC220;font-weight:bold;font-size:14px;margin-bottom:12px'>" + it.precio + (it.t ? " /mes" : "") + "</div><table width='100%' cellpadding='0' cellspacing='0'><tr><td width='50%' style='padding-right:5px'><a href='" + rv + "' style='display:block;text-align:center;background:linear-gradient(135deg,#E01C8A,#FF6A1A);color:#fff;text-decoration:none;padding:12px;border-radius:10px;font-weight:bold;font-size:13px'>Reservar</a></td><td width='50%' style='padding-left:5px'><a href='" + dl + "' style='display:block;text-align:center;background:#2a1a52;border:1px solid #6030A0;color:#cdbff0;text-decoration:none;padding:12px;border-radius:10px;font-weight:bold;font-size:13px'>Descargar sitio</a></td></tr></table></div></td></tr></table>";
  }).join("");
}
function newsletter(d, pool) {
  const nombre = (d.nombre || (d.correo || "").split("@")[0] || "").toString();
  const saludo = nombre ? "Hola " + nombre.charAt(0).toUpperCase() + nombre.slice(1) : "Hola";
  const maps = "https://www.connectia.mx/geonexa";
  const fichas = fichaRows(d.reservados || [], "RESERVADOS", "#7B3FF2") + fichaRows(d.bloqueados || [], "EN PROPUESTA", "#FFC220");
  return "<!DOCTYPE html><html><body style='margin:0;background:#0A0118;font-family:Arial,Helvetica,sans-serif'><table width='100%' cellpadding='0' cellspacing='0'><tr><td align='center' style='padding:28px 12px'><table width='600' cellpadding='0' cellspacing='0' style='max-width:600px'><tr><td style='background:linear-gradient(140deg,#1A0B3D 0%,#5A1B82 38%,#E01C8A 74%,#FF6A1A 100%);border-radius:22px;padding:40px 30px;text-align:center'><img src='" + LOGO + "' height='54' style='display:inline-block;margin-bottom:16px' alt='Connectia'><div style='color:rgba(255,255,255,.85);font-size:11px;letter-spacing:3px'>CONNECTIA \xD7 WALMART \xB7 OUT OF NOISE</div><h1 style='color:#fff;margin:12px 0 6px;font-size:26px'>" + saludo + ", gracias por acompa\xF1arnos</h1><div style='color:rgba(255,255,255,.92);font-size:14px'>Tu propuesta va adjunta en <b>PDF + Excel</b> con la ficha t\xE9cnica de cada sitio.</div></td></tr><tr><td style='padding:14px 6px 0;color:#6B6580;font-size:12px'>Enviado a: <b style='color:#E9E6F0'>" + d.correo + "</b></td></tr><tr><td style='padding:18px 6px 0'><div style='background:#160b31;border-radius:18px;padding:22px'><div style='color:#7B3FF2;font-size:11px;letter-spacing:2px;font-weight:bold'>TU SELECCI\xD3N \xB7 FICHA T\xC9CNICA</div><table width='100%' style='margin-top:6px'>" + fichas + "<tr><td style='padding-top:14px;color:#fff;font-weight:bold'>TOTAL MENSUAL</td><td align='right' style='padding-top:14px;color:#FFC220;font-weight:bold'>" + fmt(d.total) + "</td></tr></table><a href='" + maps + "' style='display:block;margin-top:16px;background:linear-gradient(135deg,#6030A0,#E01C8A);color:#fff;text-decoration:none;text-align:center;padding:16px;border-radius:12px;font-weight:bold;text-transform:uppercase;font-size:14px'>Ver el mapa</a></div></td></tr><tr><td style='padding:14px 6px 0'><div style='background:#2a1030;border:1px dashed #E01C8A;border-radius:12px;padding:14px;color:#ffd9ee;font-size:12px;text-align:center'>\u26A0\uFE0F Recuerda que la disponibilidad cambia d\xEDa con d\xEDa. Todo est\xE1 sujeto a confirmaci\xF3n.</div></td></tr><tr><td style='padding:22px 6px 0'><div style='color:#FFC220;font-size:12px;letter-spacing:2px;font-weight:bold'>TE PUEDE INTERESAR</div><div style='color:#9b8fc0;font-size:11px;margin:3px 0 6px'>Landmarks y muros premium disponibles para Walmart</div>" + interesCards(pool, d.correo, nombre) + "</td></tr><tr><td style='padding:26px 6px;text-align:center'><div style='color:#E9E6F0;font-style:italic;font-size:14px'>\xABEl tiempo es lo m\xE1s valioso que tenemos, gracias por regalarnos un poco de \xE9l.\xBB</div><div style='color:#6B6580;font-size:12px;margin-top:8px'>Atentamente, todo el equipo de Connectia \xB7 hola@connectia.mx</div></td></tr></table></td></tr></table></body></html>";
}
async function sendMail(body) {
  const r = await fetch("https://api.resend.com/emails", { method: "POST", headers: { Authorization: "Bearer " + RESEND_KEY, "Content-Type": "application/json" }, body: JSON.stringify(body) });
  return { ok: r.ok, txt: r.ok ? "" : await r.text() };
}
function page(title, msg) {
  return "<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'></head><body style='margin:0;background:#0A0118;font-family:Arial;display:flex;align-items:center;justify-content:center;min-height:100vh'><div style='max-width:420px;text-align:center;background:linear-gradient(140deg,#1A0B3D,#5A1B82,#E01C8A);padding:40px 28px;border-radius:22px;margin:16px'><img src='" + LOGO + "' height='28' style='margin-bottom:16px'><h1 style='color:#fff;font-size:22px;margin:8px 0'>" + title + "</h1><p style='color:rgba(255,255,255,.9);font-size:14px'>" + msg + "</p></div></body></html>";
}
async function handle(req) {
  if (req.method === "OPTIONS") return new Response(null, { headers: CORS });
  const url = new URL(req.url);
  const action = url.searchParams.get("action");
  if (req.method === "GET" && action === "reservar") {
    const item = url.searchParams.get("item") || "", precio = url.searchParams.get("precio") || "", correo = url.searchParams.get("correo") || "", nombre = url.searchParams.get("nombre") || "";
    await sendMail({ from: FROM, to: [AVISO], reply_to: correo || "hola@connectia.mx", subject: "\u{1F514} Nueva RESERVA \xB7 " + item, html: page("Nueva reserva", "<b>" + item + "</b><br>" + precio + "<br><br>Cliente: " + (nombre || "-") + "<br>" + correo) });
    return new Response(page("\xA1Listo!", "Registramos tu inter\xE9s en <b>" + item + "</b>. Un asesor de Connectia te contactar\xE1 muy pronto."), { headers: { ...CORS, "Content-Type": "text/html; charset=utf-8" } });
  }
  if (req.method === "GET" && action === "ficha") {
    const id = url.searchParams.get("id") || "";
    let it = INTERES.find((x) => x.id === id);
    if (!it && POI[id]) {
      const p = POI[id];
      it = { id, n: p.n, med: p.med, imp: p.imp, precio: fmt(p.t), t: p.t, lat: p.lat, lng: p.lng, img: BASE + "/" + p.wm };
    }
    if (!it) return new Response("no encontrado", { status: 404, headers: CORS });
    const pdf = await buildFichaPdf(it);
    return new Response(pdf, { headers: { ...CORS, "Content-Type": "application/pdf", "Content-Disposition": 'attachment; filename="Ficha-' + id + '.pdf"' } });
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
    const pool = pick3();
    const m = await sendMail({ from: FROM, to: [d.correo], cc: CC, reply_to: "hola@connectia.mx", subject: "Gracias por acompa\xF1arnos \xB7 Connectia \xD7 Walmart", html: newsletter(d, pool), attachments: att });
    return new Response(JSON.stringify({ ok: true, mailed: m.ok, mailErr: m.txt, att: att.length }), { headers: { ...CORS, "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 400, headers: { ...CORS, "Content-Type": "application/json" } });
  }
}
export {
  handle
};
