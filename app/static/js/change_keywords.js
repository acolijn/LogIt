/*
    This file contains the functions that are used to open the modal to change the keywords of an entry.
    It also contains the function that is used to send the updated keywords to the server.
*/

function openKeywordModal(entryId) {
    /*
    * Open the modal and populate the list of keywords.
    * The list of keywords is fetched from the server.
    *   
    * The list of keywords that are currently assigned to the entry is also fetched from the server.
    * The keywords that are currently assigned to the entry are marked as selected.
    * 
    */
    Promise.all([
        fetch('/get-keywords').then(response => {
            if (!response.ok) throw Error('Error fetching keywords: ' + response.statusText);
            return response.json();
        }),
        fetch('/get-entry-keywords/' + entryId).then(response => {
            if (!response.ok) throw Error('Error fetching entry keywords: ' + response.statusText);
            return response.json();
        })
    ]).then(([allowedKeywords, currentKeywords]) => {
        const keywordList = document.getElementById('keywordList');
        keywordList.innerHTML = ''; // Clear any previous keywords.
        allowedKeywords.keywords.forEach(keyword => {
            const listItem = document.createElement('li');
            listItem.textContent = keyword;
            listItem.className = 'keyword-item'; // Add a class to style it.
            if (currentKeywords.keywords.includes(keyword)) {
                listItem.classList.add('selected'); // Add selected class if the keyword is in the entry's current keywords.
            }
            listItem.onclick = function () {
                this.classList.toggle('selected'); // Toggle selected class on click.
            };
            keywordList.appendChild(listItem);
        });

        const modalElement = document.getElementById('keywordModal');
        const modalInstance = new bootstrap.Modal(modalElement);
        modalInstance.show(); // This uses Bootstrap's method to show the modal.

        modalElement.dataset.entryId = entryId; // Store entryId in the modal to use it in updateKeywords function.
    }).catch(error => {
        console.error(error); // Log any error that occurred during the fetch.
    });
}


function updateKeywords() {
    /*
    * Get the list of selected keywords and send it to the server to update the entry.
    * Then close the modal and reload the page.
    * 
    */
    const modal = document.getElementById('keywordModal');
    const entryId = modal.dataset.entryId;
    const selectedKeywords = Array.from(modal.querySelectorAll('.keyword-item.selected'))
        .map(li => li.textContent); // Only send those that have the 'selected' class.

    if (selectedKeywords.length === 0) {
        // If no keywords are selected, consider "None" as a selected keyword.
        selectedKeywords.push('None');
    }

    // Use AJAX or fetch API to send the updated keywords to the server
    fetch('/update-entry-keywords/' + entryId, {
        method: 'POST',
        body: JSON.stringify({ keywords: selectedKeywords }),
        headers: { 'Content-Type': 'application/json' }
    }).then(response => {
        if (response.ok) {
            // Reload the current page to reflect the changes
            location.reload();
        } else {
            // If the response is not OK, show an alert.
            alert('Failed to update keywords');
        }
    });
    const modalElement = document.getElementById('keywordModal');
    const modalInstance = new bootstrap.Modal(modalElement);
    modalInstance.hide(); // This uses Bootstrap's method to hide the modal.
}

function closeModal() {
    /*
    * Close the modal.
    */
    document.getElementById('keywordModal').style.display = 'none';
}