const assert = require("node:assert/strict");
const fs = require("node:fs");
const http = require("node:http");
const path = require("node:path");
const test = require("node:test");
const inquiry = require("../assets/form.js");

const FIXTURE = path.join(__dirname, "fixtures", "inquiry");
const SUCCESS_BODY = fs.readFileSync(path.join(FIXTURE, "success.json"), "utf8");
const EXPLICIT_FAILURE_BODY = fs.readFileSync(path.join(FIXTURE, "explicit-failure.json"), "utf8");
const CLIENT_ERROR_BODY = fs.readFileSync(path.join(FIXTURE, "client-error.json"), "utf8");
const SERVER_ERROR_BODY = fs.readFileSync(path.join(FIXTURE, "server-error.json"), "utf8");
const HTML_BODY = fs.readFileSync(path.join(FIXTURE, "html-200.html"), "utf8");

const SAMPLE = {
  company: "架空商事株式会社",
  dept: "企画",
  name: "山田 花",
  email: "hanako.yamada@example.co.jp",
  tel: "03-0000-0000",
  topic: "その他",
  message: "これは試験用の架空の文面です。"
};

function headers(contentType) {
  return {
    get(name) {
      return String(name).toLowerCase() === "content-type" ? contentType : null;
    }
  };
}

function jsonResponse(status, body, contentType) {
  return {
    status: status,
    headers: headers(contentType || "application/json"),
    text() { return Promise.resolve(body); }
  };
}

class El {
  constructor(tag, doc) {
    this.tagName = String(tag || "").toUpperCase();
    this.doc = doc;
    this.children = [];
    this.style = {};
    this.attrs = {};
    this.hidden = false;
    this.disabled = false;
    this.className = "";
    this._id = "";
    this.text = "";
    this.value = "";
    this.tabIndex = 0;
    this.listeners = {};
    this.focused = false;
  }
  get id() { return this._id; }
  set id(value) {
    this._id = value;
    if (this.doc) this.doc.ids[value] = this;
  }
  get textContent() {
    if (this.children.length) return this.children.map((child) => child.textContent).join("");
    return this.text;
  }
  set textContent(value) {
    this.text = value == null ? "" : String(value);
    this.children = [];
  }
  setAttribute(name, value) { this.attrs[name] = String(value); }
  getAttribute(name) { return Object.prototype.hasOwnProperty.call(this.attrs, name) ? this.attrs[name] : null; }
  appendChild(node) { this.children.push(node); return node; }
  replaceChildren() { this.children = []; this.text = ""; }
  addEventListener(type, fn) {
    if (!this.listeners[type]) this.listeners[type] = [];
    this.listeners[type].push(fn);
  }
  focus() { this.focused = true; }
  querySelector(selector) { return walk(this, selector); }
}

class Doc {
  constructor() {
    this.ids = {};
  }
  createElement(tag) { return new El(tag, this); }
  createTextNode(text) {
    const node = new El("#text", this);
    node.text = String(text);
    return node;
  }
  getElementById(id) { return this.ids[id] || null; }
}

function matches(el, selector) {
  const name = selector.match(/^\[name="([^"]+)"\]$/);
  if (name) return el.attrs.name === name[1];
  const button = selector.match(/^button\[type="([^"]+)"\]$/);
  if (button) return el.tagName === "BUTTON" && el.attrs.type === button[1];
  return false;
}

function walk(el, selector) {
  for (const child of el.children) {
    if (matches(child, selector)) return child;
    const found = walk(child, selector);
    if (found) return found;
  }
  return null;
}

function submitForm(form) {
  const event = { defaultPrevented: false, preventDefault() { this.defaultPrevented = true; } };
  for (const fn of form.listeners.submit || []) fn(event);
  return event;
}

