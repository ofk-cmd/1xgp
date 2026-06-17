(function () {
  'use strict';

  /**
   * Параметры лендинга → трекинговая ссылка на кнопке «Установить».
   *
   * Вход (URL лендинга):
   *   https://1xbt.kz/?domain=reffpa.com/L&tag=TAG&pb=PB&click_id={clickid}
   *
   * Выход (href кнопки):
   *   https://reffpa.com/L?tag=TAG&pb=PB&click_id={clickid}
   */
  function getParam(params, key) {
    var value = params.get(key);
    return value === null ? '' : value;
  }

  function buildTrackingLink() {
    var params = new URLSearchParams(window.location.search);
    var domain = getParam(params, 'domain').trim();
    var tag = getParam(params, 'tag').trim();
    var pb = getParam(params, 'pb').trim();
    var clickId = getParam(params, 'click_id').trim();

    if (!domain || !tag || !pb) {
      return null;
    }

    var base = domain.indexOf('://') > -1 ? domain : 'https://' + domain;
    var query = ['tag=' + tag, 'pb=' + pb];

    if (clickId) {
      query.push('click_id=' + clickId);
    }

    return base + '?' + query.join('&');
  }

  function applyInstallLinks() {
    var href = buildTrackingLink();
    var links = document.querySelectorAll('[data-install-link]');

    links.forEach(function (el) {
      if (href) {
        el.setAttribute('href', href);
        el.removeAttribute('aria-disabled');
        el.removeAttribute('title');
      } else {
        el.setAttribute('href', '#');
        el.setAttribute('aria-disabled', 'true');
        el.setAttribute('title', 'Добавьте в URL параметры: domain, tag, pb');
      }
    });
  }

  function blockDisabledInstallClick(event) {
    var target = event.target.closest('[data-install-link]');
    if (target && target.getAttribute('aria-disabled') === 'true') {
      event.preventDefault();
    }
  }

  document.addEventListener('click', blockDisabledInstallClick, true);

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyInstallLinks);
  } else {
    applyInstallLinks();
  }
})();
