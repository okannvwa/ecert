// Helper function to get CSRF token
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// Open Task Modal for Adding or Editing
function openTaskModal(action, taskId = null) {
    const modal = document.getElementById('taskModal');
    const form = document.getElementById('taskForm');
    const deleteBtn = document.getElementById('deleteTaskBtn');

    let url = '';
    if (action === 'add') {
        url = 'add/';
        deleteBtn.style.display = 'none';  // Hide delete button for new task
    } else if (action === 'edit') {
        url = `/${taskId}/delete/`;
        deleteBtn.style.display = 'block';
        deleteBtn.setAttribute('data-task-id', taskId);  // Store task ID for deletion
    }

    // Load form content via AJAX
    fetch(url, {
        headers: { 'X-CSRFToken': getCSRFToken() }
    })
    .then(response => {
        if (response.redirected) {
            // If user is redirected (usually to login), redirect to the login page
            window.location.href = response.url;
            return Promise.reject('Redirected to login');
        }
        return response.text();
    })
    .then(html => {
        document.getElementById('taskFormContent').innerHTML = html;
        form.action = url;
        modal.style.display = 'block';
    })
    .catch(error => console.error('Error loading modal content:', error));
}

// Close Modal
function closeModal() {
    document.getElementById('taskModal').style.display = 'none';
}

// Submit Form via AJAX
document.getElementById('taskForm').onsubmit = function(event) {
    event.preventDefault();
    fetch(this.action, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCSRFToken() },
        body: new FormData(this)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeModal();
            location.reload();  // Reload page to show updated tasks
        } else if (data.error) {
            alert(data.error);  // Display error message from the server if provided
        }
    })
    .catch(error => console.error('Error submitting form:', error));
};

// Delete Task
function deleteTask() {
    const taskId = document.getElementById('deleteTaskBtn').getAttribute('data-task-id');
    fetch(`/${taskId}/delete/`, {
        method: 'POST',
        headers: { 
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeModal();
            location.reload();
        } else if (data.error) {
            alert(data.error);
        }
    })
    .catch(error => console.error('Error deleting task:', error));
}

// Close modal if user clicks outside of it
window.onclick = function(event) {
    const modal = document.getElementById('taskModal');
    if (event.target === modal) {
        closeModal();
    }
};