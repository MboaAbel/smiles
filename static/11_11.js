function scheduleNotification() {
  Notification.requestPermission().then(permission => {
    if (permission === "granted") {
      const now = new Date();
      const target = new Date();
      target.setHours(12, 00, 0, 0);

      // If it's past 11:11 today, schedule for tomorrow
      if (now > target) {
        target.setDate(target.getDate() + 1);
      }

      const timeout = target.getTime() - now.getTime();

      setTimeout(() => {
        new Notification("🦷 SmileSlot Reminder", {
          body: "Time to check today’s bookings and smile!",
          icon: "/static/icon/smile.png"
        });

        // Schedule next day recursively
        scheduleNotification();
      }, timeout);
    }
  });
}

// Call it on load
scheduleNotification();
