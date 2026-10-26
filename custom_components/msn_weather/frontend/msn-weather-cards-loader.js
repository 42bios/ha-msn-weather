// Loads the MSN Weather cards; the timestamp makes sure updates are picked up without a restart.
import(new URL("./msn-weather-cards.js?t=" + Math.floor(Date.now() / 60000), import.meta.url).href);
