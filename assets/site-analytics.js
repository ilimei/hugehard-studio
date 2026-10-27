(function exposeSiteAnalytics(root, createSiteAnalytics) {
  const config = Object.freeze({ measurementId: "G-Q5PVS3N78G" });

  if (typeof module === "object" && module.exports) {
    module.exports = { createSiteAnalytics, config };
    return;
  }

  if (root && root.document) {
    createSiteAnalytics(root, config).init();
  }
})(typeof window === "undefined" ? null : window, function createSiteAnalytics(windowObject, config, dependencies = {}) {
  const CONSENT_KEY = "hugehard.siteAnalyticsConsent.v1";
  const ALLOWED_HOST = "hugehard.app";
  const TESTFLIGHT_ORIGIN = "https://testflight.apple.com";
  const TESTFLIGHT_PATH = "/join/GK8ht2vv";
  const ALLOWED_PLACEMENTS = new Set(["home_hero", "product_hero", "live_photo_guide"]);
  const DENIED_CONSENT = Object.freeze({
    analytics_storage: "denied",
    ad_storage: "denied",
    ad_user_data: "denied",
    ad_personalization: "denied"
  });
  const GRANTED_ANALYTICS_CONSENT = Object.freeze({
    analytics_storage: "granted",
    ad_storage: "denied",
    ad_user_data: "denied",
    ad_personalization: "denied"
  });

  const documentObject = windowObject.document;
  const measurementId = String(config && config.measurementId ? config.measurementId : "").trim();
  const enabled = windowObject.location.hostname === ALLOWED_HOST && /^G-[A-Z0-9]+$/i.test(measurementId);
  let consent = readConsent();
  let isActive = false;
  let isInitialized = false;
  let isTagLoaded = false;
  let hasSentPageView = false;
  const pendingEvents = [];
  let consentBanner = null;

  function readConsent() {
    try {
      const value = windowObject.localStorage.getItem(CONSENT_KEY);
      return value === "granted" || value === "denied" ? value : null;
    } catch (_error) {
      return null;
    }
  }

  function writeConsent(value) {
    try {
      windowObject.localStorage.setItem(CONSENT_KEY, value);
    } catch (_error) {
      // Keep the choice for this page even when browser storage is unavailable.
    }
  }

  function language() {
    const value = documentObject.documentElement.lang;
    return value === "en" ? "en" : "zh-CN";
  }

  function safeReferrer() {
    const value = documentObject.referrer;
    if (!value) return "";

    try {
      const parsed = new URL(value);
      if (parsed.protocol !== "http:" && parsed.protocol !== "https:") return "";
      if (parsed.origin === windowObject.location.origin) {
        return parsed.origin + parsed.pathname;
      }
      return parsed.origin;
    } catch (_error) {
      return "";
    }
  }

  function pageContext() {
    const pagePath = windowObject.location.pathname || "/";
    return {
      page_location: windowObject.location.origin + pagePath,
      page_referrer: safeReferrer(),
      page_path: pagePath,
      language: language()
    };
  }

  function createTagScript(_measurementId, onLoad) {
    const script = documentObject.createElement("script");
    script.async = true;
    script.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(measurementId);
    script.dataset.siteAnalyticsTag = "true";
    script.onload = onLoad;
    (documentObject.head || documentObject.body).appendChild(script);
  }

  function handleTagLoaded() {
    isTagLoaded = true;
    if (!isActive || consent !== "granted") {
      pendingEvents.length = 0;
      return;
    }

    const queued = pendingEvents.splice(0);
    for (const event of queued) {
      dispatchEvent(event.name, event.parameters);
    }
  }

  function ensureGoogleTag() {
    if (isInitialized) {
      windowObject["ga-disable-" + measurementId] = false;
      windowObject.gtag("consent", "update", GRANTED_ANALYTICS_CONSENT);
      return;
    }

    windowObject.dataLayer = windowObject.dataLayer || [];
    windowObject.gtag = function gtag() {
      windowObject.dataLayer.push(arguments);
    };

    windowObject.gtag("consent", "default", DENIED_CONSENT);
    windowObject.gtag("js", new Date());
    windowObject.gtag("consent", "update", GRANTED_ANALYTICS_CONSENT);
    windowObject["ga-disable-" + measurementId] = false;
    windowObject.gtag("config", measurementId, {
      send_page_view: false,
      page_location: pageContext().page_location,
      page_referrer: pageContext().page_referrer,
      page_title: windowObject.location.pathname || "/",
      allow_google_signals: false,
      allow_ad_personalization_signals: false,
      cookie_domain: "none",
      cookie_path: "/",
      cookie_expires: 0
    });

    isInitialized = true;
    const loadScript = dependencies.loadGoogleScript || createTagScript;
    loadScript(measurementId, handleTagLoaded);
  }

  function dispatchEvent(name, parameters) {
    if (typeof dependencies.sendEvent === "function") {
      dependencies.sendEvent(name, parameters);
    } else if (typeof windowObject.gtag === "function") {
      windowObject.gtag("event", name, parameters);
    }
    if (name === "page_view") hasSentPageView = true;
  }

  function sendEvent(name, parameters) {
    if (!isActive || consent !== "granted") return;
    if (!isTagLoaded) {
      pendingEvents.push({ name, parameters });
      return;
    }
    dispatchEvent(name, parameters);
  }

  function sendPageViewOnce() {
    if (hasSentPageView || pendingEvents.some((event) => event.name === "page_view") || !isActive) return;
    sendEvent("page_view", pageContext());
  }

  function activateAnalytics() {
    if (!enabled || consent !== "granted") return;
    isActive = true;
    ensureGoogleTag();
    sendPageViewOnce();
  }

  function clearPropertyCookies() {
    const cookieSuffix = measurementId.replace(/^G-/i, "");
    const cookieNames = ["_ga", "_ga_" + cookieSuffix];
    for (const name of cookieNames) {
      documentObject.cookie = name + "=; Max-Age=0; Path=/; SameSite=Lax; Secure";
    }
  }

  function deactivateAnalytics() {
    isActive = false;
    windowObject["ga-disable-" + measurementId] = true;
    const pendingPageView = pendingEvents.some((event) => event.name === "page_view");
    pendingEvents.length = 0;
    if (pendingPageView) hasSentPageView = false;
    if (isInitialized && typeof windowObject.gtag === "function") {
      windowObject.gtag("consent", "update", DENIED_CONSENT);
    }
    clearPropertyCookies();
  }

  function setConsent(value) {
    if (value !== "granted" && value !== "denied") return;
    consent = value;
    writeConsent(value);
    if (consentBanner) consentBanner.hidden = true;
    if (value === "granted") {
      activateAnalytics();
    } else {
      deactivateAnalytics();
    }
  }

  function makeButton(label, className, onClick) {
    const button = documentObject.createElement("button");
    button.type = "button";
    button.className = className;
    button.textContent = label;
    button.addEventListener("click", onClick);
    return button;
  }

  function addConsentInterface() {
    const isEnglish = language() === "en";
    const footerLinks = documentObject.querySelector(".site-footer .footer-links");

    if (footerLinks) {
      const settingsButton = makeButton(
        isEnglish ? "Analytics settings" : "统计设置",
        "site-analytics-settings",
        function openConsentSettings() {
          if (consentBanner) {
            consentBanner.hidden = false;
            const firstChoice = consentBanner.querySelector("[data-consent-choice]");
            if (firstChoice) firstChoice.focus();
          }
        }
      );
      settingsButton.setAttribute("data-analytics-settings", "true");
      footerLinks.appendChild(settingsButton);
    }

    consentBanner = documentObject.createElement("section");
    consentBanner.className = "site-analytics-consent";
    consentBanner.setAttribute("role", "region");
    consentBanner.setAttribute("aria-labelledby", "site-analytics-title");
    consentBanner.hidden = consent !== null;

    const title = documentObject.createElement("h2");
    title.id = "site-analytics-title";
    title.textContent = isEnglish ? "Site analytics" : "网站访问统计";

    const description = documentObject.createElement("p");
    description.textContent = isEnglish
      ? "If you agree, Google Analytics will record page views and clicks on TestFlight join links. It is used for site statistics, not advertising. You can change this choice from the footer at any time."
      : "同意后，Google Analytics 会记录页面访问和 TestFlight 加入链接点击，用于网站统计，不用于广告。你可以随时通过页脚更改选择。";

    const privacyNote = documentObject.createElement("p");
    const privacyLink = documentObject.createElement("a");
    privacyLink.href = isEnglish ? "/en/privacy.html" : "/privacy.html";
    privacyLink.textContent = isEnglish ? "Website privacy" : "网站隐私说明";
    privacyNote.appendChild(privacyLink);

    const actions = documentObject.createElement("div");
    actions.className = "site-analytics-actions";
    actions.appendChild(makeButton(
      isEnglish ? "Allow analytics" : "同意统计",
      "site-analytics-accept",
      function acceptAnalytics() { setConsent("granted"); }
    )).setAttribute("data-consent-choice", "granted");
    actions.appendChild(makeButton(
      isEnglish ? "Reject analytics" : "拒绝统计",
      "site-analytics-reject",
      function rejectAnalytics() { setConsent("denied"); }
    )).setAttribute("data-consent-choice", "denied");

    consentBanner.appendChild(title);
    consentBanner.appendChild(description);
    consentBanner.appendChild(privacyNote);
    consentBanner.appendChild(actions);
    documentObject.body.appendChild(consentBanner);
  }

  function isTestFlightLink(anchor) {
    if (!anchor || typeof anchor.href !== "string") return false;
    try {
      const url = new URL(anchor.href, windowObject.location.origin);
      return url.origin === TESTFLIGHT_ORIGIN && url.pathname === TESTFLIGHT_PATH;
    } catch (_error) {
      return false;
    }
  }

  function handleDocumentClick(event) {
    if (!isActive || consent !== "granted" || !event.target || typeof event.target.closest !== "function") return;
    const anchor = event.target.closest("a[data-ga4-placement]");
    if (!isTestFlightLink(anchor)) return;

    const placement = anchor.dataset && anchor.dataset.ga4Placement;
    if (!ALLOWED_PLACEMENTS.has(placement)) return;

    sendEvent("testflight_click", {
      placement,
      page_path: windowObject.location.pathname || "/",
      language: language()
    });
  }

  function init() {
    if (!enabled) return api;
    addConsentInterface();
    documentObject.addEventListener("click", handleDocumentClick);

    if (consent === "granted") {
      activateAnalytics();
    } else if (consent === "denied") {
      deactivateAnalytics();
    }
    return api;
  }

  const api = Object.freeze({ init, setConsent });
  return api;
});
