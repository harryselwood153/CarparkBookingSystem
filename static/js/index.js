function registerUser(firstName, lastName, username, password) { 
  fetch('/register', { 
    method: 'POST',
    headers: {'Content-Type': 'application/json'}, 
    body: JSON.stringify({ firstName, lastName, username, password })
  })
  .then(response => {
    if (!response.ok) { 
        return response.json().then(err => {
        throw new Error(err.error || 'Registration failed');
      });
    }
    return response.json();
  })
    .then(data => {
    alert(data.message || 'Registered successfully!'); 
  })
    .catch(err => {
    alert(err.message);
  });
}

document.getElementById('registerForm').addEventListener('submit', function(e) { 
    e.preventDefault();

    // Collect data from input fields
    const firstName = document.getElementById('firstName').value.trim();
    const lastName = document.getElementById('lastName').value.trim();
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;

    registerUser(firstName, lastName, username, password) 
});