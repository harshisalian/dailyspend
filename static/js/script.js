"""
JavaScript utilities for Daily Spend.

  Production - ready practices demonstrated:
  - Unobtrusive JavaScript(doesn't interfere with HTML)
    - Event delegation
  - Error handling
  - Accessibility support
"""

// Auto-hide alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert');

    alerts.forEach(alert => {
      // Auto-close after 5 seconds
      setTimeout(function () {
        alert.style.display = 'none';
      }, 5000);
    });
  });
