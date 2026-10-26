/*
 * MSN Weather – Lovelace cards (shipped with the msn_weather integration; no build step, no dependencies)
 *   custom:msn-weather-tile-card       – one weather detail tile
 *   custom:msn-weather-details-card    – all weather detail tiles as on msn.com
 *   custom:msn-weather-hourly-card     – day cards and hourly chart with tabs
 *   custom:msn-weather-nowcast-card    – precipitation of the next 2 hours, minute by minute
 *   custom:msn-weather-alerts-card     – weather warnings
 *   custom:msn-weather-life-card       – health and safety / activities
 *   custom:msn-weather-life-tile-card  – one life index as its own tile
 *   custom:msn-weather-monthly-card    – monthly forecast calendar with climate normals
 *   custom:msn-weather-map-card        – weather map with the correct aspect ratio
 *   strategy custom:msn-weather        – a complete weather view / dashboard
 */
const CARD_VERSION = "1.21.1";

/* ----------------------------------------------------------------------- */
/* i18n                                                                     */
/* ----------------------------------------------------------------------- */
const T = {
  de: {
    details: "Wetterdetails", temperature: "Temperatur", feels: "Gefühlt", clouds: "Bewölkt",
    precipitation: "Niederschlag", wind: "Wind", humidity: "Luftfeuchtigkeit", uv: "UV",
    aqi: "AQI", pollen: "Pollen", visibility: "Sichtbarkeit", pressure: "Druck", sun: "Sonne",
    moon: "Mond", moonphase: "Mondphase", dewpoint: "Taupunkt", relhum: "Relative Luftfeuchte",
    windspeed: "Windgeschw.", gusts: "Windböen", from: "Aus", next24: "In den nächsten 24 Std.",
    mainAllergen: "Hauptallergie", sunrise: "Sonnenaufgang", sunset: "Sonnenuntergang",
    moonrise: "Mondaufgang", moonset: "Monduntergang", nextFull: "Nächster Vollmond",
    phase: "Phase des Mondes", now: "Jetzt", hrs: "Std.", min: "Min.", feelsLabel: "Gefühlt",
    tempLabel: "Temperatur", health: "Gesundheit und Sicherheit", activities: "Aktivitäten",
    tomorrow: "Morgen", today: "Heute", hourly: "Stündlich", overview: "Übersicht",
    cloudcover: "Bewölkt", nowcastTile: "Regen in 2 Std.", noData: "Keine Daten", notFound: "Keine MSN-Wetter-Entitäten gefunden für",
  },
  en: {
    details: "Weather details", temperature: "Temperature", feels: "Feels like", clouds: "Cloud cover",
    precipitation: "Precipitation", wind: "Wind", humidity: "Humidity", uv: "UV", aqi: "AQI",
    pollen: "Pollen", visibility: "Visibility", pressure: "Pressure", sun: "Sun", moon: "Moon",
    moonphase: "Moon phase", dewpoint: "Dew point", relhum: "Relative humidity",
    windspeed: "Wind speed", gusts: "Wind gusts", from: "From", next24: "In the next 24 h",
    mainAllergen: "Main allergen", sunrise: "Sunrise", sunset: "Sunset", moonrise: "Moonrise",
    moonset: "Moonset", nextFull: "Next full moon", phase: "Moon phase", now: "Now", hrs: "h",
    min: "min", feelsLabel: "Feels", tempLabel: "Temp", health: "Health and safety",
    activities: "Activities", tomorrow: "Tomorrow", today: "Today", hourly: "Hourly",
    overview: "Overview", cloudcover: "Clouds", nowcastTile: "Rain in 2 h", noData: "No data",
    notFound: "No MSN weather entities found for",
  },
  it: { details: "Dettagli meteo", temperature: "Temperatura", feels: "Percepita", clouds: "Nuvolosità", precipitation: "Precipitazioni", wind: "Vento", humidity: "Umidità", uv: "UV", aqi: "AQI", pollen: "Pollini", visibility: "Visibilità", pressure: "Pressione", sun: "Sole", moon: "Luna", moonphase: "Fase lunare", dewpoint: "Punto di rugiada", relhum: "Umidità relativa", windspeed: "Velocità vento", gusts: "Raffiche", "from": "Da", next24: "Nelle prossime 24 h", mainAllergen: "Allergene principale", sunrise: "Alba", sunset: "Tramonto", moonrise: "Sorgere della luna", moonset: "Tramonto della luna", nextFull: "Prossima luna piena", phase: "Fase lunare", now: "Ora", hrs: "h", min: "min", feelsLabel: "Percepita", tempLabel: "Temp.", health: "Salute e sicurezza", activities: "Attività", tomorrow: "Domani", today: "Oggi", hourly: "Orario", overview: "Panoramica", cloudcover: "Nuvole", nowcastTile: "Pioggia in 2 h", noData: "Nessun dato", notFound: "Nessuna entità MSN Meteo trovata per" },
  fr: { details: "Détails météo", temperature: "Température", feels: "Ressenti", clouds: "Nébulosité", precipitation: "Précipitations", wind: "Vent", humidity: "Humidité", uv: "UV", aqi: "IQA", pollen: "Pollen", visibility: "Visibilité", pressure: "Pression", sun: "Soleil", moon: "Lune", moonphase: "Phase de la lune", dewpoint: "Point de rosée", relhum: "Humidité relative", windspeed: "Vitesse du vent", gusts: "Rafales", "from": "De", next24: "Dans les prochaines 24 h", mainAllergen: "Allergène principal", sunrise: "Lever du soleil", sunset: "Coucher du soleil", moonrise: "Lever de la lune", moonset: "Coucher de la lune", nextFull: "Prochaine pleine lune", phase: "Phase de la lune", now: "Maintenant", hrs: "h", min: "min", feelsLabel: "Ressenti", tempLabel: "Temp.", health: "Santé et sécurité", activities: "Activités", tomorrow: "Demain", today: "Aujourd'hui", hourly: "Heure par heure", overview: "Aperçu", cloudcover: "Nuages", nowcastTile: "Pluie dans 2 h", noData: "Pas de données", notFound: "Aucune entité MSN Météo trouvée pour" },
  es: { details: "Detalles del tiempo", temperature: "Temperatura", feels: "Sensación", clouds: "Nubosidad", precipitation: "Precipitación", wind: "Viento", humidity: "Humedad", uv: "UV", aqi: "ICA", pollen: "Polen", visibility: "Visibilidad", pressure: "Presión", sun: "Sol", moon: "Luna", moonphase: "Fase lunar", dewpoint: "Punto de rocío", relhum: "Humedad relativa", windspeed: "Velocidad del viento", gusts: "Rachas", "from": "Del", next24: "En las próximas 24 h", mainAllergen: "Alérgeno principal", sunrise: "Amanecer", sunset: "Atardecer", moonrise: "Salida de la luna", moonset: "Puesta de la luna", nextFull: "Próxima luna llena", phase: "Fase lunar", now: "Ahora", hrs: "h", min: "min", feelsLabel: "Sensación", tempLabel: "Temp.", health: "Salud y seguridad", activities: "Actividades", tomorrow: "Mañana", today: "Hoy", hourly: "Por horas", overview: "Resumen", cloudcover: "Nubes", nowcastTile: "Lluvia en 2 h", noData: "Sin datos", notFound: "No se encontraron entidades de MSN El Tiempo para" },
  nl: { details: "Weerdetails", temperature: "Temperatuur", feels: "Gevoelstemperatuur", clouds: "Bewolking", precipitation: "Neerslag", wind: "Wind", humidity: "Luchtvochtigheid", uv: "UV", aqi: "LKI", pollen: "Pollen", visibility: "Zicht", pressure: "Luchtdruk", sun: "Zon", moon: "Maan", moonphase: "Maanfase", dewpoint: "Dauwpunt", relhum: "Relatieve vochtigheid", windspeed: "Windsnelheid", gusts: "Windstoten", "from": "Uit", next24: "In de komende 24 uur", mainAllergen: "Belangrijkste allergeen", sunrise: "Zonsopkomst", sunset: "Zonsondergang", moonrise: "Maanopkomst", moonset: "Maanondergang", nextFull: "Volgende volle maan", phase: "Maanfase", now: "Nu", hrs: "u", min: "min", feelsLabel: "Gevoel", tempLabel: "Temp.", health: "Gezondheid en veiligheid", activities: "Activiteiten", tomorrow: "Morgen", today: "Vandaag", hourly: "Per uur", overview: "Overzicht", cloudcover: "Wolken", nowcastTile: "Regen in 2 uur", noData: "Geen gegevens", notFound: "Geen MSN Weer-entiteiten gevonden voor" },
};
const ALLERGEN = {
  de: { alder: "Erle", birch: "Birke", grass: "Gräser", ragweed: "Ambrosia", mugwort: "Beifuß", olive: "Olive" },
  en: { alder: "Alder", birch: "Birch", grass: "Grass", ragweed: "Ragweed", mugwort: "Mugwort", olive: "Olive" },
  it: { alder: "Ontano", birch: "Betulla", grass: "Graminacee", ragweed: "Ambrosia", mugwort: "Artemisia", olive: "Olivo" },
  fr: { alder: "Aulne", birch: "Bouleau", grass: "Graminées", ragweed: "Ambroisie", mugwort: "Armoise", olive: "Olivier" },
  es: { alder: "Aliso", birch: "Abedul", grass: "Gramíneas", ragweed: "Ambrosía", mugwort: "Artemisa", olive: "Olivo" },
  nl: { alder: "Els", birch: "Berk", grass: "Grassen", ragweed: "Ambrosia", mugwort: "Bijvoet", olive: "Olijf" },
};
const LIFE_LEVELS = {
  de: {
    dressing: ["Kurze Hosen", "Atmungsaktive Kleidung", "Lange Ärmel", "Leichte Jacke", "Dicke Jacke"],
    umbrella: ["Keine Notwendigkeit", "Wahrscheinlich nicht notwendig", "Wahrscheinlich erforderlich", "Notwendig", "Muss"],
    uv: ["Niedrig", "Mäßig", "Hoch", "Sehr hoch", "Extrem"],
    risk: ["Sicher", "Gering", "Mäßig", "Hoch", "Extrem"],
    activity: ["Großartig", "Gut", "Mäßig", "Schlecht", "Sehr schlecht"],
  },
  en: {
    dressing: ["Shorts", "Breathable", "Long sleeves", "Light jacket", "Heavy jacket"],
    umbrella: ["No need", "Probably not needed", "Probably needed", "Needed", "Must"],
    uv: ["Low", "Moderate", "High", "Very high", "Extreme"],
    risk: ["Safe", "Low", "Moderate", "High", "Extreme"],
    activity: ["Great", "Good", "Fair", "Poor", "Very poor"],
  },
  it: { dressing: ["Pantaloncini", "Traspirante", "Maniche lunghe", "Giacca leggera", "Giacca pesante"], umbrella: ["Non serve", "Probabilmente non serve", "Probabilmente serve", "Serve", "Indispensabile"], uv: ["Basso", "Moderato", "Alto", "Molto alto", "Estremo"], risk: ["Sicuro", "Basso", "Moderato", "Alto", "Estremo"], activity: ["Ottimo", "Buono", "Discreto", "Scarso", "Pessimo"] },
  fr: { dressing: ["Short", "Respirant", "Manches longues", "Veste légère", "Veste chaude"], umbrella: ["Pas nécessaire", "Probablement pas nécessaire", "Probablement nécessaire", "Nécessaire", "Indispensable"], uv: ["Faible", "Modéré", "Élevé", "Très élevé", "Extrême"], risk: ["Sûr", "Faible", "Modéré", "Élevé", "Extrême"], activity: ["Excellent", "Bon", "Moyen", "Mauvais", "Très mauvais"] },
  es: { dressing: ["Pantalón corto", "Transpirable", "Manga larga", "Chaqueta ligera", "Chaqueta gruesa"], umbrella: ["No hace falta", "Probablemente no hace falta", "Probablemente hace falta", "Hace falta", "Imprescindible"], uv: ["Bajo", "Moderado", "Alto", "Muy alto", "Extremo"], risk: ["Seguro", "Bajo", "Moderado", "Alto", "Extremo"], activity: ["Excelente", "Bueno", "Regular", "Malo", "Muy malo"] },
  nl: { dressing: ["Korte broek", "Ademend", "Lange mouwen", "Lichte jas", "Dikke jas"], umbrella: ["Niet nodig", "Waarschijnlijk niet nodig", "Waarschijnlijk nodig", "Nodig", "Absoluut nodig"], uv: ["Laag", "Matig", "Hoog", "Zeer hoog", "Extreem"], risk: ["Veilig", "Laag", "Matig", "Hoog", "Extreem"], activity: ["Uitstekend", "Goed", "Matig", "Slecht", "Zeer slecht"] },
};
const LIFE_NAMES = {
  de: { life_umbrella: "Regenschirm", life_walking: "Draußen / Spazierengehen", life_uv: "UV-Belastung", life_driving: "Fahrsicherheit",
        life_dressing: "Kleidung", life_heat_stroke: "Hitzschlag", life_wind_chill: "Windchill", life_running: "Laufen", life_cycling: "Radfahren",
        life_hiking: "Wandern", life_gardening: "Gartenarbeit", life_picnic: "Picknick", life_stargazing: "Sternbeobachtung" },
  en: { life_umbrella: "Umbrella", life_walking: "Outdoors / walking", life_uv: "UV exposure", life_driving: "Driving",
        life_dressing: "Clothing", life_heat_stroke: "Heat stroke", life_wind_chill: "Wind chill", life_running: "Running", life_cycling: "Cycling",
        life_hiking: "Hiking", life_gardening: "Gardening", life_picnic: "Picnic", life_stargazing: "Stargazing" },
  it: { life_umbrella: "Ombrello", life_walking: "All'aperto / passeggiata", life_uv: "Esposizione UV", life_driving: "Guida", life_dressing: "Abbigliamento", life_heat_stroke: "Colpo di calore", life_wind_chill: "Raffreddamento da vento", life_running: "Corsa", life_cycling: "Ciclismo", life_hiking: "Escursionismo", life_gardening: "Giardinaggio", life_picnic: "Picnic", life_stargazing: "Osservazione delle stelle" },
  fr: { life_umbrella: "Parapluie", life_walking: "En extérieur / marche", life_uv: "Exposition aux UV", life_driving: "Conduite", life_dressing: "Habillement", life_heat_stroke: "Coup de chaleur", life_wind_chill: "Refroidissement éolien", life_running: "Course à pied", life_cycling: "Vélo", life_hiking: "Randonnée", life_gardening: "Jardinage", life_picnic: "Pique-nique", life_stargazing: "Observation des étoiles" },
  es: { life_umbrella: "Paraguas", life_walking: "Al aire libre / caminar", life_uv: "Exposición UV", life_driving: "Conducción", life_dressing: "Ropa", life_heat_stroke: "Golpe de calor", life_wind_chill: "Sensación de frío por viento", life_running: "Correr", life_cycling: "Ciclismo", life_hiking: "Senderismo", life_gardening: "Jardinería", life_picnic: "Pícnic", life_stargazing: "Observación de estrellas" },
  nl: { life_umbrella: "Paraplu", life_walking: "Buiten / wandelen", life_uv: "UV-blootstelling", life_driving: "Autorijden", life_dressing: "Kleding", life_heat_stroke: "Hitteberoerte", life_wind_chill: "Gevoelskou", life_running: "Hardlopen", life_cycling: "Fietsen", life_hiking: "Wandelen in de natuur", life_gardening: "Tuinieren", life_picnic: "Picknick", life_stargazing: "Sterrenkijken" },
};
const LIFE_ITEMS = {
  health: [
    ["life_umbrella", "umbrella", "mdi:umbrella-outline"],
    ["life_walking", "activity", "mdi:walk"],
    ["life_uv", "uv", "mdi:white-balance-sunny"],
    ["life_driving", "activity", "mdi:car-outline"],
    ["life_dressing", "dressing", "mdi:tshirt-crew-outline"],
    ["life_heat_stroke", "risk", "mdi:thermometer-high"],
    ["life_wind_chill", "risk", "mdi:thermometer-low"],
  ],
  activities: [
    ["life_running", "activity", "mdi:run"],
    ["life_cycling", "activity", "mdi:bike"],
    ["life_hiking", "activity", "mdi:hiking"],
    ["life_walking", "activity", "mdi:walk"],
    ["life_gardening", "activity", "mdi:flower-outline"],
    ["life_picnic", "activity", "mdi:basket-outline"],
    ["life_stargazing", "activity", "mdi:star-shooting-outline"],
  ],
};
const COND_ICON = {
  "clear-night": "mdi:weather-night", cloudy: "mdi:weather-cloudy", fog: "mdi:weather-fog",
  hail: "mdi:weather-hail", lightning: "mdi:weather-lightning", "lightning-rainy": "mdi:weather-lightning-rainy",
  partlycloudy: "mdi:weather-partly-cloudy", pouring: "mdi:weather-pouring", rainy: "mdi:weather-rainy",
  snowy: "mdi:weather-snowy", "snowy-rainy": "mdi:weather-snowy-rainy", sunny: "mdi:weather-sunny",
  windy: "mdi:weather-windy", exceptional: "mdi:alert-circle-outline",
};
const COND_COLOR = {
  sunny: "#f59e0b", "clear-night": "#94a3b8", partlycloudy: "#f8b84e", cloudy: "#9ca3af",
  rainy: "#60a5fa", pouring: "#3b82f6", lightning: "#facc15", "lightning-rainy": "#facc15",
  snowy: "#7dd3fc", "snowy-rainy": "#60a5fa", fog: "#cbd5e1", hail: "#a5b4fc",
};

/* ----------------------------------------------------------------------- */
/* helpers                                                                  */
/* ----------------------------------------------------------------------- */
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const num = (v) => (v === undefined || v === null || v === "" || isNaN(Number(v)) ? null : Number(v));
const fmt = (v, d = 0) => (num(v) === null ? "–" : Number(v).toLocaleString(undefined, { maximumFractionDigits: d, minimumFractionDigits: 0, useGrouping: false }));
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const LANG_CODES = ["de", "en", "it", "fr", "es", "nl"];
/** Card language: the user's (or the card's `language`) if supported, otherwise English. */
const lang = (hass) => {
  const code = ((hass && hass.language) || "en").slice(0, 2).toLowerCase();
  return LANG_CODES.includes(code) ? code : "en";
};
/** Text in the given language, English as fallback. */
const pick = (lc, texts) => (texts[lc] !== undefined ? texts[lc] : texts.en);
const timeStr = (iso, hass, tz) => {
  if (!iso) return "–";
  const d = new Date(iso);
  if (isNaN(d)) return "–";
  try { return d.toLocaleTimeString(hass?.language || "de", { hour: "2-digit", minute: "2-digit", timeZone: tz || undefined }); }
  catch (e) { return d.toLocaleTimeString(hass?.language || "de", { hour: "2-digit", minute: "2-digit" }); }
};

/** Find the msn_weather entities belonging to the device of the given weather entity. */
function resolveEntities(hass, weatherEntity) {
  const out = {};
  if (!hass || !hass.entities) return out;
  const reg = hass.entities[weatherEntity];
  let device = reg && reg.device_id;
  if (!device) {
    // fall back to the first msn_weather weather entity
    const first = Object.values(hass.entities).find((e) => e.platform === "msn_weather" && e.entity_id.startsWith("weather."));
    device = first && first.device_id;
  }
  for (const e of Object.values(hass.entities)) {
    if (e.platform !== "msn_weather" || (device && e.device_id !== device)) continue;
    if (e.translation_key) out[e.translation_key] = e.entity_id;
    if (e.entity_id.startsWith("weather.")) out.weather = e.entity_id;
  }
  return out;
}

function aqiColor(v) {
  return v === null || v === undefined ? "#999" : v <= 50 ? "#00ae56" : v <= 100 ? "#d4a017" : v <= 150 ? "#f2610c" : v <= 200 ? "#d13438" : v <= 300 ? "#88179a" : "#6e220f";
}

function trendIcon(trend) {
  const t = (trend || "").toLowerCase();
  if (t.startsWith("incr")) return `<span class="trend up" title="${esc(trend)}">↗</span>`;
  if (t.startsWith("decr")) return `<span class="trend down" title="${esc(trend)}">↘</span>`;
  return `<span class="trend steady" title="${esc(trend || "Steady")}">→</span>`;
}

/** "Rain in 15 min" / "Rain stops in 20 min" from the 4 minute nowcast values. */
function nowcastInfo(st, hass) {
  const de = lang(hass) === "de";
  const lc = lang(hass);
  const a = (st && st.attributes) || {};
  const step = num(a.minutes_between_values) || 4;
  const rates = (a.precipitation_rate || a.precipitation || []).slice(0, Math.floor(120 / step) + 1).map((v) => Math.max(0, num(v) || 0));
  const imperial = (hass.states && Object.values(hass.states).find((x) => x.entity_id.startsWith("weather.") && x.attributes.precipitation_unit)?.attributes.precipitation_unit) === "in";
  const wet = rates.map((v) => (imperial ? v * 25.4 : v) > 0.05);
  const age = a.timestamp ? Math.max(0, (Date.now() - new Date(a.timestamp).getTime()) / 60000) : 0;
  const minutes = (i) => Math.max(1, Math.round(i * step - age));
  const snow = a.precipitation_type === "sn" || a.precipitation_type === "s";
  const what = snow ? (pick(lc, { de: "Schnee", en: "Snow", it: "Neve", fr: "Neige", es: "Nieve", nl: "Sneeuw" })) : (pick(lc, { de: "Regen", en: "Rain", it: "Pioggia", fr: "Pluie", es: "Lluvia", nl: "Regen" }));
  let text, kind;
  if (!wet.length || !wet.some(Boolean)) {
    kind = "dry"; text = pick(lc, { de: "Kein Niederschlag in 2 Std.", en: "No precipitation for 2 h", it: "Nessuna precipitazione per 2 h", fr: "Pas de précipitations pendant 2 h", es: "Sin precipitación en 2 h", nl: "Geen neerslag in 2 uur" });
  } else if (!wet[0]) {
    const i = wet.indexOf(true); kind = "start";
    text = pick(lc, { de: `${what} in ${minutes(i)} Min.`, en: `${what} in ${minutes(i)} min`, it: `${what} tra ${minutes(i)} min`, fr: `${what} dans ${minutes(i)} min`, es: `${what} en ${minutes(i)} min`, nl: `${what} over ${minutes(i)} min` });
  } else if (wet.every(Boolean)) {
    kind = "steady"; text = pick(lc, { de: `${what} hält 2 Std. an`, en: `${what} for 2 h or more`, it: `${what} per 2 h o più`, fr: `${what} pendant 2 h ou plus`, es: `${what} durante 2 h o más`, nl: `${what} 2 uur of langer` });
  } else {
    const i = wet.indexOf(false); kind = "stop";
    text = pick(lc, { de: `${what} hört in ${minutes(i)} Min. auf`, en: `${what} stops in ${minutes(i)} min`, it: `${what}: fine tra ${minutes(i)} min`, fr: `${what} : fin dans ${minutes(i)} min`, es: `${what}: termina en ${minutes(i)} min`, nl: `${what} stopt over ${minutes(i)} min` });
  }
  const icon = kind === "dry" ? "mdi:weather-partly-cloudy" : snow ? "mdi:weather-snowy" : kind === "stop" ? "mdi:weather-partly-rainy" : "mdi:weather-rainy";
  // mini histogram for tiles (0..100 x 0..40)
  const n = Math.max(rates.length, 1), mx = Math.max(imperial ? 0.1 : 2.5, ...rates);
  const bars = rates.map((v, i) => {
    const h = v > 0 ? Math.max(2, (Math.sqrt(v / mx)) * 38) : 1;
    return `<rect x="${(i * 100) / n + 0.3}" y="${40 - h}" width="${100 / n - 0.6}" height="${h}" rx="0.6" fill="${v > 0 ? "#2563eb" : "currentColor"}" opacity="${v > 0 ? 1 : 0.18}"/>`;
  }).join("");
  return { text, kind, icon, summary: st ? st.state : "", spark: `<svg class="fill" viewBox="0 0 100 40" preserveAspectRatio="none">${bars}</svg>` };
}

/** Smooth SVG path through points (Catmull-Rom → Bezier). */
function smoothPath(pts) {
  if (pts.length < 2) return "";
  let d = `M${pts[0][0].toFixed(1)},${pts[0][1].toFixed(1)}`;
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[i - 1] || pts[i], p1 = pts[i], p2 = pts[i + 1], p3 = pts[i + 2] || p2;
    const c1x = p1[0] + (p2[0] - p0[0]) / 6, c1y = p1[1] + (p2[1] - p0[1]) / 6;
    const c2x = p2[0] - (p3[0] - p1[0]) / 6, c2y = p2[1] - (p3[1] - p1[1]) / 6;
    d += ` C${c1x.toFixed(1)},${c1y.toFixed(1)} ${c2x.toFixed(1)},${c2y.toFixed(1)} ${p2[0].toFixed(1)},${p2[1].toFixed(1)}`;
  }
  return d;
}