function mount() {
  const doc = new Doc();
  const form = doc.createElement("form");
  form.id = "lead-form";
  const fields = {};
  for (const name of ["company_url", "company", "dept", "name", "email", "tel", "topic", "message"]) {
    const field = doc.createElement("input");
    field.setAttribute("name", name);
    field.value = SAMPLE[name] || "";
    form.appendChild(field);
    fields[name] = field;
  }
  const button = doc.createElement("button");
  button.setAttribute("type", "submit");
  form.appendChild(button);
  const status = doc.createElement("div");
  status.id = "form-status";
  status.hidden = true;
  form.appendChild(status);
  const done = doc.createElement("div");
  done.id = "form-done";
  done.setAttribute("aria-hidden", "true");
  done.textContent = "送信ありがとうございました。担当者よりご連絡いたします。";
  return { doc, form, fields, button, status, done };
}

function bind(env) {
  const ui = mount();
  inquiry.bindInquiryForm(ui.doc, env);
  return ui;
}

async function waitFor(fn) {
  const start = Date.now();
  while (Date.now() - start < 1500) {
    if (fn()) return;
    await new Promise((resolve) => setTimeout(resolve, 10));
  }
  throw new Error("timed out waiting for form state");
}

function assertNotDelivered(ui) {
  assert.notEqual(ui.done.style.display, "block");
  assert.notEqual(ui.form.style.display, "none");
  assert.equal(ui.status.hidden, false);
  assert.match(ui.status.textContent, /届いていません/);
  assert.doesNotMatch(ui.status.textContent, /ありがとうございました/);
  assert.equal(ui.button.disabled, false);
  assert.equal(ui.fields.company.value, SAMPLE.company);
  assert.equal(ui.fields.name.value, SAMPLE.name);
  assert.equal(ui.fields.email.value, SAMPLE.email);
  assert.equal(ui.fields.message.value, SAMPLE.message);
}

test("受付URLの初期値は空で、成功用のURLを埋め込まない", () => {
  const config = fs.readFileSync(path.join(__dirname, "../assets/config.js"), "utf8");
  const assignments = config.match(/window\.CHINICHI_LEAD_ENDPOINT\s*=\s*[^;]+;/g);
  assert.deepEqual(assignments, ['window.CHINICHI_LEAD_ENDPOINT = "";']);
});

test("応答の解釈は fixture の成功・失敗・HTML を分ける", () => {
  assert.equal(inquiry.isInquiryEndpointConfigured(""), false);
  assert.equal(inquiry.isInquiryEndpointConfigured("   "), false);
  assert.equal(inquiry.isInquiryEndpointConfigured(undefined), false);
  assert.deepEqual(
    inquiry.interpretInquiryResponse(200, "application/json", SUCCESS_BODY),
    { ok: true, reason: "accepted" }
  );
  assert.equal(inquiry.interpretInquiryResponse(204, "application/json", "").ok, true);
  assert.equal(inquiry.interpretInquiryResponse(201, null, "   ").ok, true);
  assert.equal(
    inquiry.interpretInquiryResponse(200, "application/json", EXPLICIT_FAILURE_BODY).reason,
    "explicit-failure"
  );
  assert.equal(inquiry.interpretInquiryResponse(200, "application/json", '{"success":false}').ok, false);
  assert.equal(inquiry.interpretInquiryResponse(400, "application/json", CLIENT_ERROR_BODY).reason, "http");
  assert.equal(inquiry.interpretInquiryResponse(503, "application/json", SERVER_ERROR_BODY).reason, "http");
  assert.equal(inquiry.interpretInquiryResponse(500, "application/json", SUCCESS_BODY).ok, false);
  assert.equal(inquiry.interpretInquiryResponse(200, "text/html; charset=utf-8", HTML_BODY).reason, "not-json");
  assert.equal(inquiry.interpretInquiryResponse(200, "application/json", "{").reason, "invalid-json");
});

