// product.js
function syncVariant(el) {
    const mainImg = document.getElementById('mainProductImg');
    const result = document.getElementById("zoomResult");
    const lens = document.getElementById("lens");
    const allData = JSON.parse(document.getElementById('nestedDealsData').textContent);
    const code = el.getAttribute('data-code');
    const deals = allData[code];

    mainImg.src = "https://res.cloudinary.com/dvoqsrkkq/image/fetch/f_auto,q_auto/" + el.getAttribute('data-raw-url');
    
    if (lens) lens.style.display = 'none';
    if (result) result.style.display = 'none';

    document.getElementById('displayVariantCode').innerText = code;
    
    if(deals) {
        document.getElementById('storeDealsContainer').innerHTML = deals.map(d => 
            `<tr><td>${d.store_name}</td><td>${d.coupon_code}</td><td><strong>₹${d.selling_price}</strong></td></tr>`
        ).join('');
        document.getElementById('masterShopNowBtn').href = deals[0].url;
    }
    
    document.querySelectorAll('.thumb-img').forEach(t => t.classList.remove('thumb-active'));
    el.classList.add('thumb-active');

    // Zoom Logic
    if (window.innerWidth > 768) {
        result.style.backgroundImage = "url('" + mainImg.src + "')";
        mainImg.onload = function() {
            result.style.backgroundSize = (this.width * 3) + "px " + (this.height * 3) + "px";
        };
        
        mainImg.onmousemove = (e) => {
            const pos = mainImg.getBoundingClientRect();
            let x = e.clientX - pos.left;
            let y = e.clientY - pos.top;
            lens.style.display = "block";
            result.style.display = "block";
            lens.style.left = (x - 50) + "px";
            lens.style.top = (y - 50) + "px";
            result.style.backgroundPosition = "-" + (x * 3 - 200) + "px -" + (y * 3 - 200) + "px";
        };
        
        mainImg.onmouseleave = () => { 
            lens.style.display = "none"; 
            result.style.display = "none"; 
        };
    }
}