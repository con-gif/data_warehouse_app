document.addEventListener('DOMContentLoaded', function () {
    const loadingScreen = document.getElementById('loading-screen');
    const loadingBar = document.querySelector('.loading-bar');
    const loadingText = document.querySelector('.loading-text');
    const downloadSection = document.getElementById('download-section'); // Container for download button

    function showLoadingScreen() {
        loadingScreen.classList.add('active');
        updateProgressBar(0); // Reset progress bar
    }

    function hideLoadingScreen() {
        loadingScreen.classList.remove('active');
    }

    function updateProgressBar(progress) {
        loadingBar.style.width = `${progress}%`;
        loadingText.textContent = `Uploading... ${progress}%`;
    }

    function showDownloadButton(downloadUrl) {
        // Clear any previous buttons
        downloadSection.innerHTML = '';

        // Create a new download button
        const downloadButton = document.createElement('a');
        downloadButton.href = downloadUrl;
        downloadButton.textContent = 'Download Formatted File';
        downloadButton.classList.add('btn', 'btn-primary');
        downloadButton.target = '_blank'; // Open in a new tab

        // Append to the download section
        downloadSection.appendChild(downloadButton);
    }

    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (event) => {
            event.preventDefault();
            const formData = new FormData(form);
            const xhr = new XMLHttpRequest();

            xhr.open(form.method, form.action, true);

            // Update progress bar
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percentComplete = Math.round((e.loaded / e.total) * 100);
                    updateProgressBar(percentComplete);
                }
            });

            // Handle upload completion
            xhr.addEventListener('load', () => {
                hideLoadingScreen();
                if (xhr.status === 200) {
                    const response = JSON.parse(xhr.responseText);
                    if (response.download_url) {
                        showDownloadButton(response.download_url);
                    }
                    alert(response.message || 'Upload successful!');
                } else {
                    alert(`Error uploading file: ${xhr.responseText}`);
                }
            });

            // Handle errors
            xhr.addEventListener('error', () => {
                hideLoadingScreen();
                alert('An error occurred during upload.');
            });

            showLoadingScreen();
            xhr.send(formData);
        });
    });
    
});