function sparkline(values, { w = 240, h = 90, color = "#22c1c3", fill = true, dotIndex = 0, pad = 10 } = {}) {
  const vals = values.filter((v) => num(v) !== null);
  if (vals.length < 2) return `<svg viewBox="0 0 ${w} ${h}"></svg>`;
  const mn = Math.min(...vals), mx = Math.max(...vals), rng = mx - mn || 1;
  const pts = values.map((v, i) => [pad + (i * (w - 2 * pad)) / (values.length - 1), pad + (h - 2 * pad) * (1 - (Number(v) - mn) / rng)]);
  const path = smoothPath(pts);
  const di = clamp(dotIndex, 0, pts.length - 1);
  const area = fill ? `<path d="${path} L${pts[pts.length - 1][0]},${h} L${pts[0][0]},${h} Z" fill="${color}" opacity="0.12"/>` : "";
  return `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none">
    ${area}
    ${di > 0 ? `<path d="${smoothPath(pts.slice(0, di + 1))}" stroke="${color}" stroke-width="6" fill="none" stroke-linecap="round"/>` : ""}
    <path d="${smoothPath(pts.slice(di))}" stroke="${di > 0 ? "var(--msn-muted-line)" : color}" stroke-width="6" fill="none" stroke-linecap="round"/>
    <circle cx="${pts[di][0]}" cy="${pts[di][1]}" r="9" fill="${color}" stroke="#fff" stroke-width="3"/>
  </svg>`;
}

/** Gauge arc (start/end angles in degrees, 0 = top, clockwise). */
function arcPath(cx, cy, r, a0, a1) {
  const p = (a) => [cx + r * Math.sin((a * Math.PI) / 180), cy - r * Math.cos((a * Math.PI) / 180)];
  const [x0, y0] = p(a0), [x1, y1] = p(a1);
  const large = Math.abs(a1 - a0) > 180 ? 1 : 0;
  return `M${x0.toFixed(1)},${y0.toFixed(1)} A${r},${r} 0 ${large} 1 ${x1.toFixed(1)},${y1.toFixed(1)}`;
}
function arcPoint(cx, cy, r, a) {
  return [cx + r * Math.sin((a * Math.PI) / 180), cy - r * Math.cos((a * Math.PI) / 180)];
}

const STYLE = `
  :host { display:block; --msn-tile-bg: color-mix(in srgb, var(--primary-text-color) 5%, var(--ha-card-background, var(--card-background-color, #fff)));
          --msn-muted-line: color-mix(in srgb, var(--primary-text-color) 18%, transparent);
          --msn-muted: var(--secondary-text-color); }
  ha-card { padding: 16px; }
  .head { display:flex; align-items:baseline; gap:10px; font-size:17px; font-weight:600; margin: 2px 2px 14px; }
  .head small { font-weight:500; color: var(--msn-muted); }
  .grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(var(--msn-tile-min, 230px), 1fr)); gap: 14px; }
  .tile { background: var(--msn-tile-bg); border-radius: 16px; padding: 12px 14px; height: 210px; display:flex; flex-direction:column; box-sizing:border-box; overflow:hidden; }
  .tile .t { font-size: 14px; margin-bottom: 4px; flex: none; }
  .tile .viz { flex: 1 1 0; min-height: 64px; position: relative; }
  /* absolutely positioned: the graphic only takes the space left over and never grows the tile */
  .tile .vz { position: absolute; inset: 0; width: 100%; height: 100%; display:block; overflow: visible; }
  .tile .hl { flex: none; font-weight: 700; font-size: 14px; margin-top: 6px; display:flex; align-items:center; gap:6px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .tile .sm { flex: none; font-size: 12px; color: var(--msn-muted); line-height: 1.3; margin-top: 2px;
              display:-webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow:hidden; }
  .trend { display:inline-flex; width:17px; height:17px; border-radius:50%; align-items:center; justify-content:center; font-size:11px; color:#fff; font-weight:700; }
  .trend.up { background:#f97316; } .trend.down { background:#3b82f6; } .trend.steady { background:#eab308; }
  .big { font-size: 40px; font-weight: 700; line-height: 1; }
  .unit { font-size: 15px; font-weight:500; margin-left: 2px; }
  .lbl { font-size: 13px; color: var(--msn-muted); }
  svg { width: 100%; height: 100%; overflow: visible; }
  .row { display:flex; align-items:flex-end; gap: 10px; flex-wrap: wrap; }
  .center-txt { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; pointer-events:none; }
  .disc { width: 120px; height: 120px; border-radius: 50%; background: color-mix(in srgb, var(--primary-text-color) 8%, transparent);
          display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; font-weight:700; }
  .err { color: var(--error-color); padding: 8px; }
`;

/* "Home Assistant" appearance: same content, classic HA look */
const HA_STYLE = `
  :host { --msn-tile-bg: transparent; --msn-muted-line: var(--divider-color, rgba(127,127,127,.25)); }
  .head { font-size: 18px; font-weight: 500; }
  .tile, .day, .c, .li, .detail, .clim div { background: none !important; border: 1px solid var(--divider-color, rgba(127,127,127,.25)) !important; border-radius: var(--ha-card-border-radius, 12px) !important; }
  .c.empty { border: none !important; }
  .tab { background: none !important; border: 1px solid var(--divider-color, rgba(127,127,127,.3)) !important; border-radius: 8px !important; }
  .tab.on { background: rgba(var(--rgb-primary-color, 3, 169, 244), .15) !important; color: var(--primary-color) !important; border-color: transparent !important; font-weight: 500 !important; }
  .day.on, .li.on { border-color: var(--primary-color) !important; box-shadow: none !important; background: rgba(var(--rgb-primary-color, 3, 169, 244), .06) !important; }
  .c.today { outline: none; border-color: var(--primary-color) !important; }
  .big { font-weight: 500; }
  /* HA tile */
  .hat { height: 100%; box-sizing: border-box; padding: 12px; display: flex; flex-direction: column; gap: 8px; overflow: hidden; cursor: pointer; }
  .hat .top { display: flex; align-items: center; gap: 10px; flex: none; }
  .hat .ic { width: 36px; height: 36px; border-radius: 50%; flex: none; display: flex; align-items: center; justify-content: center;
             background: color-mix(in srgb, var(--c) 20%, transparent); color: var(--c); }
  .hat .ic ha-icon { --mdc-icon-size: 20px; }
  .hat .nm { min-width: 0; flex: 1; display: flex; flex-direction: column; }
  .hat .name { font-size: 13px; color: var(--secondary-text-color); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .hat .val { font-size: 18px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: flex; align-items: center; gap: 4px; }
  .hat .val small { font-size: 13px; color: var(--secondary-text-color); font-weight: 400; margin-left: 2px; overflow: hidden; text-overflow: ellipsis; }
  .hat .val ha-icon { --mdc-icon-size: 16px; color: var(--secondary-text-color); flex: none; }
  .hat .feat { flex: 1 1 0; min-height: 26px; position: relative; display: flex; align-items: center; gap: 10px; font-size: 12px; color: var(--secondary-text-color); }
  .hat .feat { overflow: hidden; }
  .hat .feat > span { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0; }
  .hat .feat > svg.fill { position: absolute; inset: 0; width: 100%; height: 100%; overflow: visible; }
  .hat .feat .dot { position: absolute; width: 9px; height: 9px; border-radius: 50%; transform: translate(-50%, -50%); background: var(--c); box-shadow: 0 0 0 2px var(--card-background-color, #fff); }
  .hat .bar { position: relative; flex: 1; height: 8px; border-radius: 4px; background: var(--divider-color, rgba(127,127,127,.25)); }
  .hat .bar i { position: absolute; left: 0; top: 0; bottom: 0; border-radius: 4px; background: var(--c); }
  .hat .bar b { position: absolute; top: 50%; width: 12px; height: 12px; border-radius: 50%; transform: translate(-50%, -50%); background: var(--card-background-color, #fff); border: 3px solid var(--c); box-sizing: border-box; }
  .hat .txt { flex: none; font-size: 12px; color: var(--secondary-text-color); line-height: 1.35; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
  .hat .txt b { color: var(--primary-text-color); font-weight: 500; }
  .grid .hat { border: 1px solid var(--divider-color, rgba(127,127,127,.25)); border-radius: var(--ha-card-border-radius, 12px); height: 160px; }
`;

