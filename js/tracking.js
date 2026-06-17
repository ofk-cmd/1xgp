(function () {
  'use strict';

  /**
   * Собирает трекинговую ссылку из параметров лендинга.
   * Пример лендинга:
   * https://1xbt.kz/?domain=reffpa.com/L&tag=...&pb=...&click_id={clickid}
   * Результат:
   * https://reffpa.com/L?tag=...&pb=...&click_id={clickid}
   */
  function buildTrackingLink() {
    var params = new URLSearchParams(window.location.search);
    var domain = params.get('domain');
    var tag = params.get('tag');
    var pb = params.get('pb');
    var clickId = params.get('click_id');

    if (!domain || !tag || !pb) {
      return null;
    }

    var base = domain.indexOf('://') === -1 ? 'https://' + domain : domain;
    var parts = ['tag=' + tag, 'pb=' + pb];
    if (clickId) {
      parts.push('click_id=' + clickId);
    }
    return base + '?' + parts.join('&');
  }

  function applyInstallLinks() {
    var href = buildTrackingLink();
    var links = document.querySelectorAll('[data-install-link]');

    links.forEach(function (el) {
      if (href) {
        el.setAttribute('href', href);
        el.removeAttribute('aria-disabled');
      } else {
        el.setAttribute('href', '#');
        el.setAttribute('aria-disabled', 'true');
        el.setAttribute('title', 'Добавьте параметры domain, tag и pb в URL лендинга');
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyInstallLinks);
  } else {
    applyInstallLinks();
  }
})();
