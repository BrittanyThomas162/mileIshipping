document.addEventListener('DOMContentLoaded', function() {
    const prealertSelect = document.getElementById('prealert_id');
    prealertSelect.addEventListener('change', function() {
        const prealertId = prealertSelect.value;
        if (prealertId != 0) {
            fetch(`/api/prealert/${prealertId}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('tracking_number').value = data.tracking_number;
                    document.getElementById('first_name').value = data.first_name;
                    document.getElementById('last_name').value = data.last_name;
                    document.getElementById('description').value = data.description;
                    document.getElementById('sender').value = data.sender;
                    const invoiceLink = document.getElementById('invoice_link');
                    if (data.invoice) {
                        invoiceLink.href = `/uploads/${data.invoice}`;
                        invoiceLink.classList.remove('d-none');
                    } else {
                        invoiceLink.classList.add('d-none');
                    }
                });
        }
    });
});