/* ----------------------------------------------------------------------- */
/* base class                                                               */
/* ----------------------------------------------------------------------- */
class MsnBase extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._forecast = null;
    this._unsub = null;
    this._sig = "";
  }
  setConfig(config) {
    this._config = { ...config };
    this._sig = "";
  }
  set hass(hass) {
    const first = !this._hass;
    // optional per-card language override (language: en | de)
    this._hass = this._config && this._config.language
      ? Object.assign(Object.create(hass), { language: this._config.language })
      : hass;
    this._ents = resolveEntities(hass, this._config.entity);
    if (first || !this._unsub) this._subscribe();
    const sig = this._signature();
    if (sig !== this._sig) {
      this._sig = sig;
      this._render();
    }
  }
  get hass() { return this._hass; }
  /** classic Home Assistant look instead of the MSN look */
  get _ha() { return (this._config && this._config.appearance) === "ha"; }
  _css() { return STYLE + (this._ha ? HA_STYLE : ""); }
  disconnectedCallback() {
    if (this._unsub) { this._unsub.then((u) => u && u()).catch(() => {}); this._unsub = null; }
  }
  connectedCallback() {
    if (this._hass && !this._unsub) this._subscribe();
    if (this._responsive && !this._ro && window.ResizeObserver) {
      this._ro = new ResizeObserver((entries) => {
        const r = entries[0].contentRect;
        const w = Math.round(r.width), h = Math.round(r.height);
        if (Math.abs(w - (this._w || 0)) > 24 || Math.abs(h - (this._h || 0)) > 24) {
          this._w = w; this._h = h; this._sig = "";
          if (this._hass) this._render();
        }
      });
      this._ro.observe(this);
    }
  }
  get _width() { return this._w || this.getBoundingClientRect().width || 900; }
  _needsForecast() { return true; }
  _subscribe() {
    const w = this._ents.weather;
    if (!this._needsForecast() || !w || !this._hass?.connection) return;
    this._unsub = this._hass.connection
      .subscribeMessage((msg) => {
        if (msg.forecast && msg.forecast.length) { this._forecast = msg.forecast; this._sig = ""; this._render(); }
      }, { type: "weather/subscribe_forecast", forecast_type: "hourly", entity_id: w })
      .catch(() => null);
    // fallback: an empty first push would otherwise only be refreshed with the next update
    setTimeout(() => this._fetchForecast(w), 2500);
  }
  async _fetchForecast(w) {
    if (this._forecast && this._forecast.length) return;
    try {
      const res = await this._hass.callWS({
        type: "call_service", domain: "weather", service: "get_forecasts",
        service_data: { type: "hourly" }, target: { entity_id: w }, return_response: true,
      });
      const fc = res?.response?.[w]?.forecast;
      if (fc && fc.length && !(this._forecast && this._forecast.length)) { this._forecast = fc; this._sig = ""; this._render(); }
    } catch (e) { /* ignore */ }
  }
  _signature() {
    return Object.values(this._ents).map((id) => {
      const s = this._hass.states[id];
      return s ? s.last_updated : "";
    }).join("|") + (this._forecast ? this._forecast.length : 0);
  }
  /** Offset (minutes) of the weather location, taken from the forecast timestamps; null = browser time. */
  _locOffset() {
    const dt = this._forecast && this._forecast[0] && this._forecast[0].datetime;
    const m = dt && /([+-])(\d{2}):(\d{2})$/.exec(dt);
    return m ? (m[1] === "-" ? -1 : 1) * (Number(m[2]) * 60 + Number(m[3])) : null;
  }
  /** IANA time zone of the weather location (from MSN), undefined = browser zone. */
  _tz() {
    const loc = this.attr("last_update", "location");
    return (loc && loc.timezone) || undefined;
  }
  /** Wall-clock parts at the weather location. */
  _locNow() {
    const tz = this._tz();
    if (tz) {
      try {
        const p = Object.fromEntries(new Intl.DateTimeFormat("en-CA", { timeZone: tz, year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", hourCycle: "h23" })
          .formatToParts(new Date()).map((x) => [x.type, x.value]));
        return { y: Number(p.year), mo: Number(p.month), d: Number(p.day), h: Number(p.hour) };
      } catch (e) { /* fall through */ }
    }
    const off = this._locOffset();
    if (off === null) { const d = new Date(); return { y: d.getFullYear(), mo: d.getMonth() + 1, d: d.getDate(), h: d.getHours() }; }
    const d = new Date(Date.now() + off * 60000);
    return { y: d.getUTCFullYear(), mo: d.getUTCMonth() + 1, d: d.getUTCDate(), h: d.getUTCHours() };
  }
  _locDayKey(deltaDays = 0) {
    const n = this._locNow();
    const d = new Date(Date.UTC(n.y, n.mo - 1, n.d + deltaDays));
    return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, "0")}-${String(d.getUTCDate()).padStart(2, "0")}`;
  }
  st(key) { const id = this._ents[key]; return id ? this._hass.states[id] : undefined; }
  val(key) { const s = this.st(key); return s ? s.state : undefined; }
  attr(key, a) { const s = this.st(key); return s ? s.attributes[a] : undefined; }
  t(k) { return (T[lang(this._hass)] || T.en)[k] || k; }
  /** Display unit of the weather entity (follows the Home Assistant unit system). */
  _unit(kind) {
    const w = this._ents && this._ents.weather ? this._hass.states[this._ents.weather] : null;
    const a = (w && w.attributes) || {};
    return { temp: a.temperature_unit || "°C", wind: a.wind_speed_unit || "km/h", pressure: a.pressure_unit || "hPa",
             vis: a.visibility_unit || "km", precip: a.precipitation_unit || "mm" }[kind] || "";
  }
  /** Sensible decimals per unit (inHg / in need two). */
  _dec(kind) {
    const u = this._unit(kind);
    return { inHg: 2, in: 2, mm: 1, km: 1, mi: 1 }[u] ?? 0;
  }
  /** Life index name: Home Assistant's (translated) entity name, or the card language's when `language` is set. */
  _lifeName(key, st) {
    if (this._config.language) return (LIFE_NAMES[lang(this._hass)] || LIFE_NAMES.en)[key] || this._name(st);
    return this._name(st);
  }
  _name(st) {
    const reg = this._hass.entities[st.entity_id];
    const dev = reg && reg.device_id && this._hass.devices?.[reg.device_id];
    let n = st.attributes.friendly_name || st.entity_id;
    if (dev && dev.name && n.startsWith(dev.name + " ")) n = n.slice(dev.name.length + 1);
    return n;
  }
  more(key) {
    const id = this._ents[key];
    if (!id) return;
    const ev = new Event("hass-more-info", { bubbles: true, composed: true });
    ev.detail = { entityId: id };
    this.dispatchEvent(ev);
  }
}

/* ----------------------------------------------------------------------- */
/* Details card                                                             */
/* ----------------------------------------------------------------------- */
const ALL_TILES = ["temperature", "feels", "clouds", "precipitation", "nowcast", "wind", "humidity", "uv", "aqi",
  "pollen", "visibility", "pressure", "sun", "moon", "moonphase"];
const TILE_ENTITY = {
  temperature: "temperature", feels: "apparent_temperature", clouds: "cloud_cover", precipitation: "precipitation_today",
  nowcast: "nowcast", wind: "wind_speed", humidity: "humidity", uv: "uv_index", aqi: "aqi", pollen: "pollen", visibility: "visibility",
  pressure: "pressure", sun: "sunrise", moon: "moonrise", moonphase: "moon_phase",
};

class MsnTiles extends MsnBase {
  static getStubConfig(hass) {
    const w = Object.values(hass.entities || {}).find((e) => e.platform === "msn_weather" && e.entity_id.startsWith("weather."));
    return { entity: w ? w.entity_id : "" };
  }
  getCardSize() { return 8; }
  getGridOptions() { return { columns: "full", min_columns: 6 }; }

  _render() {
    if (!this._hass) return;
    if (!this._ents.temperature) {
      this.shadowRoot.innerHTML = `<ha-card><div class="err">${this.t("notFound")} ${esc(this._config.entity)}</div></ha-card>`;
      return;
    }
    const tiles = this._config.tiles || ALL_TILES;
    const showTitle = this._config.show_title !== false;
    const now = new Date();
    const head = showTitle
      ? `<div class="head">${esc(this._config.title || this.t("details"))} <small>${timeStr(now.toISOString(), this._hass, this._tz())}</small></div>`
      : "";
    const body = tiles.map((k) => (this["tile_" + k] ? this._tile(k, this["tile_" + k]()) : "")).join("");
    this.shadowRoot.innerHTML = `<style>${this._css()}</style><ha-card>${head}<div class="grid" style="${this._config.tile_min_width ? `--msn-tile-min:${this._config.tile_min_width}px` : ""}">${body}</div></ha-card>`;
    this.shadowRoot.querySelectorAll(".tile, .hat").forEach((el) => el.addEventListener("click", () => this.more(TILE_ENTITY[el.dataset.k])));
  }

  /* ---- "Home Assistant" appearance: tile-card style rendering ---------------- */

  _haSpark(values, dot, color) {
    const vals = values.filter((v) => num(v) !== null);
    if (vals.length < 2) return "";
    const mn = Math.min(...vals), mx = Math.max(...vals), rng = mx - mn || 1;
    const pts = values.map((v, i) => [(i * 100) / (values.length - 1), 4 + 32 * (1 - ((num(v) ?? mn) - mn) / rng)]);
    const di = clamp(dot, 0, pts.length - 1);
    const p = smoothPath(pts);
    return `<svg class="fill" viewBox="0 0 100 40" preserveAspectRatio="none">
        <path d="${p} L100,40 L0,40 Z" fill="${color}" opacity="0.15"/>
        <path d="${p}" stroke="${color}" stroke-width="2" fill="none" vector-effect="non-scaling-stroke"/></svg>
      <span class="dot" style="left:${pts[di][0]}%;top:${(pts[di][1] / 40) * 100}%"></span>`;
  }

  _haBar(frac, { marker = false, track = null } = {}) {
    const f = clamp(frac || 0, 0, 1) * 100;
    return `<div class="bar" ${track ? `style="background:${track}"` : ""}>${marker ? `<b style="left:${f}%"></b>` : `<i style="width:${f}%"></i>`}</div>`;
  }

  _haTile(k, d) {
    const L = lang(this._hass);
    const C = {
      orange: "var(--orange-color, #ff9800)", deep: "var(--deep-orange-color, #ff5722)", blue: "var(--blue-color, #2196f3)",
      lblue: "var(--light-blue-color, #03a9f4)", cyan: "var(--cyan-color, #00bcd4)", teal: "var(--teal-color, #009688)",
      green: "var(--green-color, #4caf50)", amber: "var(--amber-color, #ffc107)", purple: "var(--purple-color, #9c27b0)",
      indigo: "var(--indigo-color, #3f51b5)", grey: "var(--blue-grey-color, #607d8b)",
    };
    const tz = this._tz();
    const tile = { icon: "mdi:weather-partly-cloudy", color: C.blue, value: "", sub: "", feat: "" };
    const v = (key) => this.val(key);
    switch (k) {
      case "temperature": {
        const { values, dot } = this._todaySeries("temperature", "temperature");
        Object.assign(tile, { icon: "mdi:thermometer", color: C.orange, value: `${fmt(v("temperature"))} ${this._unit("temp")}`, feat: this._haSpark(values, dot, C.orange) });
        break;
      }
      case "feels": {
        const { values, dot } = this._todaySeries("apparent_temperature", "apparent_temperature");
        Object.assign(tile, { icon: "mdi:sun-thermometer-outline", color: C.deep, value: `${fmt(v("apparent_temperature"))} ${this._unit("temp")}`,
          sub: `${this.t("tempLabel")} ${fmt(v("temperature"))}°`, feat: this._haSpark(values, dot, C.deep) });
        break;
      }
      case "clouds": {
        const cc = num(v("cloud_cover"));
        Object.assign(tile, { icon: "mdi:weather-cloudy", color: C.grey, value: `${fmt(cc)} %`, sub: this.attr("condition", "short") || v("condition") || "",
          feat: this._haBar((cc || 0) / 100) });
        break;
      }
      case "precipitation": {
        const fc = this._fc("precipitation", 24).map((x) => num(x) || 0);
        const sum = fc.length ? fc.reduce((a, b) => a + b, 0) : num(v("precipitation_today"));
        const mx = Math.max(this._unit("precip") === "in" ? 0.04 : 1, ...fc);
        const bars = fc.map((x, i) => `<rect x="${i * (100 / 24) + 0.6}" y="${40 - (x / mx) * 38}" width="${100 / 24 - 1.2}" height="${Math.max((x / mx) * 38, 1)}" rx="0.8" fill="${C.blue}" opacity="${x ? 1 : 0.25}"/>`).join("");
        Object.assign(tile, { icon: "mdi:weather-rainy", color: C.blue, value: `${fmt(sum, this._dec("precip"))} ${this._unit("precip")}`, sub: pick(L, { de: "nächste 24 h", en: "next 24 h", it: "prossime 24 h", fr: "prochaines 24 h", es: "próximas 24 h", nl: "komende 24 uur" }),
          feat: fc.length ? `<svg class="fill" viewBox="0 0 100 40" preserveAspectRatio="none">${bars}</svg>` : "" });
        break;
      }
      case "nowcast": {
        const info = nowcastInfo(this.st("nowcast"), this._hass);
        Object.assign(tile, { icon: info.icon, color: info.kind === "dry" ? C.grey : C.blue, value: info.text, feat: info.spark });
        break;
      }
      case "wind": {
        const brg = num(v("wind_bearing")) || 0;
        Object.assign(tile, { icon: "mdi:weather-windy", color: C.cyan, value: `${fmt(v("wind_speed"))} ${this._unit("wind")}`, sub: `${this.t("gusts")} ${fmt(v("wind_gust"))}`,
          feat: `<svg viewBox="0 0 40 40" width="40" height="40" style="flex:none"><circle cx="20" cy="20" r="17" fill="none" stroke="var(--divider-color, #8884)" stroke-width="2"/>
            <g transform="rotate(${(brg + 180) % 360} 20 20)"><path d="M20 6 L25 28 L20 24 L15 28 Z" fill="${C.cyan}"/></g></svg>
            <span>${this.t("from")} ${esc(v("wind_direction") || "")} (${fmt(brg)}°)</span>` });
        break;
      }
      case "humidity": {
        const h = num(v("humidity"));
        Object.assign(tile, { icon: "mdi:water-percent", color: C.lblue, value: `${fmt(h)} %`, sub: `${this.t("dewpoint")} ${fmt(v("dew_point"))}°`, feat: this._haBar((h || 0) / 100) });
        break;
      }
      case "uv": {
        const uv = num(v("uv_index"));
        Object.assign(tile, { icon: "mdi:sun-wireless-outline", color: C.amber, value: fmt(uv), sub: this.attr("uv_index", "level") || "",
          feat: this._haBar((uv || 0) / 11, { marker: true, track: "linear-gradient(90deg,#6ab04c,#f6e30d,#f39c12,#e74c3c,#8e44ad)" }) });
        break;
      }
      case "aqi": {
        const a = num(v("aqi"));
        Object.assign(tile, { icon: "mdi:air-filter", color: aqiColor(a), value: fmt(a), sub: this.attr("aqi", "severity") || "",
          feat: this._haBar((a || 0) / 300, { marker: true, track: "linear-gradient(90deg,#00ae56 0%,#d4a017 30%,#f2610c 48%,#d13438 65%,#88179a 85%,#6e220f 100%)" }) });
        break;
      }
      case "pollen": {
        const po = num(v("pollen"));
        const al = this.attr("pollen", "main_allergen");
        Object.assign(tile, { icon: "mdi:flower-pollen-outline", color: C.green, value: po === null ? "–" : fmt(po),
          sub: al ? `${this.t("mainAllergen")}: ${(ALLERGEN[L] || {})[al] || al}` : "",
          feat: this._haBar((po || 0) / 120, { marker: true, track: "linear-gradient(90deg,#16a34a,#eab308,#f97316,#dc2626)" }) });
        break;
      }
      case "visibility": {
        const vi = num(v("visibility"));
        Object.assign(tile, { icon: "mdi:eye-outline", color: C.teal, value: `${fmt(vi, 1)} ${this._unit("vis")}`, sub: this.attr("visibility", "level") || "", feat: this._haBar((vi || 0) / (this._unit("vis") === "mi" ? 30 : 50)) });
        break;
      }
      case "pressure": {
        const { values, dot } = this._todaySeries("pressure", "pressure");
        Object.assign(tile, { icon: "mdi:gauge", color: C.purple, value: `${fmt(v("pressure"), this._dec("pressure"))} ${this._unit("pressure")}`, feat: this._haSpark(values, dot, C.purple) });
        break;
      }
      case "sun":
      case "moon": {
        const sun = k === "sun";
        const r = v(sun ? "sunrise" : "moonrise"), st = v(sun ? "sunset" : "moonset"), dur = num(v(sun ? "daylight" : "moon_visible"));
        let frac = 0;
        if (r && st) { let a = new Date(r).getTime(), b = new Date(st).getTime(); if (b < a) b += 86400000; frac = (Date.now() - a) / (b - a); }
        Object.assign(tile, { icon: sun ? "mdi:weather-sunset" : "mdi:weather-night", color: sun ? C.deep : C.indigo,
          value: `↑ ${timeStr(r, this._hass, tz)}`, sub: `↓ ${timeStr(st, this._hass, tz)}`,
          feat: this._haBar(frac, { marker: frac >= 0 && frac <= 1 })
            + (dur === null ? "" : `<span>${Math.floor(dur / 60)} ${this.t("hrs")} ${Math.round(dur % 60)} ${this.t("min")}</span>`) });
        break;
      }
      case "moonphase": {
        const ill = num(v("moon_illumination")) || 0;
        const code = this.attr("moon_phase", "code") || "";
        const icon = /New/i.test(code) ? "mdi:moon-new" : /Full/i.test(code) ? "mdi:moon-full" : /^Wa/i.test(code) ? "mdi:moon-waning-crescent" : "mdi:moon-waxing-crescent";
        const nf = this.attr("moon_phase", "next_full_moon");
        Object.assign(tile, { icon, color: C.amber, value: `${fmt(ill)} %`, sub: v("moon_phase") || "",
          feat: nf ? `<span>${this.t("nextFull")}: <b style="color:var(--primary-text-color)">${new Date(nf + "T12:00:00").toLocaleDateString(this._hass.language, { day: "numeric", month: "short" })}</b></span>` : "" });
        break;
      }
    }
    const tr = (d.trend || "").toLowerCase();
    const trendIc = d.trend === undefined ? "" : tr.startsWith("incr") ? "mdi:trending-up" : tr.startsWith("decr") ? "mdi:trending-down" : "mdi:trending-neutral";
    const text = [d.headline ? `<b>${esc(d.headline)}</b>` : "", d.summary ? esc(d.summary) : ""].filter(Boolean).join(" · ");
    return `<div class="hat" data-k="${k}" style="--c:${tile.color}">
      <div class="top"><div class="ic"><ha-icon icon="${tile.icon}"></ha-icon></div>
        <div class="nm"><span class="name">${esc(d.title)}</span>
          <span class="val">${esc(tile.value)}${tile.sub ? `<small>${esc(tile.sub)}</small>` : ""}${trendIc ? `<ha-icon icon="${trendIc}"></ha-icon>` : ""}</span></div></div>
      ${tile.feat ? `<div class="feat">${tile.feat}</div>` : ""}
      ${text ? `<div class="txt">${text}</div>` : ""}
    </div>`;
  }

  _tile(k, data) {
    if (this._ha) return this._haTile(k, data);
    const { title, viz, headline, summary, trend } = data;
    return `<div class="tile" data-k="${k}">
      <div class="t">${esc(title)}</div>
      <div class="viz">${viz}</div>
      ${headline ? `<div class="hl">${esc(headline)} ${trend !== undefined ? trendIcon(trend) : ""}</div>` : ""}
      ${summary ? `<div class="sm">${esc(summary)}</div>` : ""}
    </div>`;
  }

  _fc(field, n = 24) {
    return (this._forecast || []).slice(0, n).map((f) => f[field]);
  }

  /** Today's curve (00–23 h) from MSN with the dot at the current hour; falls back to the forecast. */
  _todaySeries(key, fcField) {
    const ser = this.attr(key, "today_series");
    if (ser && Object.keys(ser).length > 6) {
      const ks = Object.keys(ser).sort();
      const n = this._locNow();
      const pad = (v) => String(v).padStart(2, "0");
      const nowKey = `${n.y}/${pad(n.mo)}/${pad(n.d)} ${pad(n.h)}:00`;
      let idx = ks.findIndex((k) => k >= nowKey);
      if (idx < 0) idx = ks.length - 1;
      return { values: ks.map((k) => ser[k]), dot: idx };
    }
    return { values: [num(this.val(key)), ...this._fc(fcField, 18)], dot: 0 };
  }

  /* ---- tile visualisations: pure SVG with a fixed 300×140 geometry, so every tile scales uniformly ---- */

  _svg(inner) {
    return `<svg class="vz" viewBox="0 0 300 140" preserveAspectRatio="xMidYMid meet">${inner}</svg>`;
  }

  _spark(values, x0, y0, w, h, color, dot = 0, fill = true) {
    const vals = values.filter((v) => num(v) !== null);
    if (vals.length < 2) return "";
    const mn = Math.min(...vals), mx = Math.max(...vals), rng = mx - mn || 1;
    const pts = values.map((v, i) => [x0 + (i * w) / (values.length - 1), y0 + h * (1 - ((num(v) ?? mn) - mn) / rng)]);
    const di = clamp(dot, 0, pts.length - 1);
    const area = fill ? `<path d="${smoothPath(pts)} L${pts[pts.length - 1][0]},${y0 + h + 4} L${pts[0][0]},${y0 + h + 4} Z" fill="${color}" opacity="0.13"/>` : "";
    return `${area}
      ${di > 0 ? `<path d="${smoothPath(pts.slice(0, di + 1))}" stroke="${color}" stroke-width="5" fill="none" stroke-linecap="round"/>` : ""}
      <path d="${smoothPath(pts.slice(di))}" stroke="${di > 0 ? "var(--msn-muted-line)" : color}" stroke-width="5" fill="none" stroke-linecap="round"/>
      <circle cx="${pts[di][0]}" cy="${pts[di][1]}" r="8" fill="${color}" stroke="#fff" stroke-width="3"/>`;
  }

  _txt(x, y, text, size = 13, { weight = 400, anchor = "start", muted = false } = {}) {
    return `<text x="${x}" y="${y}" font-size="${size}" font-weight="${weight}" text-anchor="${anchor}" fill="currentColor"${muted ? ' opacity="0.65"' : ""}>${esc(text)}</text>`;
  }

  tile_temperature() {
    const v = this.val("temperature");
    const { values, dot } = this._todaySeries("temperature", "temperature");
    return {
      title: this.t("temperature"),
      viz: this._svg(this._spark(values, 8, 48, 284, 80, "#22c1c3", dot) + this._txt(292, 38, `${fmt(v)}°`, 38, { weight: 700, anchor: "end" })),
      headline: this.attr("temperature", "headline"), summary: this.attr("temperature", "summary"), trend: this.attr("temperature", "trend"),
    };
  }

  tile_feels() {
    const f = this.val("apparent_temperature"), tv = this.val("temperature");
    const { values, dot } = this._todaySeries("apparent_temperature", "apparent_temperature");
    return {
      title: this.t("feels"),
      viz: this._svg(this._spark(values, 8, 12, 284, 44, "#93c5fd", dot, false)
        + this._txt(4, 124, this.t("feelsLabel") + ":", 12, { muted: true }) + this._txt(60, 126, `${fmt(f)}°`, 34, { weight: 700 })
        + this._txt(208, 124, this.t("tempLabel") + ":", 12, { muted: true, anchor: "end" }) + this._txt(296, 126, `${fmt(tv)}°`, 34, { weight: 700, anchor: "end" })),
      headline: this.attr("apparent_temperature", "headline"), summary: this.attr("apparent_temperature", "summary"), trend: this.attr("apparent_temperature", "trend"),
    };
  }

  tile_clouds() {
    const cc = num(this.val("cloud_cover"));
    const txt = this.attr("condition", "short") || this.val("condition") || "";
    const id = "cg" + Math.random().toString(36).slice(2, 7);
    return {
      title: this.t("clouds"),
      viz: this._svg(`<defs><radialGradient id="${id}" cx="50%" cy="40%" r="60%"><stop offset="0" stop-color="#bfe3ff" stop-opacity="${0.55 + (cc || 0) / 300}"/><stop offset="1" stop-color="#64748b" stop-opacity="0.35"/></radialGradient></defs>
        <circle cx="150" cy="70" r="64" fill="url(#${id})"/>${this._txt(150, 76, txt, txt.length > 12 ? 15 : 18, { weight: 700, anchor: "middle" })}`),
      headline: `${txt}${cc !== null ? ` (${fmt(cc)}%)` : ""}`, summary: this.attr("cloud_cover", "summary"), trend: this.attr("cloud_cover", "trend"),
    };
  }

  tile_precipitation() {
    const fc = this._fc("precipitation", 24).map((v) => num(v) || 0);
    const sum24 = fc.length ? fc.reduce((a, b) => a + b, 0) : num(this.val("precipitation_today"));
    return {
      title: this.t("precipitation"),
      viz: this._svg(`<circle cx="150" cy="70" r="64" fill="currentColor" opacity="0.08"/>
        <text x="150" y="72" text-anchor="middle" fill="currentColor"><tspan font-size="34" font-weight="700">${fmt(sum24, this._dec("precip"))}</tspan><tspan font-size="15" dx="3">${this._unit("precip")}</tspan></text>
        ${this._txt(150, 96, this.t("next24"), 11, { weight: 600, anchor: "middle", muted: true })}`),
      headline: this.attr("precipitation_today", "headline"), summary: this.attr("precipitation_today", "summary"), trend: this.attr("precipitation_today", "trend"),
    };
  }

  tile_nowcast() {
    const info = nowcastInfo(this.st("nowcast"), this._hass);
    return {
      title: this.t("nowcastTile"),
      viz: this._svg(`${this._txt(150, 34, info.text, info.text.length > 22 ? 17 : 21, { weight: 700, anchor: "middle" })}
        <g transform="translate(12 52) scale(2.76 2)">${info.spark.replace(/<\/?svg[^>]*>/g, "")}</g>`),
      headline: info.summary,
    };
  }

  tile_wind() {
    const spd = this.val("wind_speed"), gust = this.val("wind_gust");
    const brg = num(this.val("wind_bearing")) || 0, dir = this.val("wind_direction") || "";
    const L = { de: ["N", "O", "S", "W"], it: ["N", "E", "S", "O"], fr: ["N", "E", "S", "O"], es: ["N", "E", "S", "O"], nl: ["N", "O", "Z", "W"] }[lang(this._hass)] || ["N", "E", "S", "W"];
    const rot = (brg + 180) % 360;
    return {
      title: this.t("wind"),
      viz: this._svg(`<g transform="translate(14 8)">
          <circle cx="62" cy="62" r="52" fill="none" stroke="var(--msn-muted-line)" stroke-width="5"/>
          <path d="${arcPath(62, 62, 52, brg - 25, brg + 25)}" stroke="#60a5fa" stroke-width="6" fill="none" stroke-linecap="round"/>
          ${this._txt(62, 4, L[0], 12, { anchor: "middle" })}${this._txt(124, 66, L[1], 12, { anchor: "middle" })}
          ${this._txt(62, 132, L[2], 12, { anchor: "middle" })}${this._txt(0, 66, L[3], 12, { anchor: "middle" })}
          <g transform="rotate(${rot} 62 62)"><path d="M62 24 L76 88 Q62 80 48 88 Z" fill="#60a5fa"/></g></g>
        ${this._txt(160, 26, `${this.t("from")} ${dir} (${fmt(brg)}°)`, 13)}
        ${this._txt(160, 74, fmt(spd), 34, { weight: 700 })}${this._txt(214, 60, this._unit("wind"), 11, { muted: true })}${this._txt(214, 74, this.t("windspeed"), 11, { muted: true })}
        ${this._txt(160, 124, fmt(gust), 34, { weight: 700 })}${this._txt(214, 110, this._unit("wind"), 11, { muted: true })}${this._txt(214, 124, this.t("gusts"), 11, { muted: true })}`),
      headline: this.attr("wind_speed", "headline"), summary: this.attr("wind_speed", "summary"), trend: this.attr("wind_speed", "trend"),
    };
  }

  tile_humidity() {
    const h = num(this.val("humidity")) || 0, dp = this.val("dew_point");
    const bars = Array.from({ length: 7 }, (_, i) => {
      const x = 10 + i * 19;
      return `<rect x="${x}" y="8" width="10" height="124" rx="5" fill="var(--msn-muted-line)"/>
              <rect x="${x}" y="${8 + 124 * (1 - h / 100)}" width="10" height="${124 * h / 100}" rx="5" fill="#5b8def"/>`;
    }).join("");
    return {
      title: this.t("humidity"),
      viz: this._svg(bars + this._txt(160, 46, `${fmt(h)}%`, 34, { weight: 700 }) + this._txt(160, 64, this.t("relhum"), 12, { muted: true })
        + this._txt(160, 110, `${fmt(dp)}°`, 34, { weight: 700 }) + this._txt(160, 128, this.t("dewpoint"), 12, { muted: true })),
      headline: this.attr("humidity", "headline"), summary: this.attr("humidity", "summary"), trend: this.attr("humidity", "trend"),
    };
  }

  _gaugeSvg(value, max, color, segments = null, label = "") {
    const cx = 150, cy = 72, r = 58;
    const a = -140 + clamp((value || 0) / max, 0, 1) * 280;
    const [px, py] = arcPoint(cx, cy, r, a);
    const track = segments
      ? segments.map(([c, a0, a1]) => `<path d="${arcPath(cx, cy, r, a0, a1)}" stroke="${c}" stroke-width="7" fill="none" stroke-linecap="round"/>`).join("")
      : `<path d="${arcPath(cx, cy, r, -140, 140)}" stroke="var(--msn-muted-line)" stroke-width="7" fill="none" stroke-linecap="round"/>
         ${a > -139 ? `<path d="${arcPath(cx, cy, r, -140, a)}" stroke="${color}" stroke-width="7" fill="none" stroke-linecap="round"/>` : ""}`;
    return this._svg(`${track}<circle cx="${px}" cy="${py}" r="9" fill="${color}" stroke="#fff" stroke-width="3"/>
      ${this._txt(cx, cy + 14, value === null ? "–" : fmt(value), 40, { anchor: "middle" })}
      ${label ? this._txt(cx, 138, label, 12, { anchor: "middle" }) : ""}`);
  }

  tile_uv() {
    const uv = num(this.val("uv_index"));
    const segs = [["#6ab04c", -140, -78], ["#f6e30d", -72, -26], ["#f39c12", -20, 26], ["#e74c3c", 32, 78], ["#8e44ad", 84, 140]];
    return {
      title: this.t("uv"),
      viz: this._gaugeSvg(uv, 11, "#f6e30d", segs),
      headline: this.attr("uv_index", "headline") || this.attr("uv_index", "level"), summary: this.attr("uv_index", "summary"), trend: this.attr("uv_index", "trend"),
    };
  }

  tile_aqi() {
    const v = num(this.val("aqi"));
    return {
      title: this.t("aqi"),
      viz: this._gaugeSvg(v, 300, aqiColor(v)),
      headline: this.attr("aqi", "headline") || this.attr("aqi", "severity"), summary: this.attr("aqi", "summary"), trend: this.attr("aqi", "trend"),
    };
  }

  tile_pollen() {
    const v = num(this.val("pollen"));
    const al = this.attr("pollen", "main_allergen");
    const alName = (ALLERGEN[lang(this._hass)] || {})[al] || al || "";
    const c = v === null ? "#999" : v < 30 ? "#16a34a" : v < 60 ? "#eab308" : v < 90 ? "#f97316" : "#dc2626";
    return {
      title: this.t("pollen"),
      viz: this._gaugeSvg(v, 120, c, null, alName ? `${this.t("mainAllergen")}: ${alName}` : ""),
      headline: this.attr("pollen", "headline") || this.attr("pollen", "level"), summary: this.attr("pollen", "summary"), trend: this.attr("pollen", "trend"),
    };
  }

  tile_visibility() {
    const v = num(this.val("visibility"));
    const level = clamp(Math.round(((v || 0) / (this._unit("vis") === "mi" ? 30 : 50)) * 5), 1, 5);
    const bars = [0, 1, 2, 3, 4].map((i) => {
      const w = 70 + i * 26, on = i >= 5 - level;
      return `<rect x="${150 - w / 2}" y="${6 + i * 15}" width="${w}" height="8" rx="4" fill="${on ? (i === 4 ? "#86d19c" : "#3aa76d") : "var(--msn-muted-line)"}"/>`;
    }).join("");
    return {
      title: this.t("visibility"),
      viz: this._svg(bars + `<text x="150" y="128" text-anchor="middle" fill="currentColor"><tspan font-size="36" font-weight="700">${fmt(v, 1)}</tspan><tspan font-size="15" dx="3">${this._unit("vis")}</tspan></text>`),
      headline: this.attr("visibility", "headline") || this.attr("visibility", "level"), summary: this.attr("visibility", "summary"), trend: this.attr("visibility", "trend"),
    };
  }

  tile_pressure() {
    const v = this.val("pressure");
    const { values, dot } = this._todaySeries("pressure", "pressure");
    return {
      title: this.t("pressure"),
      viz: this._svg(this._spark(values, 8, 12, 284, 40, "#a78bfa", dot, false)
        + this._txt(4, 118, fmt(v, this._dec("pressure")), 36, { weight: 700 }) + this._txt(100, 100, this._unit("pressure"), 13, { muted: true })
        + this._txt(100, 118, `${timeStr(new Date().toISOString(), this._hass, this._tz())} (${this.t("now")})`, 13, { weight: 700 })),
      headline: this.attr("pressure", "headline"), summary: this.attr("pressure", "summary"), trend: this.attr("pressure", "trend"),
    };
  }

  _celestialSvg(riseIso, setIso, durationMin, gradient, icon) {
    const rise = riseIso ? new Date(riseIso) : null, set = setIso ? new Date(setIso) : null;
    let frac = null;
    if (rise && set) {
      let s = set.getTime(); const r = rise.getTime();
      if (s < r) s += 86400000;
      frac = (Date.now() - r) / (s - r);
    }
    const H = 70, A = 54, X0 = 80, X1 = 220;
    const yAt = (t) => (t >= 0 && t <= 1 ? H - Math.sin(Math.PI * t) * A : H + Math.min(24, Math.abs(t < 0 ? t : t - 1) * 52));
    const pts = [];
    for (let i = 0; i <= 60; i++) { const x = 20 + (i / 60) * 260; pts.push([x, yAt((x - X0) / (X1 - X0))]); }
    const pt = frac === null ? 0.5 : clamp(frac, -0.42, 1.42);
    const px = X0 + pt * (X1 - X0), py = yAt(pt);
    const h = num(durationMin);
    const dur = h === null ? "" : `${Math.floor(h / 60)} ${this.t("hrs")} ${Math.round(h % 60)} ${this.t("min")}`;
    const id = "g" + Math.random().toString(36).slice(2, 7);
    return this._svg(`<defs><linearGradient id="${id}" x1="0" x2="1"><stop offset="0" stop-color="${gradient[0]}"/><stop offset="1" stop-color="${gradient[1]}"/></linearGradient></defs>
      <line x1="20" y1="${H}" x2="280" y2="${H}" stroke="var(--msn-muted-line)"/>
      <path d="${smoothPath(pts)}" stroke="var(--msn-muted-line)" stroke-width="6" fill="none" stroke-linecap="round"/>
      <path d="${smoothPath(pts.filter((p) => p[0] >= X0 && p[0] <= X1))}" stroke="url(#${id})" stroke-width="6" fill="none" stroke-linecap="round"/>
      <circle cx="${X0}" cy="${H}" r="5" fill="#fff" stroke="#bbb" stroke-width="2"/><circle cx="${X1}" cy="${H}" r="5" fill="#fff" stroke="#bbb" stroke-width="2"/>
      <circle cx="${px}" cy="${py}" r="11" fill="#fff" stroke="#ddd" stroke-width="2"/><text x="${px}" y="${py + 5}" text-anchor="middle" font-size="13">${icon}</text>
      ${this._txt(150, 92, dur, 12, { weight: 700, anchor: "middle" })}
      ${this._txt(4, 126, timeStr(riseIso, this._hass, this._tz()), 26, { weight: 700 })}
      ${this._txt(296, 126, timeStr(setIso, this._hass, this._tz()), 26, { weight: 700, anchor: "end" })}`);
  }

  tile_sun() {
    return {
      title: this.t("sun"),
      viz: this._celestialSvg(this.val("sunrise"), this.val("sunset"), this.val("daylight"), ["#e5484d", "#7c3aed"], "☀️"),
      headline: `${this.t("sunrise")} · ${this.t("sunset")}`,
    };
  }

  tile_moon() {
    return {
      title: this.t("moon"),
      viz: this._celestialSvg(this.val("moonrise"), this.val("moonset"), this.val("moon_visible"), ["#f0b429", "#f97316"], "🌙"),
      headline: `${this.t("moonrise")} · ${this.t("moonset")}`,
    };
  }

  tile_moonphase() {
    const ill = num(this.val("moon_illumination")) || 0;
    const code = this.attr("moon_phase", "code") || "";
    const waxing = !/^Wa/i.test(code);
    const k = 1 - (2 * ill) / 100;
    const rx = Math.abs(k) * 56;
    const sweepOuter = waxing ? 1 : 0;
    const sweepInner = k > 0 ? (waxing ? 0 : 1) : (waxing ? 1 : 0);
    const cx = 70, cy = 70;
    const lit = `M${cx},14 A56,56 0 0 ${sweepOuter} ${cx},126 A${rx},56 0 0 ${sweepInner} ${cx},14 Z`;
    const nf = this.attr("moon_phase", "next_full_moon");
    const nfTxt = nf ? new Date(nf + "T12:00:00").toLocaleDateString(this._hass.language, { day: "numeric", month: "short" }) : "–";
    return {
      title: this.t("moonphase"),
      viz: this._svg(`<circle cx="${cx}" cy="${cy}" r="56" fill="currentColor" opacity="0.1"/><path d="${lit}" fill="#f0b429"/>
        ${this._txt(150, 64, `${fmt(ill)}%`, 38)}${this._txt(150, 86, this.val("moon_phase") || "", 12, { muted: true })}
        ${this._txt(150, 116, this.t("nextFull"), 12, { muted: true })}${this._txt(150, 134, nfTxt, 14, { weight: 700 })}`),
      headline: this.val("moon_phase"),
    };
  }
}

class MsnWeatherDetailsCard extends MsnTiles {
  static getConfigForm() {
    return {
      schema: [
        { name: "entity", required: true, selector: { entity: { domain: "weather", integration: "msn_weather" } } },
        { name: "title", selector: { text: {} } },
        { name: "tiles", selector: { select: { multiple: true, reorder: true, options: ALL_TILES.map((k) => ({ value: k, label: ((UI_DE ? T.de : T.en)[TILE_LABEL_KEY[k]] || k) })) } } },
      ],
    };
  }
}

const TILE_LABEL_KEY = {
  temperature: "temperature", feels: "feels", clouds: "clouds", precipitation: "precipitation", nowcast: "nowcastTile", wind: "wind",
  humidity: "humidity", uv: "uv", aqi: "aqi", pollen: "pollen", visibility: "visibility", pressure: "pressure",
  sun: "sun", moon: "moon", moonphase: "moonphase",
};

/** A single MSN tile as its own card – for free placement in sections dashboards. */
class MsnWeatherTileCard extends MsnTiles {
  static getStubConfig(hass) { return { ...MsnTiles.getStubConfig(hass), tile: "temperature" }; }
  static getConfigForm() {
    return {
      schema: [
        { name: "entity", required: true, selector: { entity: { domain: "weather", integration: "msn_weather" } } },
        { name: "tile", required: true, selector: { select: { mode: "dropdown", options: ALL_TILES.map((k) => ({ value: k, label: (UI_DE ? T.de : T.en)[TILE_LABEL_KEY[k]] || k })) } } },
      ],
    };
  }
  getCardSize() { return 3; }
  getGridOptions() { return this._ha ? { columns: 6, rows: 2, min_columns: 3, min_rows: 1 } : { columns: 6, rows: 3, min_columns: 3, min_rows: 2 }; }
  _needsForecast() { return ["temperature", "feels", "precipitation", "pressure"].includes(this._config.tile); }
  _render() {
    if (!this._hass) return;
    const k = this._config.tile || "temperature";
    if (!this._ents.temperature || !this["tile_" + k]) {
      this.shadowRoot.innerHTML = `<ha-card><div class="err">${this.t("notFound")} ${esc(this._config.entity)}</div></ha-card>`;
      return;
    }
    this.shadowRoot.innerHTML = `<style>${this._css()}
      :host { display: block; height: 100%; }
      ha-card { height: 100%; padding: 0; box-sizing: border-box; overflow: hidden; container-type: size; }
      .tile { background: none; height: 100%; min-height: 110px; cursor: pointer; padding: 10px 12px; }
      /* small tiles: drop the explanation first, then the headline */
      @container (max-height: 175px) { .tile .sm { display: none; } }
      @container (max-height: 120px) { .tile .hl { display: none; } .tile .t { margin-bottom: 0; } }
      @container (max-height: 150px) { .hat .txt { display: none; } }
      @container (max-height: 92px) { .hat .feat { display: none; } }
    </style><ha-card>${this._tile(k, this["tile_" + k]())}</ha-card>`;
    this.shadowRoot.querySelector(".tile, .hat").addEventListener("click", () => this.more(TILE_ENTITY[k]));
  }
}

