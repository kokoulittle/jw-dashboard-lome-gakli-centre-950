const APP_STATE = {
  records: [],
  weekMap: new Map(),
};

const DATE_FULL = new Intl.DateTimeFormat('fr-FR', { dateStyle: 'full' });
const DATE_LONG = new Intl.DateTimeFormat('fr-FR', { dateStyle: 'long' });
const DATE_SHORT = new Intl.DateTimeFormat('fr-FR', { dateStyle: 'short' });

function parseDate(yyyyMmDd) {
  const [y, m, d] = yyyyMmDd.split('-').map(Number);
  return new Date(Date.UTC(y, m - 1, d));
}

function getIsoWeekYear(date) {
  const target = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
  const day = target.getUTCDay() || 7;
  target.setUTCDate(target.getUTCDate() + 4 - day);
  const isoYear = target.getUTCFullYear();
  const firstDay = new Date(Date.UTC(isoYear, 0, 1));
  const week = Math.ceil((((target - firstDay) / 86400000) + 1) / 7);
  return { isoYear, isoWeek: week };
}

function weekDateRange(isoYear, isoWeek) {
  const jan4 = new Date(Date.UTC(isoYear, 0, 4));
  const jan4Day = jan4.getUTCDay() || 7;
  const mondayWeek1 = new Date(jan4);
  mondayWeek1.setUTCDate(jan4.getUTCDate() - jan4Day + 1);
  const monday = new Date(mondayWeek1);
  monday.setUTCDate(mondayWeek1.getUTCDate() + (isoWeek - 1) * 7);
  const sunday = new Date(monday);
  sunday.setUTCDate(monday.getUTCDate() + 6);
  return { monday, sunday };
}

function setStatus(message, isError = false) {
  const status = document.getElementById('status');
  status.textContent = message;
  status.classList.toggle('error', isError);
}

function buildWeekOptions() {
  const selector = document.getElementById('week-selector');
  selector.innerHTML = '';

  const keys = [...APP_STATE.weekMap.keys()].sort((a, b) => {
    const [ya, wa] = a.split('-W').map(Number);
    const [yb, wb] = b.split('-W').map(Number);
    if (ya !== yb) return ya - yb;
    return wa - wb;
  });

  for (const key of keys) {
    const [year, week] = key.split('-W').map(Number);
    const { monday, sunday } = weekDateRange(year, week);
    const option = document.createElement('option');
    option.value = key;
    option.textContent = `Semaine ${week} (${DATE_SHORT.format(monday)} – ${DATE_SHORT.format(sunday)})`;
    selector.append(option);
  }

  if (keys.length === 0) {
    throw new Error('Aucune semaine exploitable trouvée dans le fichier CSV.');
  }

  const now = new Date();
  const current = getIsoWeekYear(new Date(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate())));
  const currentValue = `${current.isoYear}-W${current.isoWeek}`;
  selector.value = keys.includes(currentValue) ? currentValue : keys[keys.length - 1];
}

function renderWeek(weekKey) {
  const [year, week] = weekKey.split('-W').map(Number);
  const data = APP_STATE.weekMap.get(weekKey) || [];

  const { monday, sunday } = weekDateRange(year, week);
  document.getElementById('dashboard-title').textContent =
    `Tableau de Bord des Préposés à l’Accueil — Semaine du ${DATE_LONG.format(monday)} au ${DATE_LONG.format(sunday)}`;

  const fig = {
    data: [{
      type: 'table',
      header: {
        values: ['Date', 'Entrée', 'Porte', 'Intérieur', 'Comptage'],
        fill: { color: '#4F6FA0' },
        font: { color: 'white', size: 13 },
        align: 'left',
      },
      cells: {
        values: [
          data.map((r) => DATE_FULL.format(parseDate(r.Date))),
          data.map((r) => r['Entrée']),
          data.map((r) => r.Porte),
          data.map((r) => r['Intérieur']),
          data.map((r) => r.Comptage),
        ],
        fill: { color: '#E9EEF7' },
        align: 'left',
      },
    }],
    layout: { margin: { t: 20, b: 20 } },
  };

  Plotly.react('week-table', fig.data, fig.layout, { responsive: true });
}

