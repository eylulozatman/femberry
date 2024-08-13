document.addEventListener('DOMContentLoaded', checkExistingAnswer);

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('create-poll-form');
    form.addEventListener('submit', function (event) {
        event.preventDefault(); // Sayfanın yeniden yüklenmesini engeller

        const title = document.getElementById('title').value;
        const options = Array.from(document.querySelectorAll('input[name="options[]"]'))
            .map(option => option.value)
            .filter(value => value.trim() !== ''); // Boş olmayan seçenekleri filtreler

        if (options.length < 2) {
            alert('Please add at least two options.');
            return;
        }

        const data = {
            title: title,
            options: options
        };

        fetch(form.action, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(), // CSRF tokenını alır
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = "{% url 'poll-page' %}";
            } else {
                alert('There was an error creating the poll.');
            }
        })
        .catch(error => console.error('Error:', error));
    });
});

function addOption() {
    const additionalOptions = document.getElementById('additional-options');
    const optionCount = additionalOptions.childElementCount + 3; // 3 sabit seçenek olduğu için
    const newOption = document.createElement('div');
    newOption.innerHTML = `<label for="option${optionCount}">Poll Option ${optionCount}:</label>
                           <input type="text" id="option${optionCount}" name="options[]" required><br>`;
    additionalOptions.appendChild(newOption);
}

function checkExistingAnswer() {
    Object.keys(userAnswers).forEach(pollId => {
        // Eğer kullanıcının bu ankette bir cevabı varsa
        if (userAnswers[pollId]) {
            userAnswers[pollId].forEach(option => {
                // Bu poll ID'sine sahip tüm düğmeleri al
                const buttons = document.querySelectorAll(`button[data-poll-id="${pollId}"]`);

                buttons.forEach(button => {
                    // Eğer düğme seçili seçeneğe eşitse, "selected" sınıfını ekle
                    if (button.textContent.trim() === option) {
                        button.classList.add('selected');
                    }
                });
            });
        }
    });
}

function answerPoll(pollId, selectedOption, buttonElement) {
    const data = {
        poll_id: pollId,
        answer: selectedOption
    };

    const url = '/answer-poll/';

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Sonuçları güncelle
            renderResults(pollId, data.results);
            
            // Seçilen seçeneğe "selected" class'ı ekle
            const buttons = document.querySelectorAll(`button[data-poll-id="${pollId}"]`);
            buttons.forEach(button => button.classList.remove('selected'));  // Önceki seçili durumu temizle
            buttonElement.classList.add('selected');  // Seçilen seçeneği işaretle
        } else {
            alert(data.error || 'There was an error submitting your answer.');
        }
    })
    .catch(error => console.error('Error:', error));
}

function renderResults(pollId, results) {
    const resultsDiv = document.getElementById(`results-${pollId}`);
    resultsDiv.innerHTML = ''; // Önceki sonuçları temizle

    for (const option in results) {
        const percentage = results[option].toFixed(2);
        const resultItem = document.createElement('div');
        resultItem.textContent = `${option}: ${percentage}%`;
        resultsDiv.appendChild(resultItem);
    }
}

// Get Results butonuna tıklama işlevi
function getResults(pollId) {
    fetch(`/polls/results/${pollId}/`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            renderResults(pollId, data.results);
        } else {
            alert(data.error || 'There was an error fetching results.');
        }
    })
    .catch(error => console.error('Error:', error));
}


function togglePopup() {
    const popup = document.getElementById('poll-popup');
    popup.style.display = (popup.style.display === 'block') ? 'none' : 'block';
}

function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}