/* ----------------------------------------------------------------------- */
/* Life card                                                                */
/* ----------------------------------------------------------------------- */
const CAT_COLORS = ["#4caf50", "#8bc34a", "#ffc107", "#ff7043", "#e53935"];
const DRESS_COLORS = ["#86d07a", "#8ab4f8", "#8e9cf0", "#8f91e8", "#6f6fd8"];

class MsnWeatherLifeCard extends MsnBase {
  static getStubConfig(hass) { return { ...MsnWeatherDetailsCard.getStubConfig(hass), mode: "health" }; }
  static getConfigForm() {
    return {
      schema: [
        { name: "entity", required: true, selector: { entity: { domain: "weather", integration: "msn_weather" } } },
        { name: "mode", selector: { select: { options: [{ value: "health", label: "Health and safety" }, { value: "activities", label: "Activities" }] } } },
        { name: "title", selector: { text: {} } },
      ],
    };
  }
  get _responsive() { return true; }
  getCardSize() { return 7; }
  getGridOptions() { return { columns: "full", rows: "auto", min_columns: 6 }; }
  _needsForecast() { return false; }

  _render() {
    if (!this._hass) return;
    const L = lang(this._hass);
    const narrow = this._width < 640;
    const mode = this._config.mode === "activities" ? "activities" : "health";
    const items = (LIFE_ITEMS[mode]).filter(([k]) => this._ents[k] && this.st(k));
    if (!items.length) {
      this.shadowRoot.innerHTML = `<ha-card><div class="err">${this.t("notFound")} ${esc(this._config.entity)} (${mode})</div></ha-card>`;
      return;
    }
    if (!this._sel || !items.find(([k]) => k === this._sel)) this._sel = items[0][0];
    const sel = items.find(([k]) => k === this._sel);
    const s = this.st(sel[0]);
    const levels = (LIFE_LEVELS[L] || LIFE_LEVELS.en)[sel[1]];
    const hourly = (s.attributes.hourly || []).slice(0, 24);
    const colors = sel[1] === "dressing" ? DRESS_COLORS : CAT_COLORS;
    const dot = (cat) => (cat ? colors[clamp(cat, 1, 5) - 1] : "#888");
    if (this._ha) { this._renderHa(mode, items, sel, s, levels, hourly, dot); return; }
    const list = items.map(([k, kind, icon]) => {
      const st = this.st(k);
      const name = (st.attributes.friendly_name || k).replace(/^.*?\s(?=\S+$)/, "");
      return `<div class="li ${k === this._sel ? "on" : ""}" data-k="${k}">
        <ha-icon icon="${icon}"></ha-icon><b>${esc(this._lifeName(k, st))}</b>
        <span class="st">${esc(st.state)}</span><span class="dot" style="background:${dot(st.attributes.category)}"></span></div>`;
    }).join("");

    // chart
    const W = 640, H = 230, left = 200, top = 16, bottom = 196;
    const n = Math.max(hourly.length, 1), bw = (W - left - 10) / n;
    const rowY = (i) => bottom - ((i + 1) * (bottom - top)) / 5;
    let grid = levels.map((lv, i) => `<text x="${left - 10}" y="${rowY(i) + 4}" text-anchor="end" font-size="13" fill="currentColor" opacity="0.8">${esc(lv)}</text>
      <line x1="${left}" x2="${W - 10}" y1="${rowY(i)}" y2="${rowY(i)}" stroke="var(--msn-muted-line)"/>`).join("");
    let bars = "", ticks = "", dayLine = "";
    let prevDay = null;
    hourly.forEach((h, i) => {
      // category 0 = index does not apply at that hour (e.g. cycling at night)
      const raw = num(h.category) || 0, cat = clamp(raw, 1, 5);
      const x = left + i * bw + 2, y = raw ? rowY(cat - 1) + 4 : bottom - 3;
      bars += `<rect x="${x}" y="${y}" width="${Math.max(bw - 4, 2)}" height="${bottom - y}" rx="2" fill="${raw ? dot(cat) : "var(--msn-muted-line)"}"><title>${esc(raw ? levels[cat - 1] : "–")}</title></rect>`;
      const d = new Date(h.time);
      if (i % 3 === 0) ticks += `<text x="${x + bw / 2}" y="${bottom + 18}" text-anchor="middle" font-size="12" fill="currentColor" opacity="0.8">${timeStr(h.time, this._hass, this._tz())}</text>`;
      const day = d.toDateString();
      if (prevDay && day !== prevDay) dayLine = `<line x1="${x - 2}" x2="${x - 2}" y1="${top - 6}" y2="${bottom}" stroke="currentColor" stroke-dasharray="3 3" opacity="0.6"/>
        <text x="${x - 6}" y="${top - 8}" text-anchor="end" font-size="11" fill="currentColor">${this.t("today")}</text>
        <text x="${x + 2}" y="${top - 8}" font-size="11" fill="currentColor">${d.toLocaleDateString(this._hass.language, { weekday: "short", day: "numeric" })}</text>`;
      prevDay = day;
    });
    const chart = hourly.length
      ? `<svg class="lc" viewBox="0 0 ${W} ${H + 10}" preserveAspectRatio="xMidYMid meet">${grid}${bars}${dayLine}${ticks}</svg>`
      : `<div class="lbl">${this.t("noData")}</div>`;

    this.shadowRoot.innerHTML = `<style>${this._css()}
      :host { height: 100%; }
      ha-card { height: 100%; box-sizing: border-box; display: flex; flex-direction: column; overflow: hidden; }
      .head { flex: none; }
      .wrap { flex: 1 1 auto; min-height: ${narrow ? 380 : 300}px; display: grid; gap: 14px;
              grid-template-columns: ${narrow ? "1fr" : "minmax(200px, 30%) 1fr"}; grid-template-rows: ${narrow ? "auto minmax(0, 1fr)" : "minmax(0, 1fr)"}; }
      .list { min-height: 0; display: ${narrow ? "flex" : "flex"}; flex-direction: ${narrow ? "row" : "column"}; flex-wrap: ${narrow ? "wrap" : "nowrap"}; gap: 6px; overflow: hidden; }
      .li { display:flex; align-items:center; gap:8px; padding: 0 12px; border-radius: 12px; background: var(--msn-tile-bg); cursor:pointer; border: 2px solid transparent;
            ${narrow ? "min-height: 36px;" : "flex: 1 1 0; min-height: 34px; max-height: 58px;"} min-width: 0; }
      .li.on { border-color: var(--primary-text-color); }
      .li ha-icon { --mdc-icon-size: 20px; flex: none; }
      .li b { flex: 1; font-size: 13px; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
      .li .st { color: var(--msn-muted); font-size: 12px; text-align:right; white-space: nowrap; ${narrow ? "display:none;" : ""} }
      .li .dot { width: 9px; height: 9px; border-radius: 50%; flex: none; }
      .detail { background: var(--msn-tile-bg); border-radius: 16px; padding: 12px 14px; min-height: 0; display: flex; flex-direction: column; overflow: hidden; }
      .dh { display:flex; align-items:center; gap: 10px; font-size: 18px; flex: none; } .dh b { font-size: 19px; }
      .ds { border-top: 1px dashed var(--msn-muted-line); border-bottom: 1px solid var(--msn-muted-line); padding: 8px 0; margin: 8px 0 8px; flex: none;
            display:-webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow:hidden; font-size: 14px; }
      .lc { flex: 1 1 auto; min-height: 150px; width: 100%; height: 100%; display: block; }
      .tm { font-size: 12px; color: var(--msn-muted); margin-top: 6px; flex: none; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    </style>
    <ha-card>
      <div class="head">${esc(this._config.title || this.t(mode))}</div>
      <div class="wrap">
        <div class="list">${list}</div>
        <div class="detail">
          <div class="dh"><ha-icon icon="${sel[2]}"></ha-icon><span>${esc(this._lifeName(sel[0], s))}</span><b>${esc(s.state)}</b></div>
          <div class="ds">${esc(s.attributes.summary || "")}</div>
          ${chart}
          ${s.attributes.tomorrow ? `<div class="tm">${this.t("tomorrow")}: <b>${esc(s.attributes.tomorrow)}</b> – ${esc(s.attributes.tomorrow_summary || "")}</div>` : ""}
        </div>
      </div>
    </ha-card>`;
    this.shadowRoot.querySelectorAll(".li").forEach((el) => el.addEventListener("click", () => { this._sel = el.dataset.k; this._render(); }));
    this.shadowRoot.querySelector(".dh").addEventListener("click", () => this.more(this._sel));
  }

  /** Classic Home Assistant look: entity-row style list, flat detail, HTML bar chart. */
  _renderHa(mode, items, sel, s, levels, hourly, dot) {
    const tz = this._tz();
    const list = items.map(([k, , icon]) => {
      const st = this.st(k);
      return `<div class="lr ${k === this._sel ? "on" : ""}" data-k="${k}" style="--c:${dot(st.attributes.category)}">
        <span class="ic"><ha-icon icon="${icon}"></ha-icon></span>
        <span class="nm"><span class="n">${esc(this._lifeName(k, st))}</span><span class="v">${esc(st.state)}</span></span></div>`;
    }).join("");
    const cat = clamp(num(s.attributes.category) || 1, 1, 5);
    let prevDay = null;
    const bars = hourly.map((h, i) => {
      const raw = num(h.category) || 0, c = clamp(raw, 1, 5);  // 0 = not applicable at that hour
      const d = new Date(h.time);
      const day = d.toLocaleDateString("en-CA", { timeZone: tz || undefined });
      const split = prevDay && day !== prevDay;
      prevDay = day;
      const tick = i % 3 === 0 ? `<span class="tk">${timeStr(h.time, this._hass, tz)}</span>` : "";
      const mark = split ? `<span class="split"><em>${esc(d.toLocaleDateString(this._hass.language, { weekday: "short", timeZone: tz || undefined }))}</em></span>` : "";
      return `<div class="b" title="${esc(timeStr(h.time, this._hass, tz))} · ${esc(raw ? levels[c - 1] : "–")}">${mark}<i style="height:${raw ? c * 20 : 3}%;background:${raw ? dot(c) : "var(--divider-color, #8884)"}"></i>${tick}</div>`;
    }).join("");
    const legend = levels.map((lv, i) => `<span><i style="background:${dot(i + 1)}"></i>${esc(lv)}</span>`).join("");
    this.shadowRoot.innerHTML = `<style>${this._css()}
      :host { height: 100%; }
      ha-card { height: 100%; box-sizing: border-box; display: flex; flex-direction: column; overflow: hidden; padding: 16px; gap: 12px; }
      .head { margin: 0; }
      .rows { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 6px; flex: none; }
      .lr { display: flex; align-items: center; gap: 10px; padding: 6px 8px; border-radius: 10px; cursor: pointer; min-width: 0; }
      .lr:hover { background: rgba(var(--rgb-primary-text-color, 0, 0, 0), .04); }
      .lr.on { background: rgba(var(--rgb-primary-color, 3, 169, 244), .12); }
      .ic { width: 32px; height: 32px; border-radius: 50%; flex: none; display: flex; align-items: center; justify-content: center;
            background: color-mix(in srgb, var(--c) 18%, transparent); color: var(--c); }
      .ic ha-icon { --mdc-icon-size: 18px; }
      .nm { display: flex; flex-direction: column; min-width: 0; line-height: 1.25; }
      .n { font-size: 13px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
      .v { font-size: 12px; color: var(--secondary-text-color); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
      .det { border-top: 1px solid var(--divider-color, rgba(127,127,127,.25)); padding-top: 12px; flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; gap: 10px; }
      .dh { display: flex; align-items: center; gap: 12px; cursor: pointer; flex: none; }
      .dh .ic { width: 40px; height: 40px; } .dh .ic ha-icon { --mdc-icon-size: 22px; }
      .dh .n { font-size: 13px; font-weight: 400; color: var(--secondary-text-color); }
      .dh .v { font-size: 20px; font-weight: 500; color: var(--primary-text-color); line-height: 1.3; }
      .dh .nm { flex: 1; }
      .sum { font-size: 14px; line-height: 1.4; height: calc(3 * 1.4em); color: var(--primary-text-color); flex: none;
              display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
      .chart { flex: none; height: 76px; display: flex; align-items: flex-end; gap: 2px; padding: 14px 0 18px; position: relative; }
      .chart.nd { align-items: center; justify-content: center; }
      .b { flex: 1 1 0; height: 100%; position: relative; display: flex; align-items: flex-end; }
      .b i { display: block; width: 100%; border-radius: 3px 3px 1px 1px; min-height: 4px; opacity: .9; }
      .b:hover i { opacity: 1; filter: brightness(1.1); }
      .tk { position: absolute; top: 100%; left: 0; margin-top: 4px; font-size: 11px; color: var(--secondary-text-color); white-space: nowrap; }
      .split { position: absolute; left: -2px; top: -14px; bottom: 0; border-left: 1px dashed var(--secondary-text-color); opacity: .7; }
      .split em { position: absolute; top: -1px; left: 4px; font-style: normal; font-size: 11px; white-space: nowrap; }
      .lg { display: flex; flex-wrap: wrap; align-content: flex-start; gap: 4px 12px; font-size: 11px; line-height: 15px; height: 34px; overflow: hidden; color: var(--secondary-text-color); flex: none; }
      .lg span { display: inline-flex; align-items: center; gap: 5px; } .lg i { width: 8px; height: 8px; border-radius: 2px; display: inline-block; }
      .tm { font-size: 13px; line-height: 1.4; height: calc(2 * 1.4em); color: var(--secondary-text-color); flex: none; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
      .tm b { color: var(--primary-text-color); font-weight: 500; }
    </style>
    <ha-card>
      <div class="head">${esc(this._config.title || this.t(mode))}</div>
      <div class="rows">${list}</div>
      <div class="det">
        <div class="dh" style="--c:${dot(cat)}"><span class="ic"><ha-icon icon="${sel[2]}"></ha-icon></span>
          <span class="nm"><span class="n">${esc(this._lifeName(sel[0], s))}</span><span class="v">${esc(s.state)}</span></span></div>
        <div class="sum">${esc(s.attributes.summary || "")}</div>
        ${hourly.length ? `<div class="chart">${bars}</div>` : `<div class="chart nd"><div class="lbl">${this.t("noData")}</div></div>`}<div class="lg">${legend}</div>
        <div class="tm">${s.attributes.tomorrow ? `${this.t("tomorrow")}: <b>${esc(s.attributes.tomorrow)}</b> – ${esc(s.attributes.tomorrow_summary || "")}` : ""}</div>
      </div>
    </ha-card>`;
    this.shadowRoot.querySelectorAll(".lr").forEach((el) => el.addEventListener("click", () => { this._sel = el.dataset.k; this._render(); }));
    this.shadowRoot.querySelector(".dh").addEventListener("click", () => this.more(this._sel));
  }

}

/* ----------------------------------------------------------------------- */
/* Hourly card – day strip + responsive chart                               */
/* ----------------------------------------------------------------------- */
const HOURLY_TABS = {
  overview: { field: "temperature", second: "apparent_temperature", unit: "°", color: "#f59e0b", area: true, day: ["temp_high", "temp_low", "°"] },
  feels: { field: "apparent_temperature", second: "temperature", unit: "°", color: "#fb923c", area: true, day: ["feels_high", "feels_low", "°"] },
  precipitation: { field: "precipitation", unit: "precip", color: "#3b82f6", bars: true, day: ["precip_total", "precip_probability", "precip", "%"] },
  wind: { field: "wind_speed", second: "wind_gust_speed", unit: "wind", color: "#60a5fa", area: true, day: ["wind_high", "wind_low", "wind"], arrows: true },
  humidity: { field: "humidity", second: "dew_point", unit: "%", color: "#38bdf8", area: true, day: ["humidity_high", "humidity_low", "%"] },
  cloudcover: { field: "cloud_coverage", unit: "%", color: "#3b6fd8", bars: true, day: ["cloud_day", "cloud_night", "%"] },
  pressure: { field: "pressure", unit: "pressure", color: "#a78bfa", area: true, day: ["pressure_high", "pressure_low", ""], dec: "pressure" },
  uv: { field: "uv_index", unit: "", color: "#f6a821", bars: true, day: ["uv_max", null, ""] },
  visibility: { field: "visibility", unit: "vis", color: "#4caf7d", area: true, day: ["visibility_high", "visibility_low", "vis"] },
  aqi: { field: "aqi", unit: "", color: "#e0a106", bars: true, day: ["aqi", null, ""], aqiColors: true },
};
const TAB_LABEL = {
  de: { overview: "Übersicht", feels: "Gefühlt", precipitation: "Niederschlag", wind: "Wind", humidity: "Luftfeuchtigkeit", cloudcover: "Bewölkt", pressure: "Druck", uv: "UV", visibility: "Sichtbarkeit", aqi: "Luftqualität" },
  en: { overview: "Overview", feels: "Feels like", precipitation: "Precipitation", wind: "Wind", humidity: "Humidity", cloudcover: "Clouds", pressure: "Pressure", uv: "UV", visibility: "Visibility", aqi: "Air quality" },
  it: { overview: "Panoramica", feels: "Percepita", precipitation: "Precipitazioni", wind: "Vento", humidity: "Umidità", cloudcover: "Nuvole", pressure: "Pressione", uv: "UV", visibility: "Visibilità", aqi: "Qualità dell'aria" },
  fr: { overview: "Aperçu", feels: "Ressenti", precipitation: "Précipitations", wind: "Vent", humidity: "Humidité", cloudcover: "Nuages", pressure: "Pression", uv: "UV", visibility: "Visibilité", aqi: "Qualité de l'air" },
  es: { overview: "Resumen", feels: "Sensación", precipitation: "Precipitación", wind: "Viento", humidity: "Humedad", cloudcover: "Nubes", pressure: "Presión", uv: "UV", visibility: "Visibilidad", aqi: "Calidad del aire" },
  nl: { overview: "Overzicht", feels: "Gevoel", precipitation: "Neerslag", wind: "Wind", humidity: "Vochtigheid", cloudcover: "Wolken", pressure: "Luchtdruk", uv: "UV", visibility: "Zicht", aqi: "Luchtkwaliteit" },
};
const SERIES_LABEL = {
  de: { temperature: "Temperatur", apparent_temperature: "Gefühlt", precipitation: "Niederschlag (mm)", wind_speed: "Wind", wind_gust_speed: "Windböen", humidity: "Luftfeuchtigkeit", dew_point: "Taupunkt (°)", cloud_coverage: "Bewölkung", pressure: "Luftdruck", uv_index: "UV-Index", visibility: "Sichtweite", aqi: "AQI" },
  en: { temperature: "Temperature", apparent_temperature: "Feels like", precipitation: "Precipitation (mm)", wind_speed: "Wind", wind_gust_speed: "Gusts", humidity: "Humidity", dew_point: "Dew point (°)", cloud_coverage: "Clouds", pressure: "Pressure", uv_index: "UV index", visibility: "Visibility", aqi: "AQI" },
  it: { temperature: "Temperatura", apparent_temperature: "Percepita", precipitation: "Precipitazioni (mm)", wind_speed: "Vento", wind_gust_speed: "Raffiche", humidity: "Umidità", dew_point: "Punto di rugiada (°)", cloud_coverage: "Nuvolosità", pressure: "Pressione", uv_index: "Indice UV", visibility: "Visibilità", aqi: "AQI" },
  fr: { temperature: "Température", apparent_temperature: "Ressenti", precipitation: "Précipitations (mm)", wind_speed: "Vent", wind_gust_speed: "Rafales", humidity: "Humidité", dew_point: "Point de rosée (°)", cloud_coverage: "Nébulosité", pressure: "Pression", uv_index: "Indice UV", visibility: "Visibilité", aqi: "IQA" },
  es: { temperature: "Temperatura", apparent_temperature: "Sensación", precipitation: "Precipitación (mm)", wind_speed: "Viento", wind_gust_speed: "Rachas", humidity: "Humedad", dew_point: "Punto de rocío (°)", cloud_coverage: "Nubosidad", pressure: "Presión", uv_index: "Índice UV", visibility: "Visibilidad", aqi: "ICA" },
  nl: { temperature: "Temperatuur", apparent_temperature: "Gevoel", precipitation: "Neerslag (mm)", wind_speed: "Wind", wind_gust_speed: "Windstoten", humidity: "Vochtigheid", dew_point: "Dauwpunt (°)", cloud_coverage: "Bewolking", pressure: "Luchtdruk", uv_index: "UV-index", visibility: "Zicht", aqi: "LKI" },
};
const dayKey = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;

class MsnWeatherHourlyCard extends MsnBase {
  static getStubConfig(hass) { return MsnWeatherDetailsCard.getStubConfig(hass); }
  static getConfigForm() {
    return {
      schema: [
        { name: "entity", required: true, selector: { entity: { domain: "weather", integration: "msn_weather" } } },
        { name: "title", selector: { text: {} } },
        { name: "hours", selector: { number: { min: 6, max: 48, step: 1, mode: "box" } } },
        { name: "show_days", selector: { boolean: {} } },
        { name: "show_chart", selector: { boolean: {} } },
        { name: "tabs", selector: { select: { multiple: true, reorder: true, options: Object.keys(HOURLY_TABS).map((k) => ({ value: k, label: (UI_DE ? TAB_LABEL.de : TAB_LABEL.en)[k] })) } } },
      ],
    };
  }
  get _responsive() { return true; }
  getCardSize() { return 8; }
  getGridOptions() { return { columns: "full", rows: "auto", min_columns: 6 }; }

  _days() {
    const days = this.attr("daily_details", "days") || [];
    const today = this._locDayKey(0);
    return days.filter((d) => d.date >= this._locDayKey(-1)).slice(0, 10).map((d) => ({ ...d, isToday: d.date === today }));
  }
  /** Date key of a forecast entry at the weather location. */
  _fcDay(f) { return String(f.datetime).slice(0, 10); }