function exportWeekPdf(weekKey) {
  const { jsPDF } = window.jspdf;
  const [year, week] = weekKey.split('-W').map(Number);
  const rows = APP_STATE.weekMap.get(weekKey) || [];
  const { monday, sunday } = weekDateRange(year, week);

  const doc = new jsPDF();
  const title = 'Assemblée locale : Lomé Gakli Centre (950)';
  const subtitle = `Préposés à l’accueil pour la semaine du ${DATE_LONG.format(monday)} au ${DATE_LONG.format(sunday)}`;

  doc.setTextColor(79, 111, 160);
  doc.setFontSize(12);
  doc.text(title, 14, 16);
  doc.setFontSize(11);
  doc.text(subtitle, 14, 24);

  doc.autoTable({
    startY: 30,
    head: [['Date', 'Entrée', 'Porte', 'Intérieur', 'Comptage']],
    body: rows.map((r) => [
      DATE_FULL.format(parseDate(r.Date)),
      r['Entrée'],
      r.Porte,
      r['Intérieur'],
      r.Comptage,
    ]),
    headStyles: { fillColor: [79, 111, 160] },
    styles: { fontSize: 9 },
  });

  doc.save(`preposes_accueil_semaine_${year}_W${week}.pdf`);
}

function initEvents() {
  const selector = document.getElementById('week-selector');
  selector.addEventListener('change', () => renderWeek(selector.value));

  document.getElementById('export-pdf').addEventListener('click', () => {
    exportWeekPdf(selector.value);
  });
}

function normalizeCsvRows(rows) {
  return (rows || []).map((rawRow) => {
    const row = rawRow || {};
    const dateValue = row.Date ?? row['\ufeffDate'] ?? row[' date'] ?? row['Date '] ?? '';

    return {
      Date: String(dateValue).trim(),
      'Entrée': row['Entrée'] || '',
      Porte: row.Porte || '',
      'Intérieur': row['Intérieur'] || '',
      Comptage: row.Comptage || '',
    };
  });
}

async function loadCsv() {
  const csvUrl = new URL('data/Random_Attendant_Crew_Schedule_2026.csv', window.location.href);
  const response = await fetch(csvUrl.toString(), { cache: 'no-store' });

  if (!response.ok) {
    throw new Error(`Fichier CSV inaccessible (${response.status}).`);
  }

  const csvText = await response.text();
  if (csvText.trim().startsWith('<!DOCTYPE') || csvText.trim().startsWith('<html')) {
    throw new Error('La réponse reçue n’est pas un CSV valide.');
  }

  const result = Papa.parse(csvText, {
    header: true,
    skipEmptyLines: 'greedy',
  });

  const fatalErrors = (result.errors || []).filter((err) => err?.code !== 'TooFewFields');
  if (fatalErrors.length) {
    throw new Error(`Erreurs CSV détectées (${fatalErrors.length}).`);
  }

  return normalizeCsvRows(result.data).filter((row) => /^\d{4}-\d{2}-\d{2}$/.test(row.Date));
}

async function init() {
  try {
    setStatus('Chargement des données…');
    APP_STATE.records = await loadCsv();

    for (const record of APP_STATE.records) {
      const parsed = parseDate(record.Date);
      if (Number.isNaN(parsed.getTime())) {
        continue;
      }

      const { isoYear, isoWeek } = getIsoWeekYear(parsed);
      const key = `${isoYear}-W${isoWeek}`;
      const bucket = APP_STATE.weekMap.get(key) || [];
      bucket.push(record);
      APP_STATE.weekMap.set(key, bucket.sort((a, b) => a.Date.localeCompare(b.Date)));
    }

    buildWeekOptions();
    initEvents();

    const selector = document.getElementById('week-selector');
    selector.disabled = false;
    document.getElementById('export-pdf').disabled = false;

    renderWeek(selector.value);
    setStatus(`Données chargées : ${APP_STATE.records.length} affectations.`);
  } catch (error) {
    console.error(error);
    setStatus('Impossible de charger le tableau. Vérifiez le fichier CSV et réessayez.', true);
  }
}

window.addEventListener('DOMContentLoaded', init);