test("空の送信先では送らず、未設定と表示して入力を残す", () => {
  let called = 0;
  const ui = bind({
    CHINICHI_LEAD_ENDPOINT: "",
    fetch() { called += 1; return Promise.reject(new Error("should not send")); },
    location: { pathname: "/corporate/index.html" }
  });
  const event = submitForm(ui.form);
  assert.equal(event.defaultPrevented, true);
  assert.equal(called, 0);
  assertNotDelivered(ui);
  assert.match(ui.status.textContent, /受付先が未設定/);
  assert.match(ui.status.textContent, /03-6205-9570/);
  assert.equal(ui.status.className, "form-status is-error");
  const link = ui.status.children.find((child) => child.tagName === "A");
  assert.equal(link.getAttribute("href"), "tel:0362059570");
  assert.equal(ui.status.getAttribute("role"), "alert");
  assert.equal(ui.status.getAttribute("aria-live"), "assertive");
});

test("空白だけの送信先も未設定として扱う", () => {
  let called = 0;
  const ui = bind({
    CHINICHI_LEAD_ENDPOINT: "  ",
    fetch() { called += 1; return Promise.reject(new Error("should not send")); }
  });
  submitForm(ui.form);
  assert.equal(called, 0);
  assert.match(ui.status.textContent, /未設定/);
});

test("通信失敗では成功と出さず、ボタンを戻して再送できる", async () => {
  let called = 0;
  const ui = bind({
    CHINICHI_LEAD_ENDPOINT: "http://127.0.0.1:9/api/public/corporate-inquiry",
    fetch() {
      called += 1;
      return Promise.reject(new TypeError("network down"));
    },
    location: { pathname: "/corporate/index.html" }
  });
  submitForm(ui.form);
  await waitFor(() => ui.button.disabled === false && /通信できなかった/.test(ui.status.textContent));
  assert.equal(called, 1);
  assertNotDelivered(ui);
  submitForm(ui.form);
  await waitFor(() => called === 2);
  assert.equal(ui.fields.email.value, SAMPLE.email);
});

test("送信中の連打は1回だけ送り、4xx のあと再送できる", async () => {
  let called = 0;
  let release;
  const bodies = [];
  const ui = bind({
    CHINICHI_LEAD_ENDPOINT: "http://127.0.0.1/mock",
    fetch(_url, options) {
      called += 1;
      bodies.push(options.body);
      return new Promise((resolve) => { release = resolve; });
    },
    location: { pathname: "/corporate/index.html" }
  });
  submitForm(ui.form);
  submitForm(ui.form);
  assert.equal(called, 1);
  assert.equal(ui.button.disabled, true);
  assert.match(ui.status.textContent, /送信しています/);
  assert.equal(ui.status.className, "form-status is-pending");
  release(jsonResponse(400, CLIENT_ERROR_BODY));
  await waitFor(() => ui.button.disabled === false);
  assertNotDelivered(ui);
  assert.equal(JSON.parse(bodies[0]).email, SAMPLE.email);
  assert.equal(JSON.parse(bodies[0]).company, SAMPLE.company);
  submitForm(ui.form);
  assert.equal(called, 2);
  release(jsonResponse(200, SUCCESS_BODY));
  await waitFor(() => ui.done.style.display === "block");
  assert.equal(ui.form.style.display, "none");
  assert.equal(ui.done.getAttribute("aria-hidden"), "false");
  assert.equal(ui.button.disabled, true);
  assert.equal(ui.status.hidden, true);
  assert.equal(ui.status.textContent, "");
});

test("5xx と HTML の 200 と ok:false は成功にしない", async () => {
  const cases = [
    jsonResponse(503, SERVER_ERROR_BODY),
    jsonResponse(422, CLIENT_ERROR_BODY),
    { status: 200, headers: headers("text/html; charset=utf-8"), text: () => Promise.resolve(HTML_BODY) },
    jsonResponse(200, EXPLICIT_FAILURE_BODY)
  ];
  for (const response of cases) {
    const ui = bind({
      CHINICHI_LEAD_ENDPOINT: "http://127.0.0.1/mock",
      fetch() { return Promise.resolve(response); }
    });
    submitForm(ui.form);
    await waitFor(() => ui.status.hidden === false && ui.button.disabled === false && ui.status.className.indexOf("is-error") !== -1);
    assertNotDelivered(ui);
  }
});