  _render() {
    if (!this._hass) return;
    const L = lang(this._hass);
    const tabs = this._config.tabs || Object.keys(HOURLY_TABS);
    if (!this._tab || !tabs.includes(this._tab)) this._tab = tabs[0];
    const cfg = HOURLY_TABS[this._tab];
    const hours = this._config.hours || 24;
    const all = this._forecast || [];
    const today = this._locDayKey(0);
    if (!this._day) this._day = today;
    const avail = Math.max(260, this._width - 34);
    const maxCols = Math.max(6, Math.floor(avail / 26));
    let fc = this._day === today ? all.slice(0, Math.min(hours, maxCols)) : all.filter((f) => this._fcDay(f) === this._day).slice(0, Math.min(24, maxCols));
    const nDays = clamp(Math.floor((avail + 10) / 104), 3, 10);

    // ---- day strip
    const days = this._config.show_days === false ? [] : this._days().slice(0, nDays);
    const dayHtml = days.map((d) => {
      const dt = new Date(d.date + "T12:00:00");
      const lbl = d.isToday ? this.t("today") : d.date < today ? (pick(L, { de: "Gestern", en: "Yesterday", it: "Ieri", fr: "Hier", es: "Ayer", nl: "Gisteren" })) : dt.toLocaleDateString(this._hass.language, { weekday: "short" });
      const [k1, k2, k1u, k2u] = cfg.day;
      const isKind = (u) => ["precip", "wind", "vis", "pressure", "temp"].includes(u);
      const u1 = isKind(k1u) ? " " + this._unit(k1u) : k1u, u2 = isKind(k2u) ? " " + this._unit(k2u) : k2u;
      const v1 = num(d[k1]), v2 = k2 ? num(d[k2]) : null;
      const fmt1 = (v) => (v === null ? "–" : fmt(v, isKind(k1u) ? this._dec(k1u) : cfg.dec ? this._dec(cfg.dec) : 0));
      const scale = this._tab === "uv" ? 11 : this._tab === "aqi" ? 300 : this._tab === "precipitation" ? (this._unit("precip") === "in" ? 0.4 : 10) : null;
      const pct = scale && v1 !== null ? clamp(v1 / scale, 0.05, 1) : null;
      const has = d.date >= today;
      return `<div class="day ${d.date === this._day ? "on" : ""} ${has ? "" : "past"}" data-d="${d.date}">
        <div class="dh"><b>${dt.getDate()}</b><span>${esc(lbl)}</span></div>
        <div class="dv"><div><span class="v1">${fmt1(v1)}</span><span class="u">${esc((u2 === undefined ? u1 : u1) || "")}</span></div>
          ${k2 ? `<div class="v2">${v2 === null ? "–" : fmt(v2, 0)}${esc(u2 !== undefined ? u2 : u1 || "")}</div>` : ""}</div>
        ${pct !== null ? `<div class="gauge"><i style="height:${pct * 100}%;background:${this._tab === "aqi" ? aqiColor(v1) : cfg.color}"></i></div>` : ""}
      </div>`;
    }).join("");

    // ---- chart
    const n = Math.max(fc.length, 1);
    const vals = fc.map((f) => num(f[cfg.field]));
    const sec = cfg.second ? fc.map((f) => num(f[cfg.second])) : [];
    const pool = [...vals, ...sec].filter((v) => v !== null);
    let mn = pool.length ? Math.min(...pool) : 0, mx = pool.length ? Math.max(...pool) : 1;
    if (cfg.bars) mn = 0;
    const minRange = this._unit("precip") === "in" && cfg.unit === "precip" ? 0.04 : this._unit("pressure") === "inHg" && cfg.unit === "pressure" ? 0.1 : 1;
    if (mx - mn < minRange) mx = mn + minRange;
    const VW = n * 100, VH = 200;
    const xs = (i) => (i + 0.5) * 100;
    const ys = (v) => VH - 8 - ((v - mn) / (mx - mn)) * (VH - 24);
    const gid = "hg" + Math.random().toString(36).slice(2, 7);
    let svg = `<defs><linearGradient id="${gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${cfg.color}" stop-opacity="0.55"/><stop offset="1" stop-color="${cfg.color}" stop-opacity="0.04"/></linearGradient></defs>`;
    if (cfg.bars) {
      vals.forEach((v, i) => {
        if (v === null) return;
        const y = ys(Math.max(v, 0));
        svg += `<rect x="${xs(i) - 28}" y="${y}" width="56" height="${Math.max(VH - y, 2)}" rx="10" fill="${cfg.aqiColors ? aqiColor(v) : cfg.color}"/>`;
      });
    } else {
      const pts = vals.map((v, i) => (v === null ? null : [xs(i), ys(v)])).filter(Boolean);
      if (pts.length > 1) {
        const pth = smoothPath(pts);
        if (cfg.area) svg += `<path d="${pth} L${pts[pts.length - 1][0]},${VH} L${pts[0][0]},${VH} Z" fill="url(#${gid})"/>`;
        svg += `<path d="${pth}" stroke="${cfg.color}" stroke-width="2.5" fill="none" vector-effect="non-scaling-stroke"/>`;
      }
    }
    if (cfg.second) {
      const pts = sec.map((v, i) => (v === null ? null : [xs(i), ys(v)])).filter(Boolean);
      if (pts.length > 1) svg += `<path d="${smoothPath(pts)}" stroke="var(--secondary-text-color)" stroke-width="2" fill="none" vector-effect="non-scaling-stroke" ${this._tab === "humidity" ? 'stroke-dasharray="5 4"' : ""}/>`;
    }
    // midnight separators
    fc.forEach((f, i) => {
      if (i > 0 && String(f.datetime).slice(11, 13) === "00") svg += `<line x1="${i * 100}" x2="${i * 100}" y1="0" y2="${VH}" stroke="var(--msn-muted-line)" stroke-dasharray="4 4" vector-effect="non-scaling-stroke"/>`;
    });
    const colW = avail / n;
    const step = colW >= 50 ? 1 : colW >= 25 ? 2 : 3;
    const cols = fc.map((f, i) => {
      const d = new Date(f.datetime);
      const show = i % step === 0;
      const v = vals[i];
      const isMid = i > 0 && String(f.datetime).slice(11, 13) === "00";
      const locDay = new Date(String(f.datetime).slice(0, 10) + "T12:00:00");
      return `<div class="col">${isMid ? `<span class="mid">${locDay.toLocaleDateString(this._hass.language, { weekday: "short", day: "numeric" })}</span>` : ""}
        ${show ? `<span class="tm">${i === 0 && this._day === today ? (pick(L, { de: "Jetzt", en: "Now", it: "Ora", fr: "Maintenant", es: "Ahora", nl: "Nu" })) : String(f.datetime).slice(11, 16)}</span>
        <ha-icon icon="${COND_ICON[f.condition] || "mdi:weather-cloudy"}" style="color:${COND_COLOR[f.condition] || "#aaa"}"></ha-icon>
        <span class="val">${v === null ? "" : fmt(v, ["precip", "pressure"].includes(cfg.unit) ? this._dec(cfg.unit) : 0) + (cfg.unit === "°" ? "°" : cfg.unit === "%" ? "%" : "")}</span>
        ${cfg.arrows && num(f.wind_bearing) !== null ? `<span class="arr" style="transform:rotate(${(num(f.wind_bearing) + 180) % 360}deg)">➤</span>` : ""}` : ""}
      </div>`;
    }).join("");
    const probs = fc.map((f, i) => `<div class="pc">${i % step === 0 ? `<ha-icon icon="mdi:water"></ha-icon>${num(f.precipitation_probability) === null ? "–" : fmt(f.precipitation_probability)}%` : ""}</div>`).join("");
    const legendMain = ((SERIES_LABEL[L] || SERIES_LABEL.en)[cfg.field] || "").replace("(mm)", `(${this._unit("precip")})`);
    const legend2 = cfg.second ? (SERIES_LABEL[L] || SERIES_LABEL.en)[cfg.second] : null;

    this.shadowRoot.innerHTML = `<style>${this._css()}
      .tabs { display:flex; gap: 6px; flex-wrap: nowrap; overflow-x: auto; scrollbar-width: none; margin: 0 -2px 12px; padding: 0 2px; }
      .tabs::-webkit-scrollbar { display: none; }
      .tab { padding: 5px 12px; border-radius: 999px; background: var(--msn-tile-bg); cursor: pointer; font-size: 13px; user-select:none; white-space: nowrap; flex: none; }
      .tab.on { background: #fcd34d; color: #111; font-weight: 600; }
      :host { height: 100%; }
      ha-card { height: 100%; box-sizing: border-box; display: flex; flex-direction: column; overflow: hidden; }
      .days { display:grid; grid-template-columns: repeat(${Math.max(days.length, 1)}, minmax(0, 1fr)); gap: 8px; margin-bottom: 10px; flex: none; }
      .day { background: var(--msn-tile-bg); border-radius: 14px; padding: 8px 10px; cursor:pointer; position:relative; border: 2px solid transparent; min-height: 74px; min-width: 0; overflow: hidden; }
      .day.on { border-color: var(--primary-color); background: var(--ha-card-background, var(--card-background-color)); box-shadow: 0 1px 6px rgba(0,0,0,.12); }
      .day.past { opacity: .75; cursor: default; }
      .day .dh { display:flex; justify-content:space-between; gap: 6px; font-size: 13px; color: var(--msn-muted); min-width: 0; }
      .day .dh span { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
      .day .dh b { color: var(--primary-text-color); font-size: 15px; }
      .day .dv { margin-top: 6px; padding-right: 18px; white-space: nowrap; } .day .v1 { font-size: 22px; font-weight: 700; } .day .u { font-size: 12px; margin-left: 2px; }
      .day .v2 { font-size: 16px; color: var(--msn-muted); }
      .day .gauge { position:absolute; right: 10px; bottom: 12px; top: 34px; width: 10px; border-radius: 6px; background: var(--msn-muted-line); overflow:hidden; display:flex; align-items:flex-end; }
      .day .gauge i { display:block; width: 100%; border-radius: 6px; }
      .tabs { flex: none; } .head { flex: none; }
      .scroll { flex: 1 1 auto; min-height: 230px; display: flex; flex-direction: column; overflow: hidden; }
      .inner { flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; }
      .cols, .probs { display:grid; grid-template-columns: repeat(${n}, 1fr); }
      .cols { flex: none; } .probs { flex: none; }
      .col { display:flex; flex-direction:column; align-items:center; gap: 3px; position:relative; min-height: 70px; font-size: 12px; min-width: 0; }
      .col .tm { color: var(--msn-muted); white-space:nowrap; } .col .val { font-size: 14px; font-weight: 600; }
      .col ha-icon { --mdc-icon-size: 22px; } .col .arr { font-size: 11px; color: var(--msn-muted); display:inline-block; }
      .col .mid { position:absolute; top: -14px; left: -2px; font-size: 11px; color: var(--msn-muted); white-space:nowrap; }
      .chart { flex: 1 1 150px; min-height: 110px; border-top: 1px solid var(--msn-muted-line); padding-top: 4px; }
      .chart svg { width:100%; height:100%; display:block; }
      .pc { text-align:center; font-size: 12px; color: #3b82f6; white-space:nowrap; } .pc ha-icon { --mdc-icon-size: 13px; }
      .leg { display:flex; gap: 18px; font-size: 13px; color: var(--msn-muted); margin-top: 8px; flex: none; }
      .leg i { display:inline-block; width: 14px; height: 4px; border-radius: 2px; vertical-align: middle; margin-right: 6px; }
      .empty { padding: 40px 0; text-align:center; color: var(--msn-muted); }
    </style>
    <ha-card>
      <div class="head">${esc(this._config.title || (tabs.length === 1 && this._tab !== "overview" ? (TAB_LABEL[L] || TAB_LABEL.en)[this._tab] : this.t("hourly")))}</div>
      ${tabs.length > 1 ? `<div class="tabs">${tabs.map((k) => `<div class="tab ${k === this._tab ? "on" : ""}" data-k="${k}">${esc((TAB_LABEL[L] || TAB_LABEL.en)[k] || k)}</div>`).join("")}</div>` : ""}
      ${dayHtml ? `<div class="days">${dayHtml}</div>` : ""}
      ${this._config.show_chart === false ? "" : fc.length ? `<div class="scroll"><div class="inner">
        <div class="cols" style="margin-top:16px">${cols}</div>
        <div class="chart"><svg viewBox="0 0 ${VW} ${VH}" preserveAspectRatio="none">${svg}</svg></div>
        <div class="probs">${probs}</div>
      </div></div>` : `<div class="empty">${this._forecast === null ? (pick(L, { de: "Lade Vorhersage …", en: "Loading forecast …", it: "Caricamento previsioni …", fr: "Chargement des prévisions …", es: "Cargando previsión …", nl: "Verwachting laden …" })) : this.t("noData")}</div>`}
      ${this._config.show_chart === false ? "" : `<div class="leg"><span><i style="background:${cfg.color}"></i>${esc(legendMain || "")}</span>${legend2 ? `<span><i style="background:var(--secondary-text-color)"></i>${esc(legend2)}</span>` : ""}</div>`}
    </ha-card>`;
    this.shadowRoot.querySelectorAll(".tab").forEach((el) => el.addEventListener("click", () => { this._tab = el.dataset.k; this._render(); }));
    this.shadowRoot.querySelectorAll(".day:not(.past)").forEach((el) => el.addEventListener("click", () => { this._day = el.dataset.d; this._render(); }));
  }
}

/* ----------------------------------------------------------------------- */
/* Nowcast card – precipitation of the next 2 hours, minute by minute       */
/* ----------------------------------------------------------------------- */
// rain rate thresholds (mm/h) of the light / moderate / heavy bands
const NOWCAST_BANDS = [2.5, 7.6];

class MsnWeatherNowcastCard extends MsnBase {
  static getStubConfig(hass) { return MsnWeatherDetailsCard.getStubConfig(hass); }
  static getConfigForm() {
    return {
      schema: [
        { name: "entity", required: true, selector: { entity: { domain: "weather", integration: "msn_weather" } } },
        { name: "title", selector: { text: {} } },
      ],
    };
  }
  get _responsive() { return true; }
  getCardSize() { return 4; }
  getGridOptions() { return { columns: "full", rows: "auto", min_columns: 6 }; }
  _needsForecast() { return false; }
  _signature() {
    const st = this.st("nowcast");
    return (st ? st.state + st.attributes.timestamp : "") + this._w + this._config.appearance;
  }

  _render() {
    if (!this._hass) return;
    const de = lang(this._hass) === "de";
    const lc = lang(this._hass);
    const st = this.st("nowcast");
    const title = this._config.title || (pick(lc, { de: "Niederschlag in den nächsten 2 Std.", en: "Precipitation in the next 2 hours", it: "Precipitazioni nelle prossime 2 ore", fr: "Précipitations dans les 2 prochaines heures", es: "Precipitación en las próximas 2 horas", nl: "Neerslag in de komende 2 uur" }));
    if (!st) {
      this.shadowRoot.innerHTML = `<style>${this._css()}</style><ha-card><div class="head">${esc(title)}</div><div class="lbl">${this.t("noData")}</div></ha-card>`;
      return;
    }
    const a = st.attributes;
    const step = num(a.minutes_between_values) || 4;
    // like msn.com: the next 2 hours (MSN delivers a little more)
    const rates = (a.precipitation_rate || a.precipitation || []).slice(0, Math.floor(120 / step) + 1).map((v) => Math.max(0, num(v) || 0));
    const imperial = this._unit("precip") === "in";
    const toMm = (v) => (imperial ? v * 25.4 : v);
    const start = a.timestamp ? new Date(a.timestamp) : new Date();
    const tz = this._tz();
    const at = (i) => new Date(start.getTime() + i * step * 60000);
    const clock = (d) => timeStr(d.toISOString(), this._hass, tz);
    const snow = a.precipitation_type === "sn" || a.precipitation_type === "s";
    const colour = (mm) => (snow ? (mm < NOWCAST_BANDS[0] ? "#7dd3fc" : mm < NOWCAST_BANDS[1] ? "#38bdf8" : "#0284c7")
      : (mm < NOWCAST_BANDS[0] ? "#60a5fa" : mm < NOWCAST_BANDS[1] ? "#2563eb" : "#1e3a8a"));
    // bar height: light band up to 1/3, moderate up to 2/3, heavy above
    const height = (mm) => {
      if (mm <= 0) return 0;
      if (mm < NOWCAST_BANDS[0]) return 4 + (mm / NOWCAST_BANDS[0]) * 29;
      if (mm < NOWCAST_BANDS[1]) return 33 + ((mm - NOWCAST_BANDS[0]) / (NOWCAST_BANDS[1] - NOWCAST_BANDS[0])) * 33;
      return Math.min(100, 66 + ((mm - NOWCAST_BANDS[1]) / 20) * 34);
    };
    // when does it start / stop? (first change from dry to wet and back)
    const wet = rates.map((v) => toMm(v) > 0.05);
    const events = [];
    for (let i = 1; i < wet.length; i++) {
      if (wet[i] !== wet[i - 1]) events.push({ i, start: wet[i] });
    }
    const label = (e) => `${e.start ? (pick(lc, { de: "Beginn", en: "Starts", it: "Inizio", fr: "Début", es: "Inicio", nl: "Begin" })) : (pick(lc, { de: "Ende", en: "Stops", it: "Fine", fr: "Fin", es: "Fin", nl: "Einde" }))} ${clock(at(e.i))}`;
    const bars = rates.map((v, i) => {
      const mm = toMm(v);
      return `<div class="b" title="${esc(clock(at(i)))} · ${fmt(v, imperial ? 2 : 1)} ${esc(this._unit("precip"))}/h"><i style="height:${height(mm)}%;background:${colour(mm)}"></i></div>`;
    }).join("");
    const n = Math.max(rates.length, 1);
    const ticks = [0, 30, 60, 90, 120].filter((m) => m / step < n).map((m) => {
      const x = (m / step / n) * 100;
      return `<span class="tk" style="left:${x}%">${m === 0 ? (pick(lc, { de: "Jetzt", en: "Now", it: "Ora", fr: "Maintenant", es: "Ahora", nl: "Nu" })) : clock(at(m / step))}</span>`;
    }).join("");
    const marks = events.slice(0, 3).map((e) =>
      `<span class="ev ${e.start ? "on" : "off"}" style="left:${(e.i / n) * 100}%"><em>${esc(label(e))}</em></span>`).join("");
    const dry = !wet.some(Boolean);
    const icon = dry ? "mdi:weather-partly-cloudy" : snow ? "mdi:weather-snowy" : "mdi:weather-rainy";
    const bands = pick(lc, { de: ["leicht", "mäßig", "stark"], en: ["light", "moderate", "heavy"], it: ["debole", "moderata", "forte"],
      fr: ["faible", "modérée", "forte"], es: ["débil", "moderada", "fuerte"], nl: ["licht", "matig", "zwaar"] });

    this.shadowRoot.innerHTML = `<style>${this._css()}
      ha-card { display: flex; flex-direction: column; gap: 10px; }
      .head { margin-bottom: 0; }
      .sum { display: flex; align-items: center; gap: 10px; font-size: 15px; cursor: pointer; }
      .sum ha-icon { --mdc-icon-size: 26px; color: ${dry ? "var(--secondary-text-color)" : "#2563eb"}; flex: none; }
      .sum b { font-weight: 600; }
      .plot { position: relative; height: 120px; margin: 18px 0 20px; }
      .grid { position: absolute; inset: 0; display: flex; flex-direction: column-reverse; pointer-events: none; }
      .grid div { flex: 1; border-top: 1px dashed var(--msn-muted-line); position: relative; }
      .grid span { position: absolute; right: 2px; top: 1px; font-size: 10px; color: var(--secondary-text-color); z-index: 1;
                   background: color-mix(in srgb, var(--ha-card-background, var(--card-background-color, #fff)) 75%, transparent); padding: 0 3px; border-radius: 3px; }
      .bars { position: absolute; inset: 0; display: flex; align-items: flex-end; gap: 1px; }
      .b { flex: 1 1 0; height: 100%; display: flex; align-items: flex-end; }
      .b i { display: block; width: 100%; border-radius: 2px 2px 0 0; }
      .tk { position: absolute; top: 100%; margin-top: 4px; font-size: 11px; color: var(--secondary-text-color); transform: translateX(-50%); white-space: nowrap; }
      .tk:first-child { transform: none; }
      .ev { position: absolute; top: -16px; bottom: 0; border-left: 2px solid; }
      .ev.on { border-color: #2563eb; } .ev.off { border-color: var(--secondary-text-color); }
      .ev em { position: absolute; top: -2px; left: 4px; font-style: normal; font-size: 11px; font-weight: 600; white-space: nowrap; }
      .ev.off em { left: auto; right: 4px; }
      .dry { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-size: 13px; color: var(--secondary-text-color); }
      ${this._ha ? ".plot { background: none; } .sum b { font-weight: 500; }" : ".plot { background: var(--msn-tile-bg); border-radius: 12px; }"}
    </style>
    <ha-card>
      <div class="head">${esc(title)}</div>
      <div class="sum"><ha-icon icon="${icon}"></ha-icon><b>${esc(st.state || "")}</b></div>
      <div class="plot">
        <div class="grid"><div><span>${bands[0]}</span></div><div><span>${bands[1]}</span></div><div><span>${bands[2]}</span></div></div>
        <div class="bars">${bars}</div>
        ${dry ? `<div class="dry">${pick(lc, { de: "Kein Niederschlag erwartet", en: "No precipitation expected", it: "Nessuna precipitazione prevista", fr: "Aucune précipitation prévue", es: "No se esperan precipitaciones", nl: "Geen neerslag verwacht" })}</div>` : ""}
        ${marks}
        ${ticks}
      </div>
    </ha-card>`;
    this.shadowRoot.querySelector(".sum").addEventListener("click", () => this.more("nowcast"));
  }
}

/* ----------------------------------------------------------------------- */
/* Alerts card – active and upcoming severe weather warnings                 */
/* ----------------------------------------------------------------------- */
// MSN maps every national service to R / O / Y / B (red / orange / yellow / blue), e.g. NWS warning / watch /
// advisory / statement, Meteoalarm red / orange / yellow, JMA warning / advisory. W / A / S are kept as fallbacks.
const ALERT_RANK = { R: 0, W: 0, O: 1, A: 1, Y: 2, B: 3, S: 3 };
const ALERT_COLOURS = ["#d32f2f", "#f57c00", "#f9a825", "#1976d2"];
const alertRank = (a) => {
  const sig = ALERT_RANK[a.significance];
  if (sig !== undefined) return sig;
  const lv = (a.level || "").toLowerCase();
  return /red|warning|rot|rosso|rouge|rojo/.test(lv) ? 0 : /orange|watch|arancione/.test(lv) ? 1 : /statement|information|blue|blau/.test(lv) ? 3 : 2;
};
const alertColour = (a) => ALERT_COLOURS[alertRank(a)];
const ALERT_ICONS = [
  [/thunder|gewitter|lightning|temporal|orage/i, "mdi:weather-lightning"],
  [/snow|schnee|ice|eis|glätte|neve|neige|nieve|winter/i, "mdi:snowflake-alert"],
  [/rain|regen|pioggia|pluie|lluvia|precip/i, "mdi:weather-pouring"],
  [/flood|hochwasser|überschwemm|alluvion|inond/i, "mdi:home-flood"],
  [/wind|sturm|storm|gale|orkan|vento|vent|viento|hurricane|tropical/i, "mdi:weather-windy"],
  [/heat|hitze|caldo|chaleur|calor/i, "mdi:thermometer-alert"],
  [/frost|cold|kälte|freddo|froid|frío/i, "mdi:snowflake-thermometer"],
  [/fog|nebel|nebbia|brouillard|niebla/i, "mdi:weather-fog"],
  [/fire|brand|incend|feu/i, "mdi:fire-alert"],
  [/avalanche|lawine|valanga|alud/i, "mdi:landslide"],
  [/craft|boot|marine|surf|coastal|küste|wave|welle/i, "mdi:sail-boat"],
  [/air|luft|smog|ozone/i, "mdi:smog"],
];
const alertIcon = (a) => (ALERT_ICONS.find(([re]) => re.test(`${a.event || ""} ${a.title || ""}`)) || [null, "mdi:alert"])[1];

class MsnWeatherAlertsCard extends MsnBase {
  static getStubConfig(hass) { return MsnWeatherDetailsCard.getStubConfig(hass); }
  static getConfigForm() {
    return {
      schema: [
        { name: "entity", required: true, selector: { entity: { domain: "weather", integration: "msn_weather" } } },
        { name: "title", selector: { text: {} } },
        { name: "hide_when_empty", selector: { boolean: {} } },
      ],
    };
  }
  getCardSize() { return 2; }
  getGridOptions() { return { columns: 12, rows: "auto", min_columns: 4, min_rows: 1 }; }
  get _responsive() { return true; }
  _needsForecast() { return false; }
  _signature() {
    const st = this.st("alerts");
    return (st ? st.state + JSON.stringify(st.attributes.alerts || []) : "") + (this._open || "") + this._config.appearance + Math.floor(Date.now() / 300000);
  }

  /** Show as many alerts as fit into the card height (most severe first), "+n more" for the rest. */
  _fit(lc) {
    const list = this.shadowRoot.querySelector(".list"), more = this.shadowRoot.querySelector(".more");
    if (!list || !more) return;
    const items = [...list.querySelectorAll(".al")];
    items.forEach((el) => { el.style.display = ""; });
    more.hidden = true;
    if (list.scrollHeight <= list.clientHeight + 1) return;
    more.hidden = false;
    let hidden = 0;
    for (let i = items.length - 1; i > 0 && list.scrollHeight > list.clientHeight + 1; i--) {
      items[i].style.display = "none";
      hidden++;
      more.textContent = pick(lc, { de: `+${hidden} weitere`, en: `+${hidden} more`, it: `+${hidden} altre`, fr: `+${hidden} autres`, es: `+${hidden} más`, nl: `+${hidden} meer` });
    }
    if (!hidden) more.hidden = true;
  }

