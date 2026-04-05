document.addEventListener('DOMContentLoaded', function() {
    const urlInput = document.getElementById('id_akakce_url');
    if (!urlInput) return;

    // Create Fetch Button
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.innerText = 'Smart Fetch / جلب ذكي';
    btn.className = 'button';
    btn.style.marginLeft = '10px';
    btn.style.backgroundColor = '#fbbf24';
    btn.style.color = '#000';
    btn.style.fontWeight = 'bold';

    // Container for the button
    urlInput.parentNode.appendChild(btn);

    const statusMsg = document.createElement('span');
    statusMsg.style.marginLeft = '10px';
    statusMsg.style.fontSize = '12px';
    urlInput.parentNode.appendChild(statusMsg);

    btn.onclick = async function() {
        const url = urlInput.value.trim();
        if (!url) {
            alert('الرجاء إدخال رابط أولاً');
            return;
        }

        btn.disabled = true;
        statusMsg.innerText = 'جاري الجلب...';
        statusMsg.style.color = 'blue';

        try {
            const response = await fetch('/api/products/scrape/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({ url: url })
            });

            const data = await response.json();

            if (data.success) {
                // Fill fields
                if (document.getElementById('id_name_ar')) document.getElementById('id_name_ar').value = data.name;
                if (document.getElementById('id_name_tr')) document.getElementById('id_name_tr').value = data.name;
                if (document.getElementById('id_price')) document.getElementById('id_price').value = data.price;
                if (document.getElementById('id_image_url')) document.getElementById('id_image_url').value = data.image;
                if (document.getElementById('id_description_ar')) document.getElementById('id_description_ar').value = data.description;
                if (document.getElementById('id_description_tr')) document.getElementById('id_description_tr').value = data.description;
                
                statusMsg.innerText = 'تم الجلب بنجاح!';
                statusMsg.style.color = 'green';
            } else {
                statusMsg.innerText = 'خطأ: ' + (data.message || 'فشل الجلب');
                statusMsg.style.color = 'red';
                alert('فشل الجلب: ' + (data.message || 'Unknown error'));
            }
        } catch (error) {
            console.error('Fetch error:', error);
            statusMsg.innerText = 'فشل الاتصال بالخادم';
            statusMsg.style.color = 'red';
        } finally {
            btn.disabled = false;
        }
    };
});
