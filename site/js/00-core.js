// 00-core: tiny DOM helpers shared by every part (site/CONTRACT.md, "JS parts").
// Nodes are built with createElement and textContent only, never from HTML strings, so the
// page works under the site's CSP and would under Trusted Types. Nothing here stores data.
const Core = (() => {
  // Attribute names el() refuses: event handlers and inline styles are blocked by the CSP.
  const REFUSED = /^(on|style$)/i;

  // First element matching `selector` inside `root` (default: the document), or null.
  const $ = (selector, root = document) => root.querySelector(selector);

  // Every element matching `selector` inside `root`, as an array.
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

  // Append nodes or strings (as text) to `parent`, skipping null and false.
  const append = (parent, ...children) => {
    for (const child of children.flat()) {
      if (child === null || child === undefined || child === false) continue;
      parent.append(child instanceof Node ? child : document.createTextNode(String(child)));
    }
    return parent;
  };

  // Create an element. `props` sets attributes; `class` takes a string or an array, `text`
  // sets textContent, `dataset` an object of data-* values, and `hidden`/boolean attributes
  // take true or false. `children` are nodes or strings (added as text nodes).
  const el = (tag, props = {}, ...children) => {
    const node = document.createElement(tag);
    for (const [name, value] of Object.entries(props)) {
      if (value === null || value === undefined || value === false) continue;
      if (REFUSED.test(name)) throw new Error(`Core.el: attribute ${name} is not allowed`);
      if (name === 'text') {
        node.textContent = String(value);
      } else if (name === 'class') {
        node.className = Array.isArray(value) ? value.filter(Boolean).join(' ') : String(value);
      } else if (name === 'dataset') {
        for (const [key, item] of Object.entries(value)) node.dataset[key] = String(item);
      } else {
        node.setAttribute(name, value === true ? '' : String(value));
      }
    }
    append(node, ...children);
    return node;
  };

  // Set textContent only when it changes, so unchanged rows cause no layout work.
  const text = (node, value) => {
    const next = String(value);
    if (node.textContent !== next) node.textContent = next;
    return node;
  };

  // Remove every child of `node`.
  const clear = (node) => {
    node.replaceChildren();
    return node;
  };

  // Show or hide with the hidden attribute (never inline styles).
  const setHidden = (node, hidden) => {
    if (node.hidden !== Boolean(hidden)) node.hidden = Boolean(hidden);
    return node;
  };

  // Listen on `target`. With a `selector`, delegate: `handler(event, matched)` runs when the
  // event comes from inside an element matching it. Returns a function that stops listening.
  const on = (target, type, selector, handler, options) => {
    if (typeof selector === 'function') {
      target.addEventListener(type, selector, handler);
      return () => target.removeEventListener(type, selector, handler);
    }
    const listener = (event) => {
      const matched = event.target instanceof Element ? event.target.closest(selector) : null;
      if (matched && target.contains(matched)) handler(event, matched);
    };
    target.addEventListener(type, listener, options);
    return () => target.removeEventListener(type, listener, options);
  };

  // Call `fn` once `ms` after the last call; `.cancel()` drops a pending call.
  const debounce = (fn, ms) => {
    let timer = 0;
    const debounced = (...args) => {
      clearTimeout(timer);
      timer = setTimeout(() => fn(...args), ms);
    };
    debounced.cancel = () => clearTimeout(timer);
    return debounced;
  };

  // Run `fn` when the browser is idle (or after `timeout` ms), falling back to a timer.
  const idle = (fn, timeout = 500) => {
    if (typeof requestIdleCallback === 'function') return requestIdleCallback(fn, { timeout });
    return setTimeout(() => fn({ didTimeout: true, timeRemaining: () => 0 }), 1);
  };

  // Resolve after the next two animation frames: the change has been painted.
  const painted = () =>
    new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));

  // "312 KB" style sizes, in decimal units like the budgets.
  const formatBytes = (bytes) => {
    if (bytes < 1000) return `${bytes} B`;
    if (bytes < 1000000) return `${Math.round(bytes / 1000)} KB`;
    return `${(bytes / 1000000).toFixed(1)} MB`;
  };

  // "1,234" style counts.
  const formatCount = (count) => count.toLocaleString('en-US');

  // "1 font" / "3 fonts".
  const plural = (count, one, many) => `${formatCount(count)} ${count === 1 ? one : many}`;

  return Object.freeze({
    $, $$, el, append, text, clear, setHidden, on, debounce, idle, painted,
    formatBytes, formatCount, plural,
  });
})();