  _render() {
    if (!this._hass) return;
    const de = lang(this._hass) === "de";
    const lc = lang(this._hass);
    const alerts = (this.attr("alerts", "alerts") || []).slice()
      .sort((x, y) => alertRank(x) - alertRank(y) || String(x.start).localeCompare(String(y.start)));
    const title = this._config.title || (pick(lc, { de: "Wetterwarnungen", en: "Weather alerts", it: "Allerte meteo", fr: "Alertes météo", es: "Avisos meteorológicos", nl: "Weerwaarschuwingen" }));
    if (!alerts.length && this._config.hide_when_empty) {
      this.shadowRoot.innerHTML = "";
      this.style.display = "none";
      return;
    }
    this.style.display = "";
    const tz = this._tz();
    const clock = (d) => timeStr(d.toISOString(), this._hass, tz);
    const dayKeyTz = (d) => d.toLocaleDateString("en-CA", { timeZone: tz || undefined });
    const todayKey = dayKeyTz(new Date()), tomorrowKey = dayKeyTz(new Date(Date.now() + 86400000));
    // "today" / "tomorrow" / weekday name
    const dayName = (d) => {
      const k = dayKeyTz(d);
      if (k === todayKey) return pick(lc, { de: "heute", en: "today", it: "oggi", fr: "aujourd'hui", es: "hoy", nl: "vandaag" });
      if (k === tomorrowKey) return pick(lc, { de: "morgen", en: "tomorrow", it: "domani", fr: "demain", es: "mañana", nl: "morgen" });
      return d.toLocaleDateString(this._hass.language, { weekday: "long", timeZone: tz || undefined });
    };
    const span = (ms) => {
      const h = Math.floor(ms / 3600000);
      if (h < 1) { const m = Math.max(1, Math.round(ms / 60000)); return pick(lc, { de: `${m} Min.`, en: `${m} min`, it: `${m} min`, fr: `${m} min`, es: `${m} min`, nl: `${m} min` }); }
      return pick(lc, { de: `${h} Std.`, en: `${h} h`, it: `${h} h`, fr: `${h} h`, es: `${h} h`, nl: `${h} u` });
    };
    // e.g. "beginnt Dienstag um 20:00 · bis Mittwoch 01:59", "beginnt in 3 Std. · bis 23:59", "aktiv bis morgen 01:59"
    const timing = (a) => {
      const now = Date.now();
      const s = a.start ? new Date(a.start) : null, e = a.end ? new Date(a.end) : null;
      const until = (ref) => {
        if (!e) return "";
        const sameDay = dayKeyTz(e) === dayKeyTz(ref);
        return sameDay ? clock(e) : `${dayName(e)} ${clock(e)}`;
      };
      if (s && s.getTime() > now) {
        const soon = s.getTime() - now < 6 * 3600000 || dayKeyTz(s) === todayKey;
        const begin = soon
          ? (pick(lc, { de: `beginnt in ${span(s.getTime() - now)}`, en: `starts in ${span(s.getTime() - now)}`, it: `inizia tra ${span(s.getTime() - now)}`, fr: `commence dans ${span(s.getTime() - now)}`, es: `empieza en ${span(s.getTime() - now)}`, nl: `begint over ${span(s.getTime() - now)}` }))
          : (pick(lc, { de: `beginnt ${dayName(s)} um ${clock(s)}`, en: `starts ${dayName(s)} at ${clock(s)}`, it: `inizia ${dayName(s)} alle ${clock(s)}`, fr: `commence ${dayName(s)} à ${clock(s)}`, es: `empieza ${dayName(s)} a las ${clock(s)}`, nl: `begint ${dayName(s)} om ${clock(s)}` }));
        return { active: false, text: e ? `${begin} · ${pick(lc, { de: "bis", en: "until", it: "fino a", fr: "jusqu'à", es: "hasta", nl: "tot" })} ${until(s)}` : begin };
      }
      return { active: true, text: e ? `${pick(lc, { de: "aktiv bis", en: "active until", it: "attiva fino alle", fr: "active jusqu'à", es: "activo hasta", nl: "actief tot" })} ${until(new Date())}` : (pick(lc, { de: "aktiv", en: "active", it: "attiva", fr: "active", es: "activo", nl: "actief" })) };
    };
    const top = alerts.length ? alertColour(alerts[0]) : null;
    const items = alerts.map((a, i) => {
      const open = this._open === String(i);
      const rel = timing(a);
      const event = a.event || (a.title || "").replace(/\s+-\s+\S+$/, "");
      const badge = a.severity || a.level || "";
      return `<div class="al ${open ? "open" : ""} ${rel.active ? "now" : ""}" data-i="${i}" style="--c:${alertColour(a)}">
        <div class="top"><span class="ic"><ha-icon icon="${alertIcon(a)}"></ha-icon></span>
          <span class="nm"><span class="l1"><b>${esc(event)}</b>${badge ? `<span class="badge">${esc(badge)}</span>` : ""}</span>
            <small><em>${esc(rel.text)}</em></small></span>
          <ha-icon class="chev" icon="mdi:chevron-${open ? "up" : "down"}"></ha-icon></div>
        ${open ? `<div class="body">${a.description && a.description !== event ? `<p>${esc(a.description)}</p>` : ""}${a.safety_guide ? `<p class="safe"><ha-icon icon="mdi:shield-check-outline"></ha-icon>${esc(a.safety_guide)}</p>` : ""}
          <p class="src">${esc([a.status, a.source].filter(Boolean).join(" · "))}</p></div>` : ""}
      </div>`;
    }).join("");
    this.shadowRoot.innerHTML = `<style>${this._css()}
      :host { display: block; height: 100%; }
      ha-card { height: 100%; box-sizing: border-box; display: flex; flex-direction: column; gap: 8px; overflow: hidden; container-type: size; }
      .list { flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; gap: 8px; overflow: hidden; }
      .more { flex: none; font-size: 12px; color: var(--secondary-text-color); padding-left: 2px; }
      .al { flex: none; }
      /* low cards: one line per alert */
      @container (max-height: 150px) {
        .head { font-size: 15px; margin: 0; }
        .top { padding: 4px 8px; gap: 8px; align-items: center; }
        .ic { width: 24px; height: 24px; } .ic ha-icon { --mdc-icon-size: 15px; }
        .nm { flex-direction: row; align-items: center; gap: 8px; min-width: 0; }
        .nm small { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .chev, .body { display: none; }
      }
      .head { margin-bottom: 2px; display: flex; align-items: center; gap: 8px; }
      .count { font-size: 12px; font-weight: 600; color: #fff; background: ${top || "var(--success-color, #43a047)"}; border-radius: 10px; padding: 1px 8px; }
      .none { display: flex; align-items: center; gap: 10px; color: var(--secondary-text-color); font-size: 14px; }
      .none ha-icon { color: var(--success-color, #43a047); }
      .al { border-radius: 12px; overflow: hidden; cursor: pointer; background: color-mix(in srgb, var(--c) ${this._ha ? 8 : 12}%, transparent);
            border: 1px solid color-mix(in srgb, var(--c) 35%, transparent); }
      .al.now { border-width: 2px; }
      .top { display: flex; align-items: center; gap: 12px; padding: 10px 12px; }
      .ic { width: 38px; height: 38px; border-radius: 50%; flex: none; display: flex; align-items: center; justify-content: center; background: var(--c); color: #fff; }
      .ic ha-icon { --mdc-icon-size: 22px; }
      .nm { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
      .l1 { display: flex; align-items: center; gap: 8px; min-width: 0; }
      .l1 b { font-size: 15px; font-weight: ${this._ha ? 500 : 600}; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
      .badge { flex: none; font-size: 11px; font-weight: 600; color: #fff; background: var(--c); border-radius: 8px; padding: 1px 7px; text-transform: uppercase; letter-spacing: .03em; }
      .nm small { font-size: 12px; color: var(--secondary-text-color); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
      .nm small em { font-style: normal; color: var(--primary-text-color); }
      .chev { color: var(--secondary-text-color); flex: none; }
      .body { padding: 0 14px 12px 62px; font-size: 13px; line-height: 1.45; }
      .body p { margin: 0 0 6px; } .safe { display: flex; gap: 6px; } .safe ha-icon { --mdc-icon-size: 16px; flex: none; color: var(--c); }
      .src { color: var(--secondary-text-color); font-size: 12px; }
      /* narrow cards: wrap instead of truncating */
      ha-card { container-type: inline-size; }
      @container (max-width: 380px) {
        .top { gap: 10px; padding: 8px 10px; align-items: flex-start; }
        .ic { width: 30px; height: 30px; } .ic ha-icon { --mdc-icon-size: 18px; }
        .l1 { flex-wrap: wrap; row-gap: 2px; }
        .l1 b { white-space: normal; font-size: 14px; }
        .nm small { white-space: normal; line-height: 1.35; }
        .chev { display: none; }
        .body { padding: 0 10px 10px 50px; }
      }
    </style>
    <ha-card>
      <div class="head">${esc(title)}${alerts.length ? `<span class="count">${alerts.length}</span>` : ""}</div>
      ${items ? `<div class="list">${items}</div><div class="more" hidden></div>` : `<div class="none"><ha-icon icon="mdi:check-circle-outline"></ha-icon>${pick(lc, { de: "Keine Warnungen für diesen Ort", en: "No warnings for this location", it: "Nessuna allerta per questo luogo", fr: "Aucune alerte pour ce lieu", es: "Sin avisos para esta ubicación", nl: "Geen waarschuwingen voor deze locatie" })}</div>`}
    </ha-card>`;
    requestAnimationFrame(() => this._fit(lc));
    this.shadowRoot.querySelectorAll(".al").forEach((el) => el.addEventListener("click", () => {
      this._open = this._open === el.dataset.i ? null : el.dataset.i;
      this._sig = ""; this._render();
    }));
  }
}

/* ----------------------------------------------------------------------- */
/* Life tile – one health / activity index as its own tile                  */
/* ----------------------------------------------------------------------- */
const LIFE_INDEX = Object.fromEntries([...LIFE_ITEMS.health, ...LIFE_ITEMS.activities].map(([k, kind, icon]) => [k.replace(/^life_/, ""), { key: k, kind, icon }]));

class MsnWeatherLifeTileCard extends MsnBase {
  static getStubConfig(hass) { return { ...MsnWeatherDetailsCard.getStubConfig(hass), index: "umbrella" }; }
  static getConfigForm() {
    const names = UI_DE
      ? { umbrella: "Regenschirm", walking: "Draußen / Spazierengehen", uv: "UV-Belastung", driving: "Fahrsicherheit", dressing: "Kleidung",
          heat_stroke: "Hitzschlag", wind_chill: "Windchill", running: "Laufen", cycling: "Radfahren", hiking: "Wandern",
          gardening: "Gartenarbeit", picnic: "Picknick", stargazing: "Sternbeobachtung" }
      : { umbrella: "Umbrella", walking: "Outdoors / walking", uv: "UV exposure", driving: "Driving", dressing: "Clothing",
          heat_stroke: "Heat stroke", wind_chill: "Wind chill", running: "Running", cycling: "Cycling", hiking: "Hiking",
          gardening: "Gardening", picnic: "Picnic", stargazing: "Stargazing" };
    return {
      schema: [
        { name: "entity", required: true, selector: { entity: { domain: "weather", integration: "msn_weather" } } },
        { name: "index", required: true, selector: { select: { mode: "dropdown", options: Object.keys(LIFE_INDEX).map((k) => ({ value: k, label: names[k] || k })) } } },
      ],
    };
  }
  getCardSize() { return 3; }
  getGridOptions() { return this._ha ? { columns: 6, rows: 2, min_columns: 3, min_rows: 1 } : { columns: 6, rows: 3, min_columns: 3, min_rows: 2 }; }
  _needsForecast() { return false; }

  _render() {
    if (!this._hass) return;
    const info = LIFE_INDEX[this._config.index] || LIFE_INDEX.umbrella;
    const st = this.st(info.key);
    if (!st) {
      this.shadowRoot.innerHTML = `<ha-card><div class="err">${this.t("notFound")} ${esc(this._config.entity)} (${esc(this._config.index || "")})</div></ha-card>`;
      return;
    }
    const L = lang(this._hass);
    const levels = (LIFE_LEVELS[L] || LIFE_LEVELS.en)[info.kind];
    const colours = info.kind === "dressing" ? DRESS_COLORS : CAT_COLORS;
    const dot = (c) => (c ? colours[clamp(c, 1, 5) - 1] : "var(--divider-color, #8884)");
    const cat = num(st.attributes.category) || 0;
    const hourly = (st.attributes.hourly || []).slice(0, 24);
    const tz = this._tz();
    const bars = hourly.map((h) => {
      const raw = num(h.category) || 0;
      return `<i title="${esc(timeStr(h.time, this._hass, tz))} · ${esc(raw ? levels[clamp(raw, 1, 5) - 1] : "–")}" style="height:${raw ? clamp(raw, 1, 5) * 20 : 4}%;background:${dot(raw)}"></i>`;
    }).join("");
    const chart = hourly.length ? `<div class="lb">${bars}</div>` : "";
    const name = this._lifeName(info.key, st);
    const summary = st.attributes.summary || "";
    const body = this._ha
      ? `<div class="hat" style="--c:${dot(cat)}">
          <div class="top"><span class="ic"><ha-icon icon="${info.icon}"></ha-icon></span>
            <span class="nm"><span class="name">${esc(name)}</span><span class="val">${esc(st.state)}</span></span></div>
          ${chart ? `<div class="feat">${chart}</div>` : ""}
          ${summary ? `<div class="txt">${esc(summary)}</div>` : ""}</div>`
      : `<div class="tile">
          <div class="t">${esc(name)}</div>
          <div class="viz">${chart}</div>
          <div class="hl"><span class="cdot" style="background:${dot(cat)}"></span>${esc(st.state)}</div>
          ${summary ? `<div class="sm">${esc(summary)}</div>` : ""}</div>`;
    this.shadowRoot.innerHTML = `<style>${this._css()}
      :host { display: block; height: 100%; }
      ha-card { height: 100%; padding: 0; box-sizing: border-box; overflow: hidden; container-type: size; }
      .tile { background: none; height: 100%; min-height: 110px; cursor: pointer; padding: 10px 12px; }
      .hat { cursor: pointer; }
      .lb { position: absolute; inset: 4px 0 0; display: flex; align-items: flex-end; gap: 2px; }
      .hat .feat .lb { inset: 0; }
      .lb i { flex: 1 1 0; border-radius: 2px 2px 0 0; min-height: 2px; }
      .cdot { width: 10px; height: 10px; border-radius: 50%; flex: none; }
      @container (max-height: 175px) { .tile .sm { display: none; } }
      @container (max-height: 120px) { .tile .hl { display: none; } .tile .t { margin-bottom: 0; } }
      @container (max-height: 150px) { .hat .txt { display: none; } }
      @container (max-height: 92px) { .hat .feat { display: none; } }
    </style><ha-card>${body}</ha-card>`;
    this.shadowRoot.querySelector(".tile, .hat").addEventListener("click", () => this.more(info.key));
  }
}

/* ----------------------------------------------------------------------- */
/* Rain cards – when does it rain, until when, how much                      */
/*   custom:msn-weather-rain-card        – sentence + mini bars (nowcast + 48 h forecast)  */
/*   custom:msn-weather-rain-chart-card  – amount per hour as bars with the time below      */
/* ----------------------------------------------------------------------- */
class MsnWeatherRainCard extends MsnBase {
  static getStubConfig(hass) { return MsnWeatherDetailsCard.getStubConfig(hass); }
  static getConfigForm() {
    return {
      schema: [
        { name: "entity", required: true, selector: { entity: { domain: "weather", integration: "msn_weather" } } },
        { name: "title", selector: { text: {} } },
      ],
    };
  }
  get _chart() { return false; }
  getCardSize() { return this._chart ? 4 : 2; }
  getGridOptions() {
    if (this._chart) return { columns: "full", rows: "auto", min_columns: 6 };
    return this._ha ? { columns: 6, rows: 2, min_columns: 4, min_rows: 2 } : { columns: 6, rows: 3, min_columns: 4, min_rows: 2 };
  }
  _signature() {
    const st = this.st("nowcast");
    return JSON.stringify((this._forecast || []).slice(0, 48).map((f) => [f.datetime, f.precipitation, f.precipitation_probability]))
      + (st ? st.state + st.attributes.timestamp : "") + this._w + this._config.appearance + Math.floor(Date.now() / 300000);
  }

  /** Hourly forecast for the next hours: time, amount, probability, snow. */
  _hours(n) {
    const now = Date.now();
    return (this._forecast || [])
      .map((f) => ({ t: new Date(f.datetime).getTime(), mm: Math.max(0, num(f.precipitation) || 0), p: num(f.precipitation_probability) || 0,
        snow: /snow/.test(f.condition || "") }))
      .filter((h) => h.t > now - 3600000).slice(0, n);
  }

  _outlook() {
    const de = lang(this._hass) === "de";
    const lc = lang(this._hass);
    const tz = this._tz();
    const inch = this._unit("precip") === "in";
    const wetMm = inch ? 0.002 : 0.05;  // = a visible bar in the rain chart
    const hours = this._hours(48);
    const st = this.st("nowcast"), a = (st && st.attributes) || {};
    const step = num(a.minutes_between_values) || 4;
    const rates = (a.precipitation_rate || []).slice(0, Math.floor(120 / step) + 1).map((v) => num(v) || 0);
    const ts = a.timestamp ? new Date(a.timestamp).getTime() : Date.now();
    const ncWet = rates.map((v) => (inch ? v * 25.4 : v) > 0.05);
    const now = Date.now();
    const dayKey = (t) => new Date(t).toLocaleDateString("en-CA", { timeZone: tz || undefined });
    const clock = (t) => timeStr(new Date(t).toISOString(), this._hass, tz);
    const when = (t) => {
      const k = dayKey(t);
      const day = k === dayKey(now) ? "" : k === dayKey(now + 86400000) ? (pick(lc, { de: "morgen ", en: "tomorrow ", it: "domani ", fr: "demain ", es: "mañana ", nl: "morgen " }))
        : new Date(t).toLocaleDateString(this._hass.language, { weekday: "long", timeZone: tz || undefined }) + " ";
      return `${day}${clock(t)}`;
    };
    const dur = (ms) => {
      const h = Math.round(ms / 3600000);
      if (h < 1) { const m = Math.max(5, Math.round(ms / 300000) * 5); return pick(lc, { de: `${m} Min.`, en: `${m} min`, it: `${m} min`, fr: `${m} min`, es: `${m} min`, nl: `${m} min` }); }
      return pick(lc, { de: `${h} Std.`, en: `${h} h`, it: `${h} h`, fr: `${h} h`, es: `${h} h`, nl: `${h} u` });
    };
    const amount = (from, to) => hours.filter((h) => h.t + 3600000 > from && h.t < to).reduce((s2, h) => s2 + h.mm, 0);
    const wetH = (h) => h.mm >= wetMm;
    const ncNow = ncWet.length ? ncWet[0] : null;
    const raining = ncNow !== null ? ncNow : (hours[0] ? wetH(hours[0]) : false);
    const snowAt = (t) => (hours.find((h) => h.t <= t && t < h.t + 3600000) || hours[0] || {}).snow;
    const word = (t) => (snowAt(t) ? (pick(lc, { de: "Schnee", en: "Snow", it: "Neve", fr: "Neige", es: "Nieve", nl: "Sneeuw" })) : (pick(lc, { de: "Regen", en: "Rain", it: "Pioggia", fr: "Pluie", es: "Lluvia", nl: "Regen" })));
    let kind, head, parts = [], start = null, end = null;
    if (raining) {
      start = now;
      const iDry = ncWet.indexOf(false);
      if (iDry > 0) end = ts + iDry * step * 60000;
      else {
        const j = hours.findIndex((h) => h.t > now && !wetH(h));
        end = j >= 0 ? hours[j].t : null;
      }
      kind = "raining";
      if (end && end - now < 2 * 3600000 && iDry > 0) head = pick(lc, { de: `${word(now)} hört in ${dur(end - now)} auf`, en: `${word(now)} stops in ${dur(end - now)}`, it: `${word(now)}: fine tra ${dur(end - now)}`, fr: `${word(now)} : fin dans ${dur(end - now)}`, es: `${word(now)}: termina en ${dur(end - now)}`, nl: `${word(now)} stopt over ${dur(end - now)}` });
      else head = end ? (pick(lc, { de: `${word(now)} bis ${when(end)}`, en: `${word(now)} until ${when(end)}`, it: `${word(now)} fino a ${when(end)}`, fr: `${word(now)} jusqu'à ${when(end)}`, es: `${word(now)} hasta ${when(end)}`, nl: `${word(now)} tot ${when(end)}` }))
        : (pick(lc, { de: `${word(now)} bis mindestens ${when((hours[hours.length - 1] || { t: now }).t + 3600000)}`, en: `${word(now)} until at least ${when((hours[hours.length - 1] || { t: now }).t + 3600000)}`, it: `${word(now)} fino ad almeno ${when((hours[hours.length - 1] || { t: now }).t + 3600000)}`, fr: `${word(now)} jusqu'à au moins ${when((hours[hours.length - 1] || { t: now }).t + 3600000)}`, es: `${word(now)} hasta al menos ${when((hours[hours.length - 1] || { t: now }).t + 3600000)}`, nl: `${word(now)} tot minstens ${when((hours[hours.length - 1] || { t: now }).t + 3600000)}` }));
      if (end) parts.push(pick(lc, { de: `noch ca. ${dur(end - now)}`, en: `about ${dur(end - now)} more`, it: `ancora circa ${dur(end - now)}`, fr: `encore environ ${dur(end - now)}`, es: `aún unos ${dur(end - now)}`, nl: `nog ca. ${dur(end - now)}` }));
    } else {
      const iWet = ncWet.indexOf(true);
      if (iWet > 0) start = ts + iWet * step * 60000;
      else {
        const j = hours.findIndex((h) => h.t + 3600000 > now && wetH(h));
        start = j >= 0 ? Math.max(hours[j].t, now) : null;
      }
      if (start === null) {
        kind = "dry";
        head = pick(lc, { de: "Kein Regen in den nächsten 48 Std.", en: "No rain in the next 48 h", it: "Nessuna pioggia nelle prossime 48 h", fr: "Pas de pluie dans les 48 h", es: "Sin lluvia en las próximas 48 h", nl: "Geen regen in de komende 48 uur" });
      } else {
        kind = "start";
        const j = hours.findIndex((h) => h.t >= start && !wetH(h) && h.t > start);
        end = j >= 0 ? hours[j].t : null;
        head = start - now < 2 * 3600000
          ? (pick(lc, { de: `${word(start)} in ${dur(start - now)}`, en: `${word(start)} in ${dur(start - now)}`, it: `${word(start)} tra ${dur(start - now)}`, fr: `${word(start)} dans ${dur(start - now)}`, es: `${word(start)} en ${dur(start - now)}`, nl: `${word(start)} over ${dur(start - now)}` }))
          : (pick(lc, { de: `${word(start)} ab ${when(start)}`, en: `${word(start)} from ${when(start)}`, it: `${word(start)} da ${when(start)}`, fr: `${word(start)} à partir de ${when(start)}`, es: `${word(start)} desde ${when(start)}`, nl: `${word(start)} vanaf ${when(start)}` }));
        if (end) parts.push(pick(lc, { de: `bis ${when(end)}`, en: `until ${when(end)}`, it: `fino a ${when(end)}`, fr: `jusqu'à ${when(end)}`, es: `hasta ${when(end)}`, nl: `tot ${when(end)}` }), pick(lc, { de: `ca. ${dur(end - start)}`, en: `about ${dur(end - start)}`, it: `circa ${dur(end - start)}`, fr: `environ ${dur(end - start)}`, es: `unos ${dur(end - start)}`, nl: `ca. ${dur(end - start)}` }));
        else if (hours.length) parts.push(pick(lc, { de: `bis mindestens ${when(hours[hours.length - 1].t + 3600000)}`, en: `until at least ${when(hours[hours.length - 1].t + 3600000)}`, it: `fino ad almeno ${when(hours[hours.length - 1].t + 3600000)}`, fr: `jusqu'à au moins ${when(hours[hours.length - 1].t + 3600000)}`, es: `hasta al menos ${when(hours[hours.length - 1].t + 3600000)}`, nl: `tot minstens ${when(hours[hours.length - 1].t + 3600000)}` }));
      }
    }
    if (start !== null) {
      const mm = amount(start, end || now + 48 * 3600000);
      if (mm >= wetMm) parts.push(`${fmt(mm, this._dec("precip"))} ${this._unit("precip")}`);
      const p = Math.max(0, ...hours.filter((h) => h.t + 3600000 > start && (!end || h.t < end)).map((h) => h.p));
      if (p && kind === "start") parts.push(pick(lc, { de: `Wahrscheinlichkeit ${fmt(p)} %`, en: `probability ${fmt(p)} %`, it: `probabilità ${fmt(p)} %`, fr: `probabilité ${fmt(p)} %`, es: `probabilidad ${fmt(p)} %`, nl: `kans ${fmt(p)} %` }));
    }
    const warn = (this.attr("alerts", "alerts") || []).find((al) => /rain|regen|pioggia|pluie|lluvia|regen|snow|schnee|neve|neige|nieve|sneeuw|thunder|gewitter/i.test(`${al.event || ""} ${al.title || ""}`));
    let warning = "";
    if (warn) {
      const ws = warn.start ? new Date(warn.start).getTime() : null;
      const lvl = warn.severity || warn.level || "";
      warning = ws && ws > now
        ? (pick(lc, { de: `Warnung (${lvl}) ab ${when(ws)}`, en: `Warning (${lvl}) from ${when(ws)}`, it: `Allerta (${lvl}) da ${when(ws)}`, fr: `Alerte (${lvl}) à partir de ${when(ws)}`, es: `Aviso (${lvl}) desde ${when(ws)}`, nl: `Waarschuwing (${lvl}) vanaf ${when(ws)}` }))
        : (pick(lc, { de: `Warnung (${lvl}) aktiv`, en: `Warning (${lvl}) active`, it: `Allerta (${lvl}) attiva`, fr: `Alerte (${lvl}) active`, es: `Aviso (${lvl}) activo`, nl: `Waarschuwing (${lvl}) actief` }));
    }
    const icon = kind === "dry" ? "mdi:weather-partly-cloudy" : snowAt(start || now) ? "mdi:weather-snowy" : "mdi:weather-pouring";
    return { kind, head, sub: parts.join(" · "), warning, icon, hours };
  }

