const assert = require("node:assert/strict");
const test = require("node:test");
const { createSiteAnalytics, config } = require("../assets/site-analytics.js");

class MockElement {
  constructor(tagName, document) {
    this.tagName = tagName.toUpperCase();
    this.document = document;
    this.children = [];
    this.dataset = {};
    this.attributes = {};
    this.listeners = new Map();
    this.hidden = false;
    this.className = "";
    this.textContent = "";
  }

  appendChild(child) {
    child.parentElement = this;
    this.children.push(child);
    return child;
  }

  addEventListener(name, callback) {
    const callbacks = this.listeners.get(name) || [];
    callbacks.push(callback);
    this.listeners.set(name, callbacks);
  }

  setAttribute(name, value) {
    this.attributes[name] = String(value);
    if (name.startsWith("data-")) {
      const key = name.slice(5).replace(/-([a-z])/g, (_match, letter) => letter.toUpperCase());
      this.dataset[key] = String(value);
    }
  }

  getAttribute(name) {
    return this.attributes[name] || null;
  }

  querySelector(selector) {
    if (selector !== "[data-consent-choice]") return null;
    return findElement(this, (element) => Boolean(element.dataset.consentChoice));
  }

  closest(selector) {
    if (selector === "a[data-ga4-placement]" && this.tagName === "A" && this.dataset.ga4Placement) {
      return this;
    }
    return this.parentElement ? this.parentElement.closest(selector) : null;
  }

  focus() {
    this.focused = true;
  }

  click() {
    for (const callback of this.listeners.get("click") || []) {
      callback({ target: this, currentTarget: this });
    }
  }
}

function findElement(root, predicate) {
  for (const child of root.children) {
    if (predicate(child)) return child;
    const nested = findElement(child, predicate);
    if (nested) return nested;
  }
  return null;
}

class MockDocument {
  constructor({ language = "en", referrer = "" } = {}) {
    this.documentElement = { lang: language };
    this.referrer = referrer;
    this.listeners = new Map();
    this.created = [];
    this.footerLinks = this.createElement("nav");
    this.head = this.createElement("head");
    this.body = this.createElement("body");
    this.cookieWrites = [];
    this._cookie = "_ga=old; _ga_" + config.measurementId.slice(2) + "=old; other=value";
    Object.defineProperty(this, "cookie", {
      get: () => this._cookie,
      set: (value) => this.cookieWrites.push(String(value))
    });
  }

  createElement(tagName) {
    const element = new MockElement(tagName, this);
    this.created.push(element);
    return element;
  }

  querySelector(selector) {
    return selector === ".site-footer .footer-links" ? this.footerLinks : null;
  }

  addEventListener(name, callback) {
    const callbacks = this.listeners.get(name) || [];
    callbacks.push(callback);
    this.listeners.set(name, callbacks);
  }

  dispatch(name, event) {
    for (const callback of this.listeners.get(name) || []) callback(event);
  }
}

function makeBrowser({
  hostname = "hugehard.app",
  origin = "https://hugehard.app",
  pathname = "/apps/this-pic-can-change/",
  language = "en",
  referrer = "https://search.example/results?q=private#fragment",
  storedConsent = null
} = {}) {
  const document = new MockDocument({ language, referrer });
  const storage = new Map();
  if (storedConsent) storage.set("hugehard.siteAnalyticsConsent.v1", storedConsent);
  const window = {
    document,
    location: { hostname, origin, pathname, search: "?campaign=private", hash: "#fragment" },
    localStorage: {
      getItem(key) { return storage.has(key) ? storage.get(key) : null; },
      setItem(key, value) { storage.set(key, String(value)); }
    }
  };
  return { window, document, storage };
}

function choiceButton(document, value) {
  return document.created.find((element) => element.dataset.consentChoice === value);
}

function clickAnchor(document, { href = "https://testflight.apple.com/join/GK8ht2vv", placement = "home_hero" } = {}) {
  const anchor = document.createElement("a");
  anchor.href = href;
  anchor.dataset.ga4Placement = placement;
  document.dispatch("click", { target: anchor });
}

function commands(window) {
  return (window.dataLayer || []).map((args) => Array.from(args));
}

function events(window, name) {
  return commands(window).filter((command) => command[0] === "event" && command[1] === name);
}

