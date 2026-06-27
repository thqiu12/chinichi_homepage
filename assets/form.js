/* 法人問い合わせフォーム送信処理(全ページ共通)
   - window.CHINICHI_LEAD_ENDPOINT が設定されていればJSONでPOST
   - 未設定/失敗時はフォールバックで完了表示(問い合わせを取りこぼさない) */
(function () {
  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  ready(function () {
    var form = document.getElementById("lead-form");
    if (!form) return;
    var done = document.getElementById("form-done");

    form.addEventListener("submit", function (e) {
      e.preventDefault();

      // ハニーポット(bot対策):隠しフィールドに入力があれば無視
      if (form.querySelector('[name="company_url"]') &&
          form.querySelector('[name="company_url"]').value) {
        return;
      }

      var data = {
        source: "website-corporate",
        page: location.pathname,
        company: val("company"),
        dept: val("dept"),
        name: val("name"),
        email: val("email"),
        tel: val("tel"),
        topic: val("topic"),
        message: val("message")
      };

      function val(n) {
        var el = form.querySelector('[name="' + n + '"]');
        return el ? el.value.trim() : "";
      }

      function showDone() {
        if (done) { form.style.display = "none"; done.style.display = "block"; }
      }

      var endpoint = window.CHINICHI_LEAD_ENDPOINT;
      if (!endpoint) { showDone(); return; }

      var btn = form.querySelector('button[type="submit"]');
      if (btn) { btn.disabled = true; btn.style.opacity = ".6"; }

      fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      })
        .then(function () { showDone(); })
        .catch(function () { showDone(); });
    });
  });
})();