  /** Bars of the amount per hour; labels = show the amounts above the bars. */
  _bars(hours, { labels = true, ticks = true, tickEvery = 3 } = {}) {
    const tz = this._tz();
    const dec = this._dec("precip");
    const mx = Math.max(this._unit("precip") === "in" ? 0.04 : 1, ...hours.map((h) => h.mm));
    const peak = hours.reduce((b, h, i) => (h.mm > (hours[b] ? hours[b].mm : 0) ? i : b), -1);
    let prev = null;
    return hours.map((h, i) => {
      const day = new Date(h.t).toLocaleDateString("en-CA", { timeZone: tz || undefined });
      const split = prev && day !== prev ? `<span class="split"><em>${esc(new Date(h.t).toLocaleDateString(this._hass.language, { weekday: "short", timeZone: tz || undefined }))}</em></span>` : "";
      prev = day;
      const hgt = h.mm > 0 ? Math.max(4, (h.mm / mx) * 100) : 0;
      const col = h.snow ? "#38bdf8" : "#2563eb";
      const tipTime = `${new Date(h.t).toLocaleDateString(this._hass.language, { weekday: "short", timeZone: tz || undefined })} ${timeStr(new Date(h.t).toISOString(), this._hass, tz)}`;
      const side = i < hours.length / 2 ? "l" : "r";
      return `<div class="hb">
        <span class="tip ${side}"><b>${esc(tipTime)}</b> ${fmt(h.mm, dec)} ${esc(this._unit("precip"))} · ${fmt(h.p)} %</span>
        ${split}<div class="col">${h.mm > 0 && (labels === true || (labels === "peak" && i === peak)) ? `<b>${fmt(h.mm, dec)}</b>` : ""}<i style="height:${hgt}%;background:${col};opacity:${0.45 + 0.55 * clamp(h.p / 100, 0, 1)}"></i></div>
        ${ticks ? `<span class="tk">${i % tickEvery === 0 ? esc(timeStr(new Date(h.t).toISOString(), this._hass, tz).replace(/:00(?=\s|$)/, "")) : ""}</span>` : ""}</div>`;
    }).join("");
  }

  _render() {
    if (!this._hass) return;
    const de = lang(this._hass) === "de";
    const lc = lang(this._hass);
    if (this._forecast === null) {
      this.shadowRoot.innerHTML = `<style>${this._css()}</style><ha-card><div class="lbl">${pick(lc, { de: "Lade Vorhersage …", en: "Loading forecast …", it: "Caricamento previsioni …", fr: "Chargement des prévisions …", es: "Cargando previsión …", nl: "Verwachting laden …" })}</div></ha-card>`;
      return;
    }
    const css = `
      .hb { flex: 1 1 0; min-width: 0; display: flex; flex-direction: column; position: relative; }
      .hb .col { flex: 1; display: flex; flex-direction: column; justify-content: flex-end; align-items: center; min-height: 0; }
      .hb .col i { display: block; width: 78%; border-radius: 3px 3px 0 0; }
      .hb .col b { font-size: 10px; font-weight: 500; color: var(--secondary-text-color); margin-bottom: 2px; white-space: nowrap; }
      .hb .tk { height: 14px; font-size: 11px; color: var(--secondary-text-color); white-space: nowrap; text-align: left; }
      .hb .tip { display: none; position: absolute; bottom: calc(100% - 10px); z-index: 3; white-space: nowrap; font-size: 12px; padding: 4px 8px;
                 border-radius: 8px; background: var(--primary-text-color); color: var(--card-background-color, #fff); pointer-events: none; }
      .hb .tip.l { left: 0; } .hb .tip.r { right: 0; }
      .hb .tip b { font-weight: 600; }
      .hb:hover .tip, .hb:active .tip { display: block; }
      .hb:hover .col i { filter: brightness(1.25); }
      .split { position: absolute; left: -1px; top: 0; bottom: 14px; border-left: 1px dashed var(--secondary-text-color); opacity: .6; }
      .split em { position: absolute; top: -2px; left: 3px; font-style: normal; font-size: 10px; white-space: nowrap; }
    `;
    if (this._chart) {
      const n = clamp(num(this._config.hours) || 48, 6, 48);
      const hours = this._hours(n);
      const total = hours.reduce((a, h) => a + h.mm, 0);
      const colW = (this._width - 32) / Math.max(hours.length, 1);
      const title = this._config.title || (pick(lc, { de: `Niederschlag ${n} Std.`, en: `Precipitation ${n} h`, it: `Precipitazioni ${n} h`, fr: `Précipitations ${n} h`, es: `Precipitación ${n} h`, nl: `Neerslag ${n} uur` }));
      this.shadowRoot.innerHTML = `<style>${this._css()}${css}
        ha-card { display: flex; flex-direction: column; gap: 8px; }
        .head { margin-bottom: 0; display: flex; justify-content: space-between; align-items: baseline; }
        .head small { font-weight: 400; color: var(--secondary-text-color); font-size: 13px; }
        .bars { height: 130px; display: flex; gap: 2px; padding-top: 14px; border-bottom: 1px solid var(--msn-muted-line); }
        .bars + .tks { display: none; }
        .hb .tk { position: absolute; top: 100%; margin-top: 2px; left: 50%; transform: translateX(-50%); }
        .wrap { padding-bottom: 18px; }
      </style>
      <ha-card>
        <div class="head">${esc(title)}<small>${fmt(total, this._dec("precip"))} ${esc(this._unit("precip"))}</small></div>
        <div class="wrap"><div class="bars">${this._bars(hours, { labels: colW >= 22 ? true : "peak", tickEvery: colW >= 16 ? 3 : 6 })}</div></div>
      </ha-card>`;
      return;
    }
    const o = this._outlook();
    const color = o.kind === "dry" ? "var(--secondary-text-color)" : "#2563eb";
    const mini = `<div class="mini">${this._bars(o.hours.slice(0, 48), { labels: false, ticks: false })}</div>`;
    this.shadowRoot.innerHTML = `<style>${this._css()}${css}
      :host { display: block; height: 100%; }
      ha-card { height: 100%; box-sizing: border-box; display: flex; flex-direction: column; gap: 6px; overflow: hidden; cursor: pointer; container-type: size;
                ${this._ha ? "padding: 12px;" : ""} }
      .top { display: flex; align-items: center; gap: 10px; }
      .ic { width: 38px; height: 38px; border-radius: 50%; flex: none; display: flex; align-items: center; justify-content: center;
            background: color-mix(in srgb, ${color} 18%, transparent); color: ${color}; }
      .ic ha-icon { --mdc-icon-size: 22px; }
      .nm { min-width: 0; display: flex; flex-direction: column; }
      .nm .t { font-size: 13px; color: var(--secondary-text-color); }
      .nm b { font-size: 17px; font-weight: ${this._ha ? 500 : 700}; line-height: 1.25; }
      .sub { font-size: 13px; color: var(--secondary-text-color); line-height: 1.35; }
      .warn { display: flex; align-items: center; gap: 4px; font-size: 12px; color: var(--warning-color, #f9a825); }
      .warn ha-icon { --mdc-icon-size: 15px; }
      .mini { flex: 1 1 0; min-height: 22px; display: flex; gap: 1px; align-items: stretch; }
      .mini .split { bottom: 0; } .mini .split em { display: none; }
      @container (max-height: 110px) { .mini { display: none; } }
    </style>
    <ha-card>
      <div class="top"><span class="ic"><ha-icon icon="${o.icon}"></ha-icon></span>
        <span class="nm"><span class="t">${esc(this._config.title || (pick(lc, { de: "Regen", en: "Rain", it: "Pioggia", fr: "Pluie", es: "Lluvia", nl: "Regen" })))}</span><b>${esc(o.head)}</b></span></div>
      ${o.sub ? `<div class="sub">${esc(o.sub)}</div>` : ""}
      ${mini}
    </ha-card>`;
    this.shadowRoot.querySelector("ha-card").addEventListener("click", () => this.more("nowcast"));
  }
}

class MsnWeatherRainChartCard extends MsnWeatherRainCard {
  static getConfigForm() {
    return {
      schema: [
        { name: "entity", required: true, selector: { entity: { domain: "weather", integration: "msn_weather" } } },
        { name: "title", selector: { text: {} } },
        { name: "hours", selector: { number: { min: 6, max: 48, step: 1, mode: "box" } } },
      ],
    };
  }
  get _chart() { return true; }
  get _responsive() { return true; }
}

/* ----------------------------------------------------------------------- */
/* Monthly card – calendar like the monthly forecast on msn.com             */
/* ----------------------------------------------------------------------- */
class MsnWeatherMonthlyCard extends MsnBase {
  static getStubConfig(hass) { return MsnWeatherDetailsCard.getStubConfig(hass); }
  static getConfigForm() {
    return {
      schema: [
        { name: "entity", required: true, selector: { entity: { domain: "weather", integration: "msn_weather" } } },
        { name: "title", selector: { text: {} } },
        { name: "days", selector: { number: { min: 7, max: 42, step: 1, mode: "box" } } },
      ],
    };
  }
  get _responsive() { return true; }
  getCardSize() { return 8; }
  getGridOptions() { return { columns: "full", rows: "auto", min_columns: 6 }; }
  _needsForecast() { return false; }
  _render() {
    if (!this._hass) return;
    const L = lang(this._hass);
    const days = (this.attr("monthly_forecast", "days") || []).slice(0, this._config.days || 35);
    const compact = this._width < 560;
    if (!days.length) {
      this.shadowRoot.innerHTML = `<style>${this._css()}</style><ha-card><div class="head">${esc(this._config.title || (pick(L, { de: "Monatsvorhersage", en: "Monthly forecast", it: "Previsioni mensili", fr: "Prévisions mensuelles", es: "Previsión mensual", nl: "Maandverwachting" })))}</div><div class="lbl">${this.t("noData")}</div></ha-card>`;
      return;
    }
    const today = dayKey(new Date());
    const first = new Date(days[0].date + "T12:00:00");
    const lead = (first.getDay() + 6) % 7; // Monday first
    const wd = [...Array(7)].map((_, i) => new Date(2024, 0, 1 + i).toLocaleDateString(this._hass.language, { weekday: "short" }));
    const cells = [...Array(lead)].map(() => `<div class="c empty"></div>`).concat(days.map((d) => {
      const dt = new Date(d.date + "T12:00:00");
      return `<div class="c ${d.date === today ? "today" : ""}">
        <div class="dn">${dt.getDate()}${dt.getDate() === 1 ? " " + dt.toLocaleDateString(this._hass.language, { month: "short" }) : ""}</div>
        <ha-icon icon="${COND_ICON[d.condition] || "mdi:weather-partly-cloudy"}" style="color:${COND_COLOR[d.condition] || "#aaa"}"></ha-icon>
        <div class="t"><b>${fmt(d.temp_high)}°</b> <span>${fmt(d.temp_low)}°</span></div>
        ${num(d.precipitation_probability) ? `<div class="p"><ha-icon icon="mdi:water"></ha-icon>${fmt(d.precipitation_probability)}%</div>` : ""}
      </div>`;
    })).join("");
    const avgH = this.val("climate_avg_high"), avgL = this.val("climate_avg_low");
    const recH = this.val("climate_record_high"), recL = this.val("climate_record_low");
    const recHY = this.attr("climate_record_high", "year"), recLY = this.attr("climate_record_low", "year");
    const since = this.attr("climate_avg_high", "since");
    const stat = (icon, color, label, value) => this._ha
      ? `<div class="st" style="--c:${color}"><span class="ic"><ha-icon icon="${icon}"></ha-icon></span><span class="nm"><span>${label}</span><b>${value}</b></span></div>`
      : `<div><span>${label}</span><b>${value}</b></div>`;
    const haCss = !this._ha ? "" : `
      .cal { gap: 0 !important; }
      .wdr { gap: 0; border-bottom: 1px solid var(--divider-color, rgba(127,127,127,.25)); padding-bottom: 6px; margin-bottom: 0; }
      .wd { font-weight: 500; text-transform: uppercase; font-size: 11px; letter-spacing: .04em; }
      .cal .c { border: none !important; border-radius: 0 !important; background: none !important; box-shadow: inset 0 -1px 0 var(--divider-color, rgba(127,127,127,.18)); }
      .cal .c:not(.empty):hover { background: rgba(var(--rgb-primary-text-color, 0, 0, 0), .04) !important; }
      .cal .c.empty { box-shadow: none; }
      .cal .c .dn { font-size: 12px; top: 5px; left: 7px; }
      .cal .c.today { background: rgba(var(--rgb-primary-color, 3, 169, 244), .10) !important; border-radius: 10px !important; box-shadow: none; }
      .cal .c.today .dn { color: var(--primary-color); font-weight: 700; }
      .c .t b { font-weight: 500; } .c .p { color: var(--secondary-text-color); } .c .p ha-icon { color: #3b82f6; }
      .clim { gap: 6px 12px; margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--divider-color, rgba(127,127,127,.25)); }
      .clim .st { border: none !important; background: none !important; padding: 0 !important; display: flex; align-items: center; gap: 10px; }
      .clim .ic { width: 34px; height: 34px; border-radius: 50%; flex: none; display: flex; align-items: center; justify-content: center;
                  background: color-mix(in srgb, var(--c) 18%, transparent); color: var(--c); }
      .clim .ic ha-icon { --mdc-icon-size: 18px; }
      .clim .nm { display: flex; flex-direction: column; min-width: 0; }
      .clim b { font-size: 16px; font-weight: 500; } .clim span span { font-size: 12px; }`;
    this.shadowRoot.innerHTML = `<style>${this._css()}
      :host { height: 100%; }
      ha-card { height: 100%; box-sizing: border-box; display: flex; flex-direction: column; overflow: hidden; }
      .head { flex: none; }
      .wdr { display:grid; grid-template-columns: repeat(7, minmax(0,1fr)); gap: 6px; flex: none; margin-bottom: 4px; }
      .cal { flex: 1 1 auto; min-height: 0; display:grid; grid-template-columns: repeat(7, minmax(0,1fr)); grid-auto-rows: minmax(${compact ? 52 : 70}px, 1fr); gap: ${compact ? 4 : 6}px; overflow: hidden; }
      .wd { text-align:center; font-size: 12px; color: var(--msn-muted); }
      .c { background: var(--msn-tile-bg); border-radius: 12px; padding: 4px; display:flex; flex-direction:column; align-items:center; justify-content:center; gap: 2px; min-height: 0; min-width: 0; overflow: hidden; position: relative; }
      .c .p { ${compact ? "display:none;" : ""} }
      .c.empty { background: none; } .c.today { outline: 2px solid var(--primary-color); }
      .c .dn { font-size: 11px; color: var(--msn-muted); position: absolute; top: 4px; left: 6px; }
      .c ha-icon { --mdc-icon-size: 24px; } .c .t { font-size: 14px; } .c .t span { color: var(--msn-muted); }
      .c .p { font-size: 11px; color: #3b82f6; } .c .p ha-icon { --mdc-icon-size: 11px; }
      .clim { flex: none; display:grid; grid-template-columns: repeat(${compact ? 2 : 4}, minmax(0,1fr)); gap: 8px; margin-top: 10px; }
      .clim div { background: var(--msn-tile-bg); border-radius: 12px; padding: 6px 10px; min-width: 0; }
      .clim b { font-size: 17px; display:block; } .clim span { font-size: 11px; color: var(--msn-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block; }
      ${haCss}
    </style>
    <ha-card>
      <div class="head">${esc(this._config.title || (pick(L, { de: "Monatsvorhersage", en: "Monthly forecast", it: "Previsioni mensili", fr: "Prévisions mensuelles", es: "Previsión mensual", nl: "Maandverwachting" })))}</div>
      <div class="wdr">${wd.map((w) => `<div class="wd">${esc(w)}</div>`).join("")}</div>
      <div class="cal">${cells}</div>
      ${avgH !== undefined ? `<div class="clim">
        ${stat("mdi:thermometer-chevron-up", "#ff7043", pick(L, { de: "Ø Höchstwert heute", en: "Avg high today", it: "Massima media oggi", fr: "Max. moyenne du jour", es: "Máxima media hoy", nl: "Gem. maximum vandaag" }), fmt(avgH) + "°")}
        ${stat("mdi:thermometer-chevron-down", "#42a5f5", pick(L, { de: "Ø Tiefstwert heute", en: "Avg low today", it: "Minima media oggi", fr: "Min. moyenne du jour", es: "Mínima media hoy", nl: "Gem. minimum vandaag" }), fmt(avgL) + "°")}
        ${stat("mdi:thermometer-alert", "#e53935", (pick(L, { de: "Rekordhoch", en: "Record high", it: "Record massimo", fr: "Record de chaleur", es: "Récord máximo", nl: "Warmterecord" })) + (recHY ? " (" + recHY + ")" : ""), fmt(recH) + "°")}
        ${stat("mdi:snowflake-thermometer", "#5c6bc0", (pick(L, { de: "Rekordtief", en: "Record low", it: "Record minimo", fr: "Record de froid", es: "Récord mínimo", nl: "Kouderecord" })) + (recLY ? " (" + recLY + ")" : ""), fmt(recL) + "°")}
      </div>` : ""}
    </ha-card>`;
  }
}

/* ----------------------------------------------------------------------- */
/* Map card – weather map image with correct aspect ratio (also in the editor) */
/* ----------------------------------------------------------------------- */
class MsnWeatherMapCard extends MsnBase {
  disconnectedCallback() {
    super.disconnectedCallback();
    clearInterval(this._playTimer);
    this._stopPlayer();
  }

  _stopPlayer() {
    clearTimeout(this._frameTimer);
    try { this._decoder?.close(); } catch (e) { /* closed */ }
    this._decoder = null;
    this._player = null;
  }

  /**
   * Play the animated map ourselves (ImageDecoder): the slider can pause and scrub it.
   * Returns false when the browser cannot decode the animation (the <img> keeps playing then).
   */
  async _initPlayer(url, st) {
    this._stopPlayer();
    const times = (st.attributes.frames || []).map((f) => new Date(f).getTime());
    if (times.length < 2 || !("ImageDecoder" in window)) return false;
    const token = (this._playerToken = (this._playerToken || 0) + 1);
    try {
      const res = await fetch(url, { credentials: "same-origin" });
      const type = (res.headers.get("content-type") || "image/webp").split(";")[0];
      if (!(await ImageDecoder.isTypeSupported(type))) return false;
      const decoder = new ImageDecoder({ data: await res.arrayBuffer(), type });
      await decoder.tracks.ready;
      const n = decoder.tracks.selectedTrack.frameCount;
      if (token !== this._playerToken || n < 2) { decoder.close(); return false; }
      const canvas = this.shadowRoot.querySelector(".img canvas");
      if (!canvas) { decoder.close(); return false; }
      this._decoder = decoder;
      const ms = num(st.attributes.frame_ms) || 700;
      const p = (this._player = { n: Math.min(n, times.length), idx: 0, paused: false, ms, times, canvas, ctx: canvas.getContext("2d") });
      await this._showFrame(0);
      canvas.classList.add("ok");
      const loop = async () => {
        if (this._player !== p) return;
        // only advance while the card is on screen and the page is visible
        const r = this.getBoundingClientRect();
        const onScreen = document.visibilityState === "visible" && r.width > 0 && r.bottom > 0 && r.top < (window.innerHeight || 1e6);
        if (!p.paused && onScreen) { p.idx = (p.idx + 1) % p.n; await this._showFrame(p.idx); }
        this._frameTimer = setTimeout(loop, p.idx === p.n - 1 ? ms * 3 : ms);
      };
      this._frameTimer = setTimeout(loop, ms);
      return true;
    } catch (e) {
      return false;
    }
  }

  async _showFrame(i) {
    const p = this._player;
    if (!p || !this._decoder) return;
    try {
      const { image } = await this._decoder.decode({ frameIndex: i });
      if (p.canvas.width !== image.displayWidth) { p.canvas.width = image.displayWidth; p.canvas.height = image.displayHeight; }
      p.ctx.drawImage(image, 0, 0);
      image.close();
    } catch (e) { return; }
    p.idx = i;
    const tt = this.shadowRoot.querySelector(".ttl .tt");
    if (tt) tt.textContent = this._frameLabel(p.times[i]);
  }


  /** Fallback without ImageDecoder: follow the animated WebP by time (title only). */
  _startPlayhead(st) {
    clearInterval(this._playTimer);
    const tt = this.shadowRoot.querySelector(".ttl .tt");
    const frames = (st.attributes.frames || []).map((f) => new Date(f).getTime());
    if (!tt || frames.length < 2) return;
    const ms = num(st.attributes.frame_ms) || 700;
    const n = frames.length, cycle = (n - 1) * ms + 3 * ms, t0 = performance.now();
    this._playTimer = setInterval(() => {
      if (!tt.isConnected) { clearInterval(this._playTimer); return; }
      const i = Math.min(n - 1, Math.floor(((performance.now() - t0) % cycle) / ms));
      tt.textContent = this._frameLabel(frames[i]);
    }, 175);
  }


  /** "+9 h · Mo. 23:00" (forecast) or "Mo. 13:30" (observations). */
  _frameLabel(t) {
    const tz = this._tz();
    const d = new Date(t);
    const day = d.toLocaleDateString(this._hass.language, { weekday: "short", timeZone: tz || undefined });
    const time = `${day} ${timeStr(d.toISOString(), this._hass, tz)}`;
    const h = Math.round((t - Date.now()) / 3600000);
    return h >= 1 ? `+${h} h · ${time}` : time;  // the slider uses the same hours
  }

  /** Legend from the image attributes (gradient or radar swatches). */
  _legendHtml(lg) {
    if (!lg || this._config.show_legend === false) return "";
    if (this._legendCollapsed) return `<div class="lgd mini" title="Legende"><ha-icon icon="mdi:palette-outline"></ha-icon></div>`;
    if (lg.type === "levels") {
      return `<div class="lgd lv">${lg.items.map((it) => `<span><i style="background:${it.color}"></i>${esc(it.label)}</span>`).join("")}</div>`;
    }
    if (lg.type === "swatches") {
      return `<div class="lgd sw">${lg.rows.map((r) => `<div class="row"><span>${esc(r.label)}</span>${r.colors.map((c) => `<i style="background:${c}"></i>`).join("")}</div>`).join("")}
        <div class="row ends"><span></span><em>${esc(lg.low)}</em><em>${esc(lg.high)}</em></div></div>`;
    }
    return `<div class="lgd gr">${lg.unit ? `<span class="u">${esc(lg.unit)}</span>` : ""}<div class="scale">
      <div class="bar" style="background:linear-gradient(90deg, ${lg.stops.join(", ")})"></div>
      <div class="ticks">${lg.ticks.map(([p, t]) => `<span style="left:${p * 100}%">${esc(t)}</span>`).join("")}</div></div></div>`;
  }


