// Loads the MSN Weather cards. The integration passes a hash of the cards file as "v", so the
// browser caches the cards until an update changes them.
const version = new URL(import.meta.url).searchParams.get("v") || Date.now();
import(new URL("./msn-weather-cards.js?v=" + version, import.meta.url).href);
