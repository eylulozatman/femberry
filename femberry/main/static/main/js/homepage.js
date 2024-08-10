function openPopup(popupId) {
    document.getElementById(popupId).classList.add('active');
}

function closePopup(popupId) {
    document.getElementById(popupId).classList.remove('active');
}



function getCsrfToken() {
    // Implement CSRF token retrieval logic if needed
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function submitFormByPopupId(popupId) {
    var form = document.getElementById(popupId).querySelector('form');
    var formData = new FormData(form);

    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': '{{ csrf_token }}'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (popupId === 'searchFriendPopup') {
            renderSearchResults(data.matching_usernames);
        } else {
            // Diğer popup'lara göre işlem yapılabilir
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });

    return false; // Formun normal submit işlemi engellenir
}

function respondToRequest(button, action) {
    var requestElement = button.closest('.friend-request');
    var requestId = requestElement.getAttribute('data-request-id');

    // URL'yi HTML'den al
    const url = document.getElementById('friendRequestsPopup').getAttribute('data-respond-friend-request-url');

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()  // CSRF token'ı fonksiyonla al
        },
        body: JSON.stringify({
            request_id: requestId,
            action: action
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            requestElement.remove();
        } else {
            console.error('Error:', data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}




document.getElementById('searchFriendForm').addEventListener('submit', function(event) {
event.preventDefault();
var formData = new FormData(this);
fetch(this.action, {
method: 'POST',
body: formData
})
.then(response => response.json())
.then(data => {
renderResults(data.matching_users);
})
.catch(error => {
console.error('Error:', error);
});
});
function renderResults(users) {
    var resultsContainer = document.getElementById('searchResults');
    resultsContainer.innerHTML = ''; // Clear previous results

    if (users.length === 0) {
        resultsContainer.textContent = 'No matching users found.';
    } else {
        var list = document.createElement('ul');
        users.forEach(function(user) {
            var listItem = document.createElement('li');
            var button = document.createElement('button');
            button.textContent = 'Send Request';

            if (user.status !== 'rejected' && user.status !== 'none') {
                button.disabled = true; // Disable button if not 'rejected' or no request
                button.textContent = user.status.charAt(0).toUpperCase() + user.status.slice(1); // Show status
            }

            button.onclick = function() {
                sendFriendship(user.username); 
            };
            listItem.textContent = user.username + ' ';
            listItem.appendChild(button); 
            list.appendChild(listItem); 
        });
        resultsContainer.appendChild(list); 
    }
}

function sendFriendship(username) {
    // Determine the appropriate URL
    const url = `/send-friendship/${encodeURIComponent(username)}/`;

    // Perform the fetch request
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),  // Ensure CSRF token is sent
        },
        body: JSON.stringify({}), // No need to send username in body since it's in the URL
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log('Friend request sent successfully');
            const sendFriendshipButton = document.getElementById(`send-friendship-${username}`);
            sendFriendshipButton.classList.toggle('friend-request-sent');
        } else {
            console.error('Error:', data.message);
        }
    })
    .catch(error => console.error('Error:', error));
}



function toggleEditDelete(postId) {
const menu = document.getElementById(`edit-delete-menu-${postId}`);
const isVisible = menu.style.display === 'block';
menu.style.display = isVisible ? 'none' : 'block';

// Immediately show the Save button/form when the menu is toggled
const editForm = document.getElementById(`edit-post-form-${postId}`);

console.log(`Toggled form: ${editForm.id}`);

if (!isVisible) {
editForm.style.display = 'block';
}
}

// You can remove or adjust the editPost function if it also handles showing the form
function editPost(postId) {
const titleElement = document.getElementById(`post-title-${postId}`);
titleElement.contentEditable = true;
titleElement.focus();
}


// Function to handle the form submission for editing
document.addEventListener('DOMContentLoaded', function () {
document.querySelectorAll('form[id^="edit-post-form-"]').forEach(form => {
form.addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent default form submission
    const postId = form.querySelector('input[name="post_id"]').value;
    const titleElement = document.getElementById(`post-title-${postId}`);
    const newText = titleElement.innerText.trim();

    // Set the new text in the hidden input
    // bu adım gerekli olmayabilir, direkt değişken datayı kullanabiliriz.
    form.querySelector(`#new-text-${postId}`).value = newText;

    // Fetch the form data to send
    const formData = new FormData(form);
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest', // Indicate AJAX request
            'X-CSRFToken': formData.get('csrfmiddlewaretoken') // CSRF token
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Set the new text in the title element
            titleElement.innerText = newText;
            
            // Disable editing of the title
            titleElement.contentEditable = false;

            // Hide the save button
            form.style.display = 'none';

            // Hide the edit/delete menu
            document.getElementById(`edit-delete-menu-${postId}`).style.display = 'none';
        } else {
            alert('Error saving post');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
});
});


function postlike(postId) {
    const likeButton = document.getElementById(`likebtn-${postId}`);
    const liked = likeButton.classList.contains('liked');

    // Determine the appropriate URL and method based on whether the post is liked
    const url = liked ? `/unlike-post/${postId}/` : `/like-post/${postId}/`;
    const method = 'POST';

    // Perform the fetch request
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(), // Ensure CSRF token is sent
        },
        credentials: 'same-origin'
    }).then(response => {
        if (response.ok) {
            likeButton.classList.toggle('liked');
            likeButton.classList.toggle('not-liked');
        }
    }).catch(error => {
        console.error('Error:', error);
    });
}





function SetPostsFromFriends() {
    const btn = document.getElementById('just-friends-btn');
  
    btn.classList.toggle('userPrefSelected');
    console.log('Button class list:', btn.classList);  // Debugging


    // Send an asynchronous POST request to update preferences
    fetch('/update-user-pref/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()  // Use your existing function to get CSRF token
        },
        body: JSON.stringify({})  // Send an empty body for the toggle action
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/' + data.redirect;  // Redirect on success
        } else {
            console.error('Update failed:', data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