test("analytics waits for consent, sanitizes page context, and sends one TestFlight event", () => {
  const { window, document, storage } = makeBrowser();
  const scriptLoads = [];
  const controller = createSiteAnalytics(window, config, {
    loadGoogleScript(id, onLoad) { scriptLoads.push({ id, onLoad }); }
  });

  controller.init();
  clickAnchor(document);
  assert.equal(scriptLoads.length, 0, "unknown consent must not load Google or queue a click");
  assert.equal(window.dataLayer, undefined, "no gtag stub should be initialized before consent");

  choiceButton(document, "granted").click();
  assert.equal(scriptLoads.length, 1);
  assert.equal(scriptLoads[0].id, config.measurementId);
  assert.equal(events(window, "page_view").length, 0, "page view waits until the mocked tag is ready");
  clickAnchor(document);
  scriptLoads[0].onLoad();

  const pageViews = events(window, "page_view");
  assert.equal(pageViews.length, 1);
  assert.deepEqual(Object.keys(pageViews[0][2]).sort(), ["language", "page_location", "page_path", "page_referrer"]);
  assert.equal(pageViews[0][2].page_location, "https://hugehard.app/apps/this-pic-can-change/");
  assert.equal(pageViews[0][2].page_referrer, "https://search.example");
  assert.equal(pageViews[0][2].page_path, "/apps/this-pic-can-change/");
  assert.equal(pageViews[0][2].language, "en");

  const clickEvents = events(window, "testflight_click");
  assert.equal(clickEvents.length, 1, "the pre-consent click must not be replayed");
  assert.deepEqual(clickEvents[0][2], {
    placement: "home_hero",
    page_path: "/apps/this-pic-can-change/",
    language: "en"
  });

  const configCommand = commands(window).find((command) => command[0] === "config");
  assert.equal(configCommand[1], config.measurementId);
  assert.equal(configCommand[2].send_page_view, false);
  assert.equal(configCommand[2].cookie_domain, "none");
  assert.equal(configCommand[2].cookie_expires, 0);
  assert.equal(configCommand[2].allow_google_signals, false);
  assert.equal(configCommand[2].allow_ad_personalization_signals, false);
  assert.equal(storage.get("hugehard.siteAnalyticsConsent.v1"), "granted");

  clickAnchor(document, { href: "https://example.com/join/GK8ht2vv", placement: "home_hero" });
  clickAnchor(document, { placement: "unapproved_placement" });
  clickAnchor(document, { href: "mailto:person@example.com", placement: "home_hero" });
  assert.equal(events(window, "testflight_click").length, 1, "only the exact invitation and approved placement are counted");
});

test("rejection withdraws consent, drops pending events, and clears this property's cookies", () => {
  const { window, document, storage } = makeBrowser({ language: "zh-CN" });
  const scriptLoads = [];
  const controller = createSiteAnalytics(window, config, {
    loadGoogleScript(id, onLoad) { scriptLoads.push({ id, onLoad }); }
  });

  controller.init();
  choiceButton(document, "granted").click();
  clickAnchor(document, { placement: "product_hero" });
  assert.equal(events(window, "page_view").length, 0);
  assert.equal(events(window, "testflight_click").length, 0);

  document.created.find((element) => element.dataset.analyticsSettings === "true").click();
  choiceButton(document, "denied").click();
  scriptLoads[0].onLoad();

  assert.equal(events(window, "page_view").length, 0, "revoked pending page view must not be sent later");
  assert.equal(events(window, "testflight_click").length, 0, "revoked pending click must not be sent later");
  assert.equal(storage.get("hugehard.siteAnalyticsConsent.v1"), "denied");
  assert.equal(window["ga-disable-" + config.measurementId], true);
  assert.ok(document.cookieWrites.includes("_ga=; Max-Age=0; Path=/; SameSite=Lax; Secure"));
  const suffix = config.measurementId.replace(/^G-/, "");
  assert.ok(document.cookieWrites.includes(`_ga_${suffix}=; Max-Age=0; Path=/; SameSite=Lax; Secure`));

  clickAnchor(document);
  assert.equal(events(window, "testflight_click").length, 0);
});

test("withdrawal and re-consent on one page does not duplicate the page view", () => {
  const { window, document } = makeBrowser({
    pathname: "/guides/video-to-live-photo/",
    language: "zh-CN",
    referrer: "https://hugehard.app/guides/?utm_source=private#top"
  });
  const scriptLoads = [];
  const controller = createSiteAnalytics(window, config, {
    loadGoogleScript(id, onLoad) { scriptLoads.push({ id, onLoad }); }
  });

  controller.init();
  choiceButton(document, "granted").click();
  scriptLoads[0].onLoad();
  assert.equal(events(window, "page_view").length, 1);
  assert.equal(events(window, "page_view")[0][2].page_referrer, "https://hugehard.app/guides/");

  document.created.find((element) => element.dataset.analyticsSettings === "true").click();
  choiceButton(document, "denied").click();
  document.created.find((element) => element.dataset.analyticsSettings === "true").click();
  choiceButton(document, "granted").click();

  assert.equal(scriptLoads.length, 1);
  assert.equal(events(window, "page_view").length, 1);
  clickAnchor(document, { placement: "live_photo_guide" });
  assert.equal(events(window, "testflight_click").length, 1);
});

test("the tracker is inert on tools subdomains and when no measurement ID is configured", () => {
  const onTools = makeBrowser({ hostname: "tools.hugehard.app", origin: "https://tools.hugehard.app" });
  let loads = 0;
  createSiteAnalytics(onTools.window, config, { loadGoogleScript() { loads += 1; } }).init();
  assert.equal(loads, 0);
  assert.equal(onTools.window.dataLayer, undefined);
  assert.equal(onTools.document.created.some((element) => element.className === "site-analytics-consent"), false);

  const withoutId = makeBrowser();
  createSiteAnalytics(withoutId.window, { measurementId: "" }, { loadGoogleScript() { loads += 1; } }).init();
  assert.equal(loads, 0);
  assert.equal(withoutId.window.dataLayer, undefined);
});