  static getStubConfig(hass) {
    const img = Object.values(hass.entities || {}).find((e) => e.platform === "msn_weather" && e.entity_id.startsWith("image.") && !e.disabled_by);
    return { entity: img ? img.entity_id : "" };
  }
  static getConfigForm() {
    return {
      schema: [
        { name: "entity", required: true, selector: { entity: { domain: "image", integration: "msn_weather" } } },
        { name: "zoom", selector: { number: { min: 3, max: 11, step: 1, mode: "slider" } } },
        { name: "show_legend", selector: { boolean: {} } },
        { name: "show_zoom", selector: { boolean: {} } },
        { name: "fit", selector: { select: { mode: "dropdown", options: [{ value: "cover", label: "Cover (crop)" }, { value: "contain", label: "Contain (show all)" }] } } },
      ],
    };
  }
  _needsForecast() { return false; }
  getCardSize() { return 5; }
  getGridOptions() { return { columns: 12, min_columns: 4 }; }
  _signature() {
    const s = this._hass.states[this._config.entity];
    const n = this._ents.map_forecast_hours ? this._hass.states[this._ents.map_forecast_hours] : null;
    const sel = this._ents.cyclone_map_storm ? this._hass.states[this._ents.cyclone_map_storm] : null;
    const zm = this._ents.map_zoom ? this._hass.states[this._ents.map_zoom] : null;
    return (zm ? zm.state : "") + (s ? s.state + JSON.stringify(s.attributes.width) : "") + (n ? n.state : "") + (sel ? sel.state + sel.attributes.options : "");
  }
  _render() {
    if (!this._hass) return;
    const s = this._hass.states[this._config.entity];
    if (!s) {
      this.shadowRoot.innerHTML = `<ha-card><div class="err">${this.t("notFound")} ${esc(this._config.entity)}</div></ha-card>`;
      return;
    }
    const w = num(s.attributes.width) || 800, h = num(s.attributes.height) || 500;
    const pic = s.attributes.entity_picture ? `${s.attributes.entity_picture}${s.attributes.entity_picture.includes("?") ? "&" : "?"}v=${encodeURIComponent(s.state)}` : "";
    const numId = this._ents.map_forecast_hours;
    const nst = numId ? this._hass.states[numId] : null;
    // forecast slider inside the map; while the animation plays a marker follows the shown hour
    // tropical cyclone map: one chip per active storm (drives the select entity)
    const reg = this._hass.entities[this._config.entity];
    const selId = this._ents.cyclone_map_storm;
    const sel = selId && reg && reg.translation_key === "map_tropical_cyclones" ? this._hass.states[selId] : null;
    const stormInfo = Object.fromEntries((this.attr("tropical_cyclones", "storms") || []).map((x) => [x.name, x]));
    const opts = sel ? (sel.attributes.options || []) : [];
    const chips = opts.length > 2 ? `<div class="chips">${opts.map((o) => {
      const info = stormInfo[o];
      const label = o === "auto" ? "Auto" : `${esc(o)}${info ? ` <small>${esc(info.category)}</small>` : ""}`;
      return `<span class="chip ${sel.state === o ? "on" : ""}" data-o="${esc(o)}">${o === "auto" ? `<ha-icon icon="mdi:auto-mode"></ha-icon>` : `<ha-icon icon="mdi:weather-hurricane"></ha-icon>`}${label}</span>`;
    }).join("")}</div>` : "";
    // title / legend as overlays when they are not drawn into the image
    const clean = s.attributes.labels_in_image === false;
    const firstFrame = (s.attributes.frames || [])[0] || s.attributes.valid_time;
    // a changed forecast hour is "being calculated" until the new image is there
    const shown = num(s.attributes.forecast_hours);
    const pending = nst && s.attributes.supports_forecast && shown !== null && num(nst.state) !== shown;
    const busy = pick(lang(this._hass), { de: "wird berechnet …", en: "calculating …", it: "calcolo in corso …", fr: "calcul en cours …", es: "calculando …", nl: "wordt berekend …" });
    const titleHtml = clean ? `<div class="ttl"><b>${esc(s.attributes.title || this._name(s))}</b>${firstFrame ? `<span class="tt">${esc(this._frameLabel(new Date(firstFrame).getTime()))}</span>` : ""}${pending ? `<span class="busy">${busy}</span>` : ""}</div>` : "";
    // fixed zoom of this card: ask the integration once to render this map with it
    const wantZoom = num(this._config.zoom);
    if (wantZoom && s.attributes.fixed_zoom !== wantZoom && this._zoomReq !== `${this._config.entity}:${wantZoom}`) {
      this._zoomReq = `${this._config.entity}:${wantZoom}`;
      this._hass.callService("msn_weather", "set_map_zoom", { entity_id: this._config.entity, zoom: wantZoom });
    }
    const legendHtml = clean ? this._legendHtml(s.attributes.legend) : "";
    // zoom buttons (all maps share the zoom; the cyclone map fits its storm itself)
    const zoomId = this._ents.map_zoom;
    const zst = zoomId && this._config.show_zoom === true && !this._config.zoom && !(reg && reg.translation_key === "map_tropical_cyclones") ? this._hass.states[zoomId] : null;
    const zoom = zst ? num(zst.state) : null;
    const zoomHtml = zst ? `<div class="zoom"><button data-z="1" ${zoom >= 11 ? "disabled" : ""} title="+">+</button><button data-z="-1" ${zoom <= 3 ? "disabled" : ""} title="−">−</button></div>` : "";
    this.shadowRoot.innerHTML = `<style>${this._css()}
      ha-card { padding: 0; overflow: hidden; }
      .ttl, .lgd { position: absolute; z-index: 2; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,.2); pointer-events: none;
                   background: color-mix(in srgb, var(--card-background-color, #fff) 90%, transparent); backdrop-filter: blur(4px); color: var(--primary-text-color); }
      .ttl { top: 8px; left: 8px; max-width: calc(100% - 64px); padding: 4px 12px; font-size: 13px; display: flex; gap: 8px; align-items: baseline; white-space: nowrap; overflow: hidden; }
      .ttl b { font-weight: 500; overflow: hidden; text-overflow: ellipsis; }
      .ttl .busy { color: var(--primary-color); } .ttl .tt { color: var(--secondary-text-color); font-variant-numeric: tabular-nums; }
      .lgd { right: 8px; bottom: 8px; width: min(44%, 300px); box-sizing: border-box; padding: 6px 10px 4px; font-size: 11px; }
      .lgd.gr { display: flex; align-items: flex-start; gap: 8px; }
      .lgd { pointer-events: auto; cursor: pointer; }
      .lgd.mini { width: auto; padding: 4px 6px; } .lgd.mini ha-icon { --mdc-icon-size: 18px; color: var(--secondary-text-color); }
      .lgd.lv { width: auto; max-width: 60%; display: flex; flex-wrap: wrap; gap: 4px 10px; padding: 5px 10px; }
      .lgd.lv span { display: inline-flex; align-items: center; gap: 5px; color: var(--secondary-text-color); white-space: nowrap; }
      .lgd.lv i { width: 12px; height: 10px; border-radius: 2px; display: inline-block; }
      .lgd .u { color: var(--secondary-text-color); padding-top: 1px; }
      .lgd .scale { flex: 1; } .lgd .bar { height: 8px; border-radius: 4px; }
      .lgd .ticks { position: relative; height: 14px; margin: 2px 4px 0; }
      .lgd .ticks span { position: absolute; transform: translateX(-50%); color: var(--secondary-text-color); }
      .lgd.sw .row { display: grid; grid-template-columns: 6.5em repeat(6, 1fr); gap: 2px; align-items: center; }
      .lgd.sw .row span { padding-right: 6px; color: var(--secondary-text-color); }
      .lgd.sw .row i { height: 8px; border-radius: 2px; }
      .lgd.sw .ends { grid-template-columns: 6.5em 1fr 1fr; } .lgd.sw .ends em { font-style: normal; color: var(--secondary-text-color); }
      .lgd.sw .ends em:last-child { text-align: right; }
      .zoom { position: absolute; top: 8px; right: 8px; z-index: 2; display: flex; flex-direction: column; border-radius: 10px; overflow: hidden;
              box-shadow: 0 1px 4px rgba(0,0,0,.25); }
      .zoom button { width: 30px; height: 30px; border: none; font-size: 18px; line-height: 1; cursor: pointer; padding: 0;
                     background: color-mix(in srgb, var(--card-background-color, #fff) 92%, transparent); color: var(--primary-text-color); }
      .zoom button + button { border-top: 1px solid var(--divider-color, rgba(127,127,127,.3)); }
      .zoom button:disabled { opacity: .35; cursor: default; }
      .chips { position: absolute; left: 8px; right: 8px; bottom: 8px; display: flex; gap: 6px; overflow-x: auto; scrollbar-width: none; z-index: 1; }
      .chips::-webkit-scrollbar { display: none; }
      .chip { display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; border-radius: 16px; font-size: 13px; cursor: pointer; white-space: nowrap;
              border: 1px solid var(--divider-color, rgba(127,127,127,.3)); user-select: none; }
      .chip ha-icon { --mdc-icon-size: 16px; } .chip small { color: var(--secondary-text-color); font-size: 11px; }
      .chip { background: color-mix(in srgb, var(--card-background-color, #fff) 88%, transparent); backdrop-filter: blur(4px); color: var(--primary-text-color); }
      .chip.on { background: var(--primary-color); color: var(--text-primary-color, #fff); border-color: transparent; font-weight: 500; }
      .chip.on small { color: inherit; opacity: .8; }
      .img { width: 100%; aspect-ratio: ${w} / ${h}; background: var(--msn-tile-bg); cursor: pointer; display:block; }
      .img img { width: 100%; height: 100%; object-fit: ${this._config.fit === "contain" ? "contain" : "cover"}; display:block; }
      .img { position: relative; }
      .ph { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px;
            color: var(--secondary-text-color); font-size: 13px; }
      .ph ha-icon { --mdc-icon-size: 36px; opacity: .5; }
      .ph.load ha-icon { animation: msnpulse 1.4s ease-in-out infinite; }
      @keyframes msnpulse { 50% { opacity: .15; } }
      .img img { position: relative; opacity: 0; transition: opacity .3s; }
      .img canvas { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: ${this._config.fit === "contain" ? "contain" : "cover"};
                    display: block; opacity: 0; pointer-events: none; }
      .img canvas.ok { opacity: 1; }
      .img img.ok { opacity: 1; }
      .cap { position: absolute; left: 10px; bottom: 10px; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 500;
             background: color-mix(in srgb, var(--card-background-color, #fff) 85%, transparent); color: var(--primary-text-color); pointer-events: none; }
    </style><ha-card><div class="img"><div class="ph load"><ha-icon icon="mdi:map-outline"></ha-icon><span>${esc(this._name(s))}</span></div>
      ${pic ? `<img src="${pic}" alt=""><canvas></canvas>` : ""}${titleHtml}${legendHtml}${chips}${zoomHtml}</div></ha-card>`;
    this.shadowRoot.querySelectorAll(".zoom button").forEach((el) => el.addEventListener("click", (ev) => {
      ev.stopPropagation();
      const value = clamp((zoom || 8) + Number(el.dataset.z), 3, 11);
      this._hass.callService("number", "set_value", { entity_id: zoomId, value });
    }));
    this.shadowRoot.querySelectorAll(".chip").forEach((el) => el.addEventListener("click", (ev) => {
      ev.stopPropagation();
      this._hass.callService("select", "select_option", { entity_id: selId, option: el.dataset.o });
    }));
    const img = this.shadowRoot.querySelector(".img img");
    if (img) {
      let tries = 0;
      img.addEventListener("load", () => {
        img.classList.add("ok"); this.shadowRoot.querySelector(".ph").style.display = "none";
        this._initPlayer(img.currentSrc || img.src, s).then((ok) => {
          if (ok) { clearInterval(this._playTimer); img.style.visibility = "hidden"; }
          else this._startPlayhead(s);
        });
      });
      img.addEventListener("error", () => {
        // the map may still be rendering on the server – retry a few times
        if (tries++ < 6) setTimeout(() => { if (img.isConnected) img.src = `${pic}&r=${tries}`; }, 4000);
        else this.shadowRoot.querySelector(".ph").classList.remove("load");
      });
    }
    this.shadowRoot.querySelector(".img").addEventListener("click", () => {
      const ev = new Event("hass-more-info", { bubbles: true, composed: true });
      ev.detail = { entityId: this._config.entity };
      this.dispatchEvent(ev);
    });
    const lgdEl = this.shadowRoot.querySelector(".lgd");
    if (lgdEl) lgdEl.addEventListener("click", (ev) => {
      ev.stopPropagation();
      this._legendCollapsed = !this._legendCollapsed;
      this._sig = ""; this._render();
    });

  }
}

/* ----------------------------------------------------------------------- */
// Home Assistant sets <html lang> to the user's language; fall back to the browser language.
const UI_DE = (document.documentElement.lang || navigator.language || "").toLowerCase().startsWith("de");
const CARDS = UI_DE ? [
  ["msn-weather-tile-card", MsnWeatherTileCard, "MSN Wetter – Kachel", "Eine einzelne Wetterdetail-Kachel (Temperatur, Wind, UV …) – frei platzierbar"],
  ["msn-weather-details-card", MsnWeatherDetailsCard, "MSN Wetter – Wetterdetails", "Alle Wetterdetail-Kacheln wie auf msn.com"],
  ["msn-weather-hourly-card", MsnWeatherHourlyCard, "MSN Wetter – Stündlich", "Tageskarten und stündliches Diagramm mit Reitern"],
  ["msn-weather-life-card", MsnWeatherLifeCard, "MSN Wetter – Leben", "Gesundheit und Sicherheit / Aktivitäten mit Stundenverlauf"],
  ["msn-weather-life-tile-card", MsnWeatherLifeTileCard, "MSN Wetter – Leben-Kachel", "Ein einzelner Index (Regenschirm, Radfahren, Fahrsicherheit …) als eigene Kachel mit Stundenverlauf"],
  ["msn-weather-rain-card", MsnWeatherRainCard, "MSN Wetter – Regen", "Wann der Regen beginnt, bis wann er dauert und wie viel fällt"],
  ["msn-weather-rain-chart-card", MsnWeatherRainChartCard, "MSN Wetter – Regenmengen", "Niederschlagsmenge pro Stunde als Balken mit Uhrzeit"],
  ["msn-weather-alerts-card", MsnWeatherAlertsCard, "MSN Wetter – Wetterwarnungen", "Aktive und kommende Wetterwarnungen mit Zeitraum und Sicherheitshinweisen"],
  ["msn-weather-nowcast-card", MsnWeatherNowcastCard, "MSN Wetter – Niederschlag 2 Std.", "Minutengenaue Niederschlagsvorhersage: wann der Regen beginnt und aufhört"],
  ["msn-weather-monthly-card", MsnWeatherMonthlyCard, "MSN Wetter – Monatsvorhersage", "Kalender mit 30-Tage-Vorhersage, Klima-Durchschnitt und Rekorden"],
  ["msn-weather-map-card", MsnWeatherMapCard, "MSN Wetter – Wetterkarte", "Animierte Wetterkarte mit korrektem Seitenverhältnis und optionalem Vorhersage-Regler"],
] : [
  ["msn-weather-tile-card", MsnWeatherTileCard, "MSN Weather – Tile", "A single weather detail tile (temperature, wind, UV …) – place it anywhere"],
  ["msn-weather-details-card", MsnWeatherDetailsCard, "MSN Weather – Weather details", "All weather detail tiles like on msn.com"],
  ["msn-weather-hourly-card", MsnWeatherHourlyCard, "MSN Weather – Hourly", "Day cards and hourly chart with tabs"],
  ["msn-weather-life-card", MsnWeatherLifeCard, "MSN Weather – Life", "Health and safety / activities with hourly outlook"],
  ["msn-weather-life-tile-card", MsnWeatherLifeTileCard, "MSN Weather – Life tile", "A single index (umbrella, cycling, driving …) as its own tile with hourly outlook"],
  ["msn-weather-rain-card", MsnWeatherRainCard, "MSN Weather – Rain", "When rain starts, until when it lasts and how much falls"],
  ["msn-weather-rain-chart-card", MsnWeatherRainChartCard, "MSN Weather – Rain amounts", "Precipitation per hour as bars with the time below"],
  ["msn-weather-alerts-card", MsnWeatherAlertsCard, "MSN Weather – Weather alerts", "Active and upcoming weather warnings with period and safety advice"],
  ["msn-weather-nowcast-card", MsnWeatherNowcastCard, "MSN Weather – Precipitation 2 h", "Minute-by-minute precipitation: when rain starts and stops"],
  ["msn-weather-monthly-card", MsnWeatherMonthlyCard, "MSN Weather – Monthly forecast", "Calendar with ~30 day forecast, climate normals and records"],
  ["msn-weather-map-card", MsnWeatherMapCard, "MSN Weather – Weather map", "Animated weather map with correct aspect ratio and optional forecast slider"],
];
window.customCards = window.customCards || [];
const FIELD_LABELS = {
  de: { entity: "Entität", tile: "Kachel", tiles: "Kacheln", appearance: "Darstellung", title: "Titel", hours: "Stunden",
        show_days: "Tageskarten anzeigen", show_chart: "Stunden-Diagramm anzeigen", tabs: "Reiter", mode: "Bereich", days: "Tage", show_zoom: "Zoom-Knöpfe anzeigen (gemeinsamer Zoom)", show_legend: "Legende anzeigen (antippen zum Einklappen)", zoom: "Fester Zoom dieser Karte (3 = Kontinent, 11 = lokal)", fit: "Bildanpassung", hide_when_empty: "Ausblenden, wenn keine Warnung", index: "Index" },
  en: { entity: "Entity", tile: "Tile", tiles: "Tiles", appearance: "Appearance", title: "Title", hours: "Hours",
        show_days: "Show day cards", show_chart: "Show hourly chart", tabs: "Tabs", mode: "Section", days: "Days", show_zoom: "Show zoom buttons (shared zoom)", show_legend: "Show legend (tap to collapse)", zoom: "Fixed zoom of this map (3 = continent, 11 = local)", fit: "Image fit", hide_when_empty: "Hide when there is no warning", index: "Index" },
};
const APPEARANCE_FIELD = { name: "appearance", selector: { select: { mode: "dropdown", options: [
  { value: "msn", label: UI_DE ? "MSN (wie msn.com)" : "MSN (like msn.com)" },
  { value: "ha", label: "Home Assistant" },
] } } };
for (const [, cls] of CARDS) {
  const orig = cls.getConfigForm;
  if (orig && !orig._msnWrapped) {
    const wrapped = function () {
      const f = orig.call(cls);
      return { ...f, schema: [...f.schema, APPEARANCE_FIELD], computeLabel: (field) => (FIELD_LABELS[UI_DE ? "de" : "en"][field.name] || field.name) };
    };
    wrapped._msnWrapped = true;
    cls.getConfigForm = wrapped;
  }
}
for (const [type, cls, name, description] of CARDS) {
  if (!customElements.get(type)) customElements.define(type, cls);
  if (!window.customCards.find((c) => c.type === type)) window.customCards.push({ type, name, description, preview: true, documentationURL: "https://github.com/42bios/ha-msn-weather" });
}
/* ----------------------------------------------------------------------- */
/* Dashboard strategies – a complete weather view from all cards              */
/*   views:      - strategy: { type: custom:msn-weather }                     */
/*   dashboard:  strategy: { type: custom:msn-weather }  (one view per entry) */
/* options: entity, appearance (msn | ha), maps (bool), language, life (tiles | cards) */
/* ----------------------------------------------------------------------- */
const MAP_ORDER = ["radar", "precipitation", "temperature", "wind", "clouds", "satellite", "alerts", "lightning",
  "winter", "tropical_cyclones", "humidity", "visibility", "pressure", "dew_point", "air_quality", "pollen"];

function msnWeatherView(hass, config, weatherId) {
  const de = (config.language || hass.language || "").startsWith("de");
  const lc = lang({ language: config.language || hass.language });
  const ents = resolveEntities(hass, weatherId);
  const appearance = config.appearance || "ha";
  const base = { entity: weatherId, appearance, ...(config.language ? { language: config.language } : {}) };
  const heading = (text, icon) => ({ type: "heading", heading: text, icon });
  const sections = [
    { type: "grid", column_span: 4, cards: [{
      type: "custom:msn-weather-alerts-card", ...base, hide_when_empty: true, grid_options: { columns: "full" },
      ...(ents.alerts ? { visibility: [{ condition: "numeric_state", entity: ents.alerts, above: 0 }] } : {}),
    }] },
    { type: "grid", column_span: 4, cards: [{ type: "custom:msn-weather-hourly-card", ...base, grid_options: { columns: "full" } }] },
    { type: "grid", column_span: 4, cards: [
      { type: "custom:msn-weather-rain-card", ...base, grid_options: { columns: 12, rows: appearance === "ha" ? 2 : 3 } },
      { type: "custom:msn-weather-rain-chart-card", ...base, grid_options: { columns: "full" } },
      { type: "custom:msn-weather-nowcast-card", ...base, grid_options: { columns: "full" } },
    ] },
    { type: "grid", column_span: 4, cards: [
      heading(pick(lc, { de: "Wetterdetails", en: "Weather details", it: "Dettagli meteo", fr: "Détails météo", es: "Detalles del tiempo", nl: "Weerdetails" }), "mdi:view-dashboard-outline"),
      ...ALL_TILES.map((tile) => ({ type: "custom:msn-weather-tile-card", ...base, tile, grid_options: { columns: 6, rows: appearance === "ha" ? 2 : 3 } })),
    ] },
    ...(config.life === "cards" ? [
      { type: "grid", column_span: 2, cards: [{ type: "custom:msn-weather-life-card", ...base, mode: "health", grid_options: { columns: "full" } }] },
      { type: "grid", column_span: 2, cards: [{ type: "custom:msn-weather-life-card", ...base, mode: "activities", grid_options: { columns: "full" } }] },
    ] : [["health", pick(lc, { de: "Gesundheit und Sicherheit", en: "Health and safety", it: "Salute e sicurezza", fr: "Santé et sécurité", es: "Salud y seguridad", nl: "Gezondheid en veiligheid" }), "mdi:shield-sun-outline"], ["activities", pick(lc, { de: "Aktivitäten", en: "Activities", it: "Attività", fr: "Activités", es: "Actividades", nl: "Activiteiten" }), "mdi:run"]].map(([mode, text, icon]) => ({
      type: "grid", column_span: 4, cards: [
        heading(text, icon),
        ...LIFE_ITEMS[mode].filter(([k]) => ents[k] && !(mode === "activities" && k === "life_walking"))
          .map(([k]) => ({ type: "custom:msn-weather-life-tile-card", ...base, index: k.replace(/^life_/, ""), grid_options: { columns: 6, rows: appearance === "ha" ? 2 : 3 } })),
      ],
    })).filter((section) => section.cards.length > 1)),
    { type: "grid", column_span: 4, cards: [{ type: "custom:msn-weather-monthly-card", ...base, grid_options: { columns: "full" } }] },
  ];
  if (config.maps !== false) {
    const maps = MAP_ORDER.map((k) => ents[`map_${k}`]).filter((id) => id && hass.states[id]);
    if (maps.length) {
      sections.push({ type: "grid", column_span: 4, cards: [
        heading(pick(lc, { de: "Wetterkarten", en: "Weather maps", it: "Mappe meteo", fr: "Cartes météo", es: "Mapas del tiempo", nl: "Weerkaarten" }), "mdi:map-outline"),
        ...(ents.map_forecast_hours ? [{ type: "tile", entity: ents.map_forecast_hours, features: [{ type: "numeric-input", style: "slider" }], grid_options: { columns: 12 } }] : []),
        ...maps.map((id) => ({ type: "custom:msn-weather-map-card", entity: id, appearance, ...(config.language ? { language: config.language } : {}), grid_options: { columns: 12 } })),
      ] });
    }
  }
  const name = hass.states[weatherId]?.attributes.friendly_name || "MSN Weather";
  return { title: config.title || name, path: config.path, icon: "mdi:weather-partly-cloudy", type: "sections", max_columns: 4, sections };
}

const msnWeatherEntities = (hass) =>
  Object.values(hass.entities || {}).filter((e) => e.platform === "msn_weather" && e.entity_id.startsWith("weather.")).map((e) => e.entity_id);

class MsnWeatherViewStrategy extends HTMLElement {
  static async generate(config, hass) {
    const weatherId = config.entity || msnWeatherEntities(hass)[0];
    if (!weatherId) {
      return { cards: [{ type: "markdown", content: pick(lang(hass), { de: "Keine MSN-Wetter-Integration gefunden.", en: "No MSN Weather integration found.", it: "Nessuna integrazione MSN Meteo trovata.", fr: "Aucune intégration MSN Météo trouvée.", es: "No se encontró ninguna integración de MSN El Tiempo.", nl: "Geen MSN Weer-integratie gevonden." }) }] };
    }
    return msnWeatherView(hass, config, weatherId);
  }
}

class MsnWeatherDashboardStrategy extends HTMLElement {
  static async generate(config, hass) {
    const ids = config.entity ? [config.entity] : msnWeatherEntities(hass);
    return {
      views: ids.length
        ? ids.map((id) => ({ strategy: { type: "custom:msn-weather", ...config, entity: id }, title: hass.states[id]?.attributes.friendly_name, path: id.split(".")[1] }))
        : [{ strategy: { type: "custom:msn-weather" } }],
    };
  }
}

if (!customElements.get("ll-strategy-view-msn-weather")) customElements.define("ll-strategy-view-msn-weather", MsnWeatherViewStrategy);
if (!customElements.get("ll-strategy-dashboard-msn-weather")) customElements.define("ll-strategy-dashboard-msn-weather", MsnWeatherDashboardStrategy);

console.info(`%c MSN WEATHER CARDS %c v${CARD_VERSION} `, "color:#fff;background:#0078d4;font-weight:700;border-radius:3px 0 0 3px;padding:2px 4px", "color:#0078d4;background:#dbeafe;font-weight:700;border-radius:0 3px 3px 0;padding:2px 4px");
