// Enable tooltips everywhere
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Add the current date for datetime-local inputs if empty
    const datetimeInputs = document.querySelectorAll('input[type="datetime-local"]');
    datetimeInputs.forEach(function(input) {
        if (!input.value) {
            const now = new Date();
            // Format the date as YYYY-MM-DDTHH:MM
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            
            const formattedDate = `${year}-${month}-${day}T${hours}:${minutes}`;
            input.value = formattedDate;
        }
    });
    
    // Add confirmation for delete actions
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
    
    // Handle global vs. targeted notifications
    const isGlobalCheckbox = document.getElementById('is_global');
    const targetTeamSelect = document.getElementById('target_team_id');
    
    if (isGlobalCheckbox && targetTeamSelect) {
        isGlobalCheckbox.addEventListener('change', function() {
            targetTeamSelect.disabled = this.checked;
            if (this.checked) {
                targetTeamSelect.value = '';
            }
        });
        
        // Initial state
        if (isGlobalCheckbox.checked) {
            targetTeamSelect.disabled = true;
        }
    }
});
