document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Helper to show transient messages
  function showMessage(text, type = "info") {
    messageDiv.textContent = text;
    messageDiv.className = type;
    messageDiv.classList.remove("hidden");
    setTimeout(() => messageDiv.classList.add("hidden"), 5000);
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Reset activity select options
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";
        activityCard.dataset.activity = name;

        const spotsLeft = details.max_participants - details.participants.length;

        const participantsList = details.participants.length > 0
          ? details.participants.map(p => `
              <li data-email="${p}">
                <span class="participant-email">${p}</span>
                <button class="delete-btn" title="Unregister" aria-label="Unregister ${p}">✖</button>
              </li>
            `).join('')
          : '<li class="no-participants"><em>No participants yet</em></li>';

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <strong>Participants:</strong>
            <ul class="participants-list">
              ${participantsList}
            </ul>
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Delegated handler for delete (unregister) buttons
  activitiesList.addEventListener('click', async (event) => {
    const btn = event.target.closest('.delete-btn');
    if (!btn) return;

    const li = btn.closest('li');
    if (!li) return;

    const email = li.dataset.email;
    const activityCard = btn.closest('.activity-card');
    const activityName = activityCard?.dataset?.activity;

    if (!activityName || !email) return;

    // Confirm before unregistering
    if (!confirm(`Unregister ${email} from ${activityName}?`)) return;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(email)}`,
        { method: 'DELETE' }
      );

      if (response.ok) {
        const result = await response.json();
        showMessage(result.message, 'success');
        // Refresh activities list to update availability and presence
        fetchActivities();
      } else {
        const err = await response.json().catch(() => ({}));
        showMessage(err.detail || 'Failed to unregister participant', 'error');
      }
    } catch (error) {
      console.error('Error unregistering participant:', error);
      showMessage('Failed to unregister. Please try again.', 'error');
    }
  });

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, 'success');
        signupForm.reset();
        fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", 'error');
      }
    } catch (error) {
      showMessage("Failed to sign up. Please try again.", 'error');
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
