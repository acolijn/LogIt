// /*
// * This script is used to change the text of an entry.
// * It uses CKEditor to provide a rich text editor.
// */

// let currentEntryId = null;

// ckeditor_toolbar = [
//     {name: 'clipboard', items: ['Cut', 'Copy', 'Paste', '-', 'Undo', 'Redo'] },
//     { name: 'editing', items: ['Find', 'Replace'] },
//     { name: 'basicstyles', items: ['Bold', 'Italic', 'Underline', 'Strike', 'RemoveFormat'] },
//     { name: 'paragraph', items: ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote'] },
//     { name: 'styles', items: ['Format', 'Font', 'FontSize'] },
// ]


// function destroyCKEditor() {
//     // Destroy the CKEditor instance if it exists
//     if (CKEDITOR.instances.ckeditorArea) {
//         CKEDITOR.instances.ckeditorArea.destroy();
//     }
// }


// function openEditor(element) {
//     /*
//     * Open the modal and populate the CKEditor instance with the original text
//     * of the entry.
//     */
//     destroyCKEditor();

//     const entryId = element.getAttribute('data-entry-id');
//     const originalText = element.getAttribute('data-entry-text');

//     currentEntryId = entryId;

//     // Create the CKEditor instance with custom toolbar configuration
//     CKEDITOR.replace('ckeditorArea', {
//         toolbar: ckeditor_toolbar
//     }).setData(originalText);
//     $('#editorModal').modal('show');
// }

// function saveEditing() {
//     /*
//     * Get the updated text from the CKEditor instance and send it to the server
//     * to update the entry.
//     * Then close the modal and reload the page.
//     */
//     const updatedText = CKEDITOR.instances.ckeditorArea.getData();
//     updateEntryText(currentEntryId, updatedText);
//     $('#editorModal').modal('hide');
// }

// function cancelEditing() {
//     /*
//     * Close the modal and destroy the CKEditor instance.
//     */
//     CKEDITOR.instances.ckeditorArea.destroy();
//     $('#editorModal').modal('hide');
// }

// function updateEntryText(entryId, updatedText) {
//     /*
//     * Send the updated text to the server to update the entry.
//     */

//     // Use AJAX or fetch API to send the updated text to the server
//     fetch('/update_entry/' + entryId, {
//         method: 'POST',
//         body: JSON.stringify({ updated_text: updatedText }),
//         headers: { 'Content-Type': 'application/json' }
//     })
//     .then(response => {
//         if (response.ok) {
//             // Reload the current page to reflect the changes
//             location.reload();
//         } else {
//             console.error('Failed to update entry:', response.statusText);
//         }
//     });
// }

// // Attach an event listener to your modal to handle the 'hidden.bs.modal' event
// $('#editorModal').on('hidden.bs.modal', function (e) {
//     destroyCKEditor();  // Destroy the CKEditor instance when the modal is closed
// });


let currentEntryId = null;
let editorInstance = null; // This will hold our CKEditor 5 instance

function destroyCKEditor() {
    // Destroy the CKEditor instance if it exists
    if (editorInstance) {
        editorInstance.destroy()
            .then(() => editorInstance = null)
            .catch(error => console.error('Error destroying editor:', error));
    }
}

function openEditor(element) {
    /*
    * Open the modal and populate the CKEditor instance with the original text
    * of the entry.
    */
    destroyCKEditor();

    const entryId = element.getAttribute('data-entry-id');
    const originalText = element.getAttribute('data-entry-text');

    currentEntryId = entryId;

    ClassicEditor
        .create(document.querySelector('#ckeditorArea'), {
            toolbar: ['undo', 'redo', '|', 'bold', 'italic', 'underline', 'strike', 'removeFormat', '|', 'numberedList', 'bulletedList', '|', 'outdent', 'indent', 'blockquote', '|', 'heading', '|', 'fontColor', 'fontSize']
        })
        .then(editor => {
            editorInstance = editor;
            editor.setData(originalText); // Set the data after creating the instance
            $('#editorModal').modal('show');
        })
        .catch(error => {
            console.error('Error creating editor:', error);
        });
}

function saveEditing() {
    /*
    * Get the updated text from the CKEditor instance and send it to the server
    * to update the entry.
    * Then close the modal and reload the page.
    */
    const updatedText = editorInstance.getData();
    updateEntryText(currentEntryId, updatedText);
    $('#editorModal').modal('hide');
}

function cancelEditing() {
    /*
    * Close the modal and destroy the CKEditor instance.
    */
    destroyCKEditor();
    $('#editorModal').modal('hide');
}

function updateEntryText(entryId, updatedText) {
    /*
    * Send the updated text to the server to update the entry.
    */
    fetch('/update_entry/' + entryId, {
        method: 'POST',
        body: JSON.stringify({ updated_text: updatedText }),
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => {
        if (response.ok) {
            // Reload the current page to reflect the changes
            location.reload();
        } else {
            console.error('Failed to update entry:', response.statusText);
        }
    });
}

// Attach an event listener to your modal to handle the 'hidden.bs.modal' event
$('#editorModal').on('hidden.bs.modal', function (e) {
    destroyCKEditor();  // Destroy the CKEditor instance when the modal is closed
});
