/* Extra JavaScript for Material for MkDocs
 * Custom functionality for AI Management Team Documentation
 * Last Updated: 2026-01-03
 */

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
  console.log('AI Management Team Documentation - Extra JS Loaded');

  // Add copy button confirmation
  const copyButtons = document.querySelectorAll('.md-clipboard');
  copyButtons.forEach(button => {
    button.addEventListener('click', function() {
      // Show temporary confirmation
      const originalTitle = this.title;
      this.title = '✓ Copied!';
      setTimeout(() => {
        this.title = originalTitle;
      }, 2000);
    });
  });

  // Add table of contents sticky behavior
  const toc = document.querySelector('.md-sidebar--secondary');
  if (toc) {
    let lastScroll = 0;
    window.addEventListener('scroll', function() {
      const currentScroll = window.pageYOffset;
      // Add subtle fade effect when scrolling
      if (currentScroll > lastScroll) {
        toc.style.opacity = '0.9';
      } else {
        toc.style.opacity = '1';
      }
      lastScroll = currentScroll;
    });
  }

  // Add keyboard shortcuts
  document.addEventListener('keydown', function(e) {
    // Ctrl+K or Cmd+K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      const searchInput = document.querySelector('.md-search__input');
      if (searchInput) {
        searchInput.focus();
      }
    }

    // Escape to close search
    if (e.key === 'Escape') {
      const searchInput = document.querySelector('.md-search__input');
      if (searchInput && document.activeElement === searchInput) {
        searchInput.blur();
      }
    }
  });

  // Add "scroll to top" smooth behavior
  const scrollTopButton = document.querySelector('.md-top');
  if (scrollTopButton) {
    scrollTopButton.addEventListener('click', function(e) {
      e.preventDefault();
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
  }

  // Add external link indicators
  const externalLinks = document.querySelectorAll('a[href^="http"]');
  externalLinks.forEach(link => {
    // Skip links to the same domain
    if (!link.href.includes(window.location.hostname)) {
      link.setAttribute('target', '_blank');
      link.setAttribute('rel', 'noopener noreferrer');
      // Add small icon to indicate external link
      if (!link.querySelector('.external-link-icon')) {
        const icon = document.createElement('span');
        icon.className = 'external-link-icon';
        icon.innerHTML = ' ↗';
        icon.style.fontSize = '0.8em';
        icon.style.opacity = '0.6';
        link.appendChild(icon);
      }
    }
  });

  // Add reading time estimator for long pages
  const content = document.querySelector('.md-content__inner');
  if (content) {
    const text = content.innerText;
    const wordCount = text.split(/\s+/).length;
    const readingTime = Math.ceil(wordCount / 200); // 200 words per minute

    if (readingTime > 5 && document.querySelector('h1')) {
      const readingTimeDiv = document.createElement('div');
      readingTimeDiv.className = 'reading-time';
      readingTimeDiv.style.cssText = 'color: var(--md-default-fg-color--light); font-size: 0.8rem; margin: 0.5rem 0;';
      readingTimeDiv.innerHTML = `📖 Estimated reading time: ${readingTime} minutes`;

      const h1 = document.querySelector('h1');
      h1.parentNode.insertBefore(readingTimeDiv, h1.nextSibling);
    }
  }

  // Add version badge to footer (if version info available)
  const footer = document.querySelector('.md-footer-meta');
  if (footer) {
    const versionBadge = document.createElement('div');
    versionBadge.style.cssText = 'text-align: center; padding: 0.5rem; font-size: 0.7rem; opacity: 0.7;';
    versionBadge.innerHTML = 'Documentation built with Material for MkDocs | Last updated: <span id="build-date"></span>';
    footer.appendChild(versionBadge);

    // Set current date
    const buildDate = document.getElementById('build-date');
    if (buildDate) {
      buildDate.textContent = new Date().toLocaleDateString();
    }
  }

  // Log analytics event (if Google Analytics is configured)
  if (window.gtag) {
    gtag('event', 'page_view', {
      page_title: document.title,
      page_location: window.location.href,
      page_path: window.location.pathname
    });
  }
});

// Add search result click tracking
document.addEventListener('click', function(e) {
  if (e.target.closest('.md-search-result__link')) {
    console.log('Search result clicked:', e.target.textContent);
    // Could send to analytics if configured
  }
});

// Add print page functionality
function printPage() {
  window.print();
}

// Expose utilities to global scope
window.ManagementTeamDocs = {
  version: '1.0',
  printPage: printPage
};