test("ハニーポット入力は送らず、成功とも未設定とも出さない", () => {
  let called = 0;
  const ui = bind({
    CHINICHI_LEAD_ENDPOINT: "",
    fetch() { called += 1; return Promise.reject(new Error("no")); }
  });
  ui.fields.company_url.value = "https://spam.example";
  submitForm(ui.form);
  assert.equal(called, 0);
  assert.equal(ui.status.hidden, true);
  assert.notEqual(ui.done.style.display, "block");
});

test("ローカル fixture サーバへの POST だけを見る（本番へは出さない）", async () => {
  const received = [];
  const server = http.createServer((req, res) => {
    const chunks = [];
    req.on("data", (chunk) => chunks.push(chunk));
    req.on("end", () => {
      const body = Buffer.concat(chunks).toString("utf8");
      received.push({ url: req.url, type: req.headers["content-type"], body });
      if (req.url === "/ok") {
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(SUCCESS_BODY);
      } else if (req.url === "/bad") {
        res.writeHead(400, { "Content-Type": "application/json" });
        res.end(CLIENT_ERROR_BODY);
      } else if (req.url === "/down") {
        res.writeHead(503, { "Content-Type": "application/json" });
        res.end(SERVER_ERROR_BODY);
      } else if (req.url === "/html") {
        res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
        res.end(HTML_BODY);
      } else if (req.url === "/false") {
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(EXPLICIT_FAILURE_BODY);
      } else if (req.url === "/empty") {
        res.writeHead(204);
        res.end();
      } else {
        res.writeHead(404, { "Content-Type": "text/plain" });
        res.end("missing");
      }
    });
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const { port } = server.address();
  const base = "http://127.0.0.1:" + port;

  try {
    const closed = bind({
      CHINICHI_LEAD_ENDPOINT: "http://127.0.0.1:9/api/public/corporate-inquiry",
      fetch: global.fetch,
      location: { pathname: "/corporate/index.html" }
    });
    submitForm(closed.form);
    await waitFor(() => /通信できなかった/.test(closed.status.textContent));
    assertNotDelivered(closed);

    const paths = [
      ["/bad", false],
      ["/down", false],
      ["/html", false],
      ["/false", false],
      ["/missing", false],
      ["/empty", true],
      ["/ok", true]
    ];
    for (const [route, expectSuccess] of paths) {
      const ui = bind({
        CHINICHI_LEAD_ENDPOINT: base + route,
        fetch: global.fetch,
        location: { pathname: "/corporate/index.html" }
      });
      submitForm(ui.form);
      if (expectSuccess) {
        await waitFor(() => ui.done.style.display === "block");
        assert.equal(ui.form.style.display, "none");
        assert.match(ui.done.textContent, /ありがとうございました/);
        assert.equal(ui.status.textContent, "");
      } else {
        await waitFor(() => ui.button.disabled === false && /届いていません/.test(ui.status.textContent));
        assertNotDelivered(ui);
      }
    }

    assert.ok(received.length >= 6);
    for (const entry of received) {
      assert.equal(entry.type, "application/json");
      const payload = JSON.parse(entry.body);
      assert.equal(payload.source, "website-corporate");
      assert.equal(payload.email, SAMPLE.email);
      assert.match(payload.email, /@example\.co\.jp$/);
    }
    const hosts = new Set(received.map((entry) => entry.url));
    assert.deepEqual(hosts, new Set(["/bad", "/down", "/html", "/false", "/missing", "/empty", "/ok"]));
  } finally {
    await new Promise((resolve, reject) => server.close((error) => error ? reject(error) : resolve()));
  }
});
