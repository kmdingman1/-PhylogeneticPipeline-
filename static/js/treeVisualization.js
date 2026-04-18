// Wires up the upload button, posts the FASTA file to the Flask backend,
// and renders the returned ASCII phylogenetic tree.

(function () {
    const fileInput = document.getElementById('fileInput');
    const uploadButton = document.getElementById('uploadButton');
    const uploadButtonLabel = document.getElementById('uploadButtonLabel');
    const statusEl = document.getElementById('status');
    const resultsEl = document.getElementById('results');
    const resultsFilename = document.getElementById('resultsFilename');
    const resultsCount = document.getElementById('resultsCount');
    const asciiTreeEl = document.getElementById('asciiTree');

    function setStatus(message, type) {
        statusEl.textContent = message || '';
        statusEl.className = 'status' + (type ? ' status--' + type : '');
    }

    function setBusy(busy) {
        uploadButton.disabled = busy;
        uploadButtonLabel.textContent = busy ? 'Processing...' : 'Upload FASTA File';
    }

    uploadButton.addEventListener('click', function () {
        fileInput.click();
    });

    fileInput.addEventListener('change', async function () {
        const file = fileInput.files && fileInput.files[0];
        if (!file) return;

        resultsEl.hidden = true;
        asciiTreeEl.textContent = '';
        setStatus('Uploading ' + file.name + '...');
        setBusy(true);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData,
            });

            const payload = await response.json().catch(() => ({}));

            if (!response.ok) {
                const msg = payload && payload.error
                    ? payload.error
                    : 'Upload failed (HTTP ' + response.status + ')';
                setStatus(msg, 'error');
                return;
            }

            // Render results
            resultsFilename.textContent = payload.filename || file.name;
            resultsCount.textContent = payload.num_sequences
                ? payload.num_sequences + ' sequences'
                : '';
            asciiTreeEl.textContent = payload.ascii_tree || '(no tree returned)';
            resultsEl.hidden = false;
            setStatus('Tree built successfully.', 'success');
        } catch (err) {
            setStatus('Network error: ' + err.message, 'error');
        } finally {
            setBusy(false);
            // Allow re-uploading the same file
            fileInput.value = '';
        }
    });
})();
