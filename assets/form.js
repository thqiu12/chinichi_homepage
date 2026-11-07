/* 法人問い合わせフォーム（全ページ共通）
   送信先 window.CHINICHI_LEAD_ENDPOINT が空なら送らない。
   成功と出すのは、POST の応答が次をすべて満たすときだけ。
   - HTTP ステータスが 200 以上 300 未満
   - 本文が空、または JSON として読める
   - JSON オブジェクトなら ok / success が false ではない
   通信失敗、2xx 以外、HTML、壊れた JSON、明示的な失敗は「届いていない」。
   そのときは入力を残し、ボタンを戻して再送できる。送信中の連打は無視する。
   応答の項目名はこのリポジトリに仕様が無い。受付URLも空のままにする。 */
(function (root) {
  var COPY = {
    unconfiguredLead: "送信できませんでした。受付先が未設定のため、内容は届いていません。入力内容はこの画面に残しています。お手数ですが、法人窓口 ",
    unconfiguredTail: " までお電話ください。",
    phoneLabel: "03-6205-9570",
    phoneHref: "tel:0362059570",
    network: "送信できませんでした。通信できなかったため、内容は届いていません。入力内容は残しています。時間をおいて、もう一度お試しください。",
    rejected: "送信できませんでした。受付側が受け付けなかったため、内容は届いていません。入力内容は残しています。時間をおいて、もう一度お試しください。",
    pending: "送信しています。完了までお待ちください。"
  };

  function isInquiryEndpointConfigured(endpoint) {
    return typeof endpoint === "string" && endpoint.trim() !== "";
  }

  function interpretInquiryResponse(status, contentType, bodyText) {
    var code = Number(status);
    if (!isFinite(code) || code < 200 || code >= 300) {
      return { ok: false, reason: "http" };
    }
    var text = bodyText == null ? "" : String(bodyText).replace(/^\s+|\s+$/g, "");
    if (text === "") return { ok: true, reason: "empty" };

    var type = String(contentType || "").toLowerCase();
    var jsonType = type.indexOf("application/json") !== -1 || type.indexOf("+json") !== -1;
    var looksJson = jsonType || text.charAt(0) === "{" || text.charAt(0) === "[";
    if (!looksJson) return { ok: false, reason: "not-json" };

    var data;
    try {
      data = JSON.parse(text);
    } catch (e) {
      return { ok: false, reason: "invalid-json" };
    }
    if (data && typeof data === "object" && !Array.isArray(data)) {
      if (data.ok === false || data.success === false) {
        return { ok: false, reason: "explicit-failure" };
      }
    }
    return { ok: true, reason: "accepted" };
  }

  function bindInquiryForm(doc, env) {
    env = env || root;
    var form = doc.getElementById("lead-form");
    if (!form) return null;
    var done = doc.getElementById("form-done");
    var statusEl = doc.getElementById("form-status");
    if (!statusEl) {
      statusEl = doc.createElement("div");
      statusEl.id = "form-status";
      statusEl.className = "form-status";
      statusEl.setAttribute("role", "alert");
      statusEl.setAttribute("aria-live", "assertive");
      statusEl.setAttribute("aria-atomic", "true");
      statusEl.tabIndex = -1;
      statusEl.hidden = true;
      form.appendChild(statusEl);
    }
    if (!statusEl.getAttribute("role")) statusEl.setAttribute("role", "alert");
    if (!statusEl.getAttribute("aria-live")) statusEl.setAttribute("aria-live", "assertive");
    if (!statusEl.getAttribute("aria-atomic")) statusEl.setAttribute("aria-atomic", "true");
    if (statusEl.tabIndex !== -1) statusEl.tabIndex = -1;

    var submitting = false;
    var accepted = false;

    function val(name) {
      var el = form.querySelector('[name="' + name + '"]');
      return el && el.value ? String(el.value).replace(/^\s+|\s+$/g, "") : "";
    }

    function setBusy(busy) {
      var btn = form.querySelector('button[type="submit"]');
      if (!btn) return;
      btn.disabled = busy;
      btn.setAttribute("aria-busy", busy ? "true" : "false");
    }

    function showStatus(kind) {
      statusEl.hidden = false;
      statusEl.className = "form-status " + (kind === "pending" ? "is-pending" : "is-error");
      if (kind === "unconfigured") {
        if (typeof statusEl.replaceChildren === "function") statusEl.replaceChildren();
        else statusEl.textContent = "";
        statusEl.appendChild(doc.createTextNode(COPY.unconfiguredLead));
        var link = doc.createElement("a");
        link.setAttribute("href", COPY.phoneHref);
        link.textContent = COPY.phoneLabel;
        statusEl.appendChild(link);
        statusEl.appendChild(doc.createTextNode(COPY.unconfiguredTail));
      } else if (kind === "network") {
        statusEl.textContent = COPY.network;
      } else if (kind === "pending") {
        statusEl.textContent = COPY.pending;
      } else {
        statusEl.textContent = COPY.rejected;
      }
    }

    function showDone() {
      accepted = true;
      statusEl.hidden = true;
      statusEl.className = "form-status";
      statusEl.textContent = "";
      form.style.display = "none";
      if (!done) return;
      done.style.display = "block";
      if (typeof done.setAttribute === "function") done.setAttribute("aria-hidden", "false");
    }

    function release() {
      if (accepted) return;
      submitting = false;
      setBusy(false);
    }

    form.addEventListener("submit", function (e) {
      if (e && typeof e.preventDefault === "function") e.preventDefault();
      if (submitting) return;

      var trap = form.querySelector('[name="company_url"]');
      if (trap && trap.value) return;

      var data = {
        source: "website-corporate",
        page: (env.location && env.location.pathname) || "",
        company: val("company"),
        dept: val("dept"),
        name: val("name"),
        email: val("email"),
        tel: val("tel"),
        topic: val("topic"),
        message: val("message")
      };

      var endpoint = env.CHINICHI_LEAD_ENDPOINT;
      if (!isInquiryEndpointConfigured(endpoint)) {
        showStatus("unconfigured");
        return;
      }

      submitting = true;
      setBusy(true);
      showStatus("pending");

      var fetchFn = env.fetch;
      if (typeof fetchFn !== "function") {
        showStatus("network");
        release();
        return;
      }

      fetchFn(String(endpoint).replace(/^\s+|\s+$/g, ""), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify(data)
      }).then(function (res) {
        var read = res && typeof res.text === "function" ? res.text() : Promise.resolve("");
        return Promise.resolve(read).then(function (text) {
          return {
            status: res.status,
            contentType: res.headers && res.headers.get ? res.headers.get("content-type") : "",
            text: text
          };
        }, function () {
          return { status: res.status, contentType: "", text: null, unreadable: true };
        });
      }).then(function (result) {
        if (result.unreadable || result.text == null) {
          showStatus("rejected");
          return;
        }
        var verdict = interpretInquiryResponse(result.status, result.contentType, result.text);
        if (verdict.ok) showDone();
        else showStatus("rejected");
      }).catch(function () {
        showStatus("network");
      }).then(release);
    });

    return { form: form, statusEl: statusEl, done: done };
  }

  if (typeof document !== "undefined" && root.document) {
    var start = function () { bindInquiryForm(document, root); };
    if (document.readyState !== "loading") start();
    else document.addEventListener("DOMContentLoaded", start);
  }

  var api = {
    COPY: COPY,
    isInquiryEndpointConfigured: isInquiryEndpointConfigured,
    interpretInquiryResponse: interpretInquiryResponse,
    bindInquiryForm: bindInquiryForm
  };
  root.ChinichiInquiry = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof window !== "undefined" ? window : globalThis);
