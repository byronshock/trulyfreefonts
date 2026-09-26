// Init script for Playwright contexts made by tests/site/conftest.py (guarded_context).
// Playwright runs it before any page script and outside the page's CSP. It records every
// attempt to store data in the browser, and every CSP violation, in window.__tffGuards,
// then calls through, so context.storage_state() sees the same writes. The privacy tests
// require every list to be empty. Property writes such as `localStorage.x = 1` bypass the
// wrappers; the storage_state() check catches those.
(() => {
  if (Object.prototype.hasOwnProperty.call(window, '__tffGuards')) return;
  const rec = {
    violations: [],
    storage: [],
    cookies: [],
    indexedDB: [],
    caches: [],
    serviceWorker: [],
    cookieStore: [],
  };
  Object.defineProperty(window, '__tffGuards', { value: rec, enumerable: false });

  const safe = (fn) => {
    try {
      return fn();
    } catch (error) {
      return `(${error && error.name})`;
    }
  };

  document.addEventListener(
    'securitypolicyviolation',
    (e) => {
      rec.violations.push({
        directive: e.effectiveDirective || e.violatedDirective,
        blocked: String(e.blockedURI),
        source: e.sourceFile,
        line: e.lineNumber,
        sample: e.sample,
      });
    },
    true,
  );

  const wrap = (proto, name, list, describe) => {
    if (!proto || typeof proto[name] !== 'function') return;
    const original = proto[name];
    Object.defineProperty(proto, name, {
      configurable: true,
      writable: true,
      value: function (...args) {
        list.push(safe(() => describe(this, args)));
        return original.apply(this, args);
      },
    });
  };

  const area = (storage) =>
    safe(() => {
      if (storage === window.localStorage) return 'local';
      if (storage === window.sessionStorage) return 'session';
      return 'other';
    });

  for (const op of ['setItem', 'removeItem', 'clear']) {
    wrap(window.Storage && Storage.prototype, op, rec.storage, (self, args) => ({
      op,
      area: area(self),
      key: args.length ? String(args[0]) : null,
    }));
  }

  const cookie = Object.getOwnPropertyDescriptor(Document.prototype, 'cookie');
  if (cookie && cookie.set) {
    Object.defineProperty(Document.prototype, 'cookie', {
      configurable: true,
      enumerable: cookie.enumerable,
      get: cookie.get,
      set(value) {
        rec.cookies.push(String(value).slice(0, 200));
        return cookie.set.call(this, value);
      },
    });
  }

  wrap(window.IDBFactory && IDBFactory.prototype, 'open', rec.indexedDB, (_, args) => ({
    op: 'open',
    name: String(args[0]),
  }));
  wrap(window.IDBFactory && IDBFactory.prototype, 'deleteDatabase', rec.indexedDB, (_, args) => ({
    op: 'deleteDatabase',
    name: String(args[0]),
  }));
  wrap(window.CacheStorage && CacheStorage.prototype, 'open', rec.caches, (_, args) => ({
    name: String(args[0]),
  }));
  wrap(
    window.ServiceWorkerContainer && ServiceWorkerContainer.prototype,
    'register',
    rec.serviceWorker,
    (_, args) => ({ url: String(args[0]) }),
  );
  wrap(window.CookieStore && CookieStore.prototype, 'set', rec.cookieStore, (_, args) => ({
    name: typeof args[0] === 'object' && args[0] ? String(args[0].name) : String(args[0]),
  }));
})();
