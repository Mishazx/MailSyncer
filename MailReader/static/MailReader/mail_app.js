function fillCredentials() {
    const select = document.getElementById('account-select');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
  
    const selectedOption = select.options[select.selectedIndex];
    if (selectedOption.value) {
        emailInput.value = selectedOption.value;
        passwordInput.value = selectedOption.getAttribute('data-password');
    } else {
        emailInput.value = '';
        passwordInput.value = '';
    }
  }
  
  document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('login-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        startFetching(email, password);
    });
    document.getElementById('clear-message').addEventListener('click', function() {
        var tbody = document.getElementById('mail-table').getElementsByTagName('tbody')[0];
        tbody.innerHTML = '';

        const progressBar = document.getElementById('progress-bar');
        const percent = 0;
        const progressText = percent + '%';

        progressBar.style.width = percent + '%';
        progressBar.setAttribute('aria-valuenow', percent);
        progressBar.textContent = progressText;

    });
});
  
  function startFetching(email, password) {
    const socket = new WebSocket('ws://localhost:8000/ws/emails/');
  
    socket.onopen = function() {
        const json = JSON.stringify({
            'email': email,
            'password': password
        });
        socket.send(json);
        console.log('WebSocket открыт:', event);
    };
  
    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        const percent = data.percent;
  
        const progressBar = document.getElementById('progress-bar');
        const progressText = percent + '%';
        
        progressBar.style.width = percent + '%';
        progressBar.setAttribute('aria-valuenow', percent);
        progressBar.textContent = progressText;
  
        if (data.message) {
            const table = document.getElementById('mail-table').getElementsByTagName('tbody')[0];
            const row = table.insertRow();
            row.insertCell(0).textContent = data.message;
            row.insertCell(1).textContent = data.from;
            row.insertCell(2).textContent = data.sent_date;
            row.insertCell(3).textContent = data.received_date;
            row.insertCell(4).innerHTML = data.body;
  
            const attachmentsCell = row.insertCell(5);
            if (data.attachments && data.attachments.length > 0) {
                const attachmentLinks = data.attachments.map(att => {
                    return `<a href="${att.url}" target="_blank">${att.filename}</a>`;
                }).join(', ');
                attachmentsCell.innerHTML = attachmentLinks;
            } else {
                attachmentsCell.textContent = 'Нет вложений';
            }
        }
    };
  
    socket.onerror = function(error) {
        console.error('WebSocket ошибка:', error);
    };
  
    socket.onclose = function(event) {
        console.log('WebSocket закрыт:', event);
    };
  }
  