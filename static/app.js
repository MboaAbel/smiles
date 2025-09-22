let deferredPrompt = null;
const installBtn = document.getElementById('install-btn');

function hideInstallBtn() {
  if (installBtn) installBtn.style.display = 'none';
}
function showInstallBtn() {
  if (installBtn) installBtn.style.display = 'block';
}

// If already running in standalone, hide install UI
if (window.matchMedia && window.matchMedia('(display-mode: standalone)').matches) {
  hideInstallBtn();
} else if (navigator.standalone) { // iOS legacy check
  hideInstallBtn();
}

// beforeinstallprompt: show custom install UI
window.addEventListener('beforeinstallprompt', (e) => {
  // Prevent the automatic mini-infobar
  e.preventDefault();
  deferredPrompt = e;

  // Show the install button if it exists
  showInstallBtn();
});

// Add click handler once (guarded)
if (installBtn) {
  installBtn.addEventListener('click', async () => {
    // Defensive: if there's no deferred prompt, nothing to do
    if (!deferredPrompt) {
      console.warn('No deferredPrompt available — maybe already installed or unsupported.');
      hideInstallBtn();
      return;
    }

    // Hide the button to prevent repeated clicks
    hideInstallBtn();

    // Show the native prompt
    try {
      await deferredPrompt.prompt();
      const choice = await deferredPrompt.userChoice;
      if (choice && choice.outcome === 'accepted') {
        console.log('PWA install accepted');
      } else {
        console.log('PWA install dismissed');
      }
    } catch (err) {
      console.error('Error while prompting install', err);
    } finally {
      // Clean up
      deferredPrompt = null;
    }
  });
}

// Hide install UI when app is installed
window.addEventListener('appinstalled', () => {
  console.log('App installed');
  hideInstallBtn();
});

// Optional: detect display-mode changes (useful when user opens installed app)
window.matchMedia('(display-mode: standalone)').addEventListener('change', e => {
  if (e.matches) {
    hideInstallBtn();
  } else {
    // If it switches back to browser mode, you might want to show it
    // showInstallBtn();
  }
});
