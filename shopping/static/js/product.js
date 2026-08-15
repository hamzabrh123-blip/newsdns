// ================= MERGED PRODUCT & ZOOM SCRIPT =================

function syncVariant(el) {
    try {
        const mainImg = document.getElementById('mainProductImg');
        const result = document.getElementById("zoomResult");
        const dataScript = document.getElementById('nestedDealsData');

        if (!dataScript) return;

        const allData = JSON.parse(dataScript.textContent);
        const code = el.getAttribute('data-code');
        const deals = allData[code];

        // Image Change via Cloudinary
        const rawUrl = el.getAttribute('data-raw-url');
        const imgUrl = "https://res.cloudinary.com/dvoqsrkkq/image/fetch/f_auto,q_auto/" + rawUrl;
        mainImg.src = imgUrl;
        
        // Hide zoom result temporarily on variant switch
        if (result) result.style.display = 'none';

        // Product Code Update
        const codeDisplay = document.getElementById('displayVariantCode');
        if (codeDisplay) codeDisplay.innerText = code;

        const container = document.getElementById('storeDealsContainer');
        const shopBtn = document.getElementById('masterShopNowBtn');

        if (container && deals && deals.length > 0) {
            container.innerHTML = deals.map(d =>
                `<tr>
                    <td>${d.store_name}</td>
                    <td>${d.coupon_code}</td>
                    <td><strong>${d.currency}${d.selling_price}</strong></td>
                </tr>`
            ).join('');

            if (shopBtn) {
                shopBtn.href = deals[0].url;

                let store = deals[0].store_name || "SHOP";
                store = store
                    .replace(/\.co\.in$/i, "")
                    .replace(/\.com$/i, "")
                    .replace(/\.in$/i, "")
                    .trim();

                const storeKey = store
                    .toLowerCase()
                    .replace(/\s+/g, "")
                    .replace(/[-_.]/g, "");

                shopBtn.innerHTML = `
                    <div style="display:flex;align-items:center;justify-content:center; width:100%; height:100%; gap:12px;">
                        <span style="font-size:22px;font-weight:800;letter-spacing:1px;">SHOP NOW</span>
                        <img src="/static/store_logo/${storeKey}.png" onerror="this.src='/static/store_logo/default.png'"
                        style="height:100%; max-height:42px; width:auto; object-fit:contain;">
                    </div>`;

                shopBtn.className = "btn-main-shop-now";

                switch (store.toLowerCase()) {
                    case "amazon":
                        shopBtn.style.background = "#FF9900";
                        shopBtn.style.color = "#000";
                        break;
                    case "flipkart":
                        shopBtn.style.background = "#2874F0";
                        shopBtn.style.color = "#fff";
                        break;
                    case "myntra":
                        shopBtn.style.background = "#ff3f6c";
                        shopBtn.style.color = "#fff";
                        break;
                    case "ajio":
                        shopBtn.style.background = "#000";
                        shopBtn.style.color = "#fff";
                        break;
                    case "meesho":
                        shopBtn.style.background = "#9C27B0";
                        shopBtn.style.color = "#fff";
                        break;
                    case "nykaa":
                        shopBtn.style.background = "#fc2779";
                        shopBtn.style.color = "#fff";
                        break;
                    case "croma":
                        shopBtn.style.background = "#00A651";
                        shopBtn.style.color = "#fff";
                        break;
                    case "tatacliq":
                        shopBtn.style.background = "#D61F2C";
                        shopBtn.style.color = "#fff";
                        break;
                    case "reliancedigital":
                        shopBtn.style.background = "#1565C0";
                        shopBtn.style.color = "#fff";
                        break;
                    default:
                        shopBtn.style.background = "#ff9900";
                        shopBtn.style.color = "#000";
                }
            }
        }

        document.querySelectorAll(".thumb-img").forEach(t => t.classList.remove("thumb-active"));
        el.classList.add("thumb-active");

        // Trigger Zoom after image loads completely
        mainImg.onload = function () {
            if (window.innerWidth > 768 && typeof initZoom === "function") {
                initZoom("mainProductImg", "zoomResult");
            }
        };

        if (mainImg.complete) {
            if (window.innerWidth > 768 && typeof initZoom === "function") {
                initZoom("mainProductImg", "zoomResult");
            }
        }

    } catch (err) {
        console.error("Sync Error:", err);
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const firstThumb = document.querySelector(".thumb-img");
    if (firstThumb) {
        syncVariant(firstThumb);
    }
});


// ================= FOOLPROOF DIRECT ZOOM & MOVEMENT SCRIPT =================

function initZoom(imgID, resultID) {
    const img = document.getElementById(imgID);
    const result = document.getElementById(resultID);
    const viewport = img.parentElement; // .main-img-viewport

    if (!img || !result || !viewport) return;

    // Purana lens agar CSS mein ho toh hata do taaki rukaavat na ho
    const existingLens = viewport.querySelector(".img-zoom-lens");
    if (existingLens) existingLens.remove();

    let tempImg = new Image();
    tempImg.src = img.src;

    tempImg.onload = setup;
    if (img.complete) setup();

    function setup() {
        result.style.backgroundImage = `url('${img.src}')`;
        // Zoom bada karne ke liye yahan multiplier set hai (e.g., 2.5x)
        const zoomFactor = 2.5; 
        result.style.backgroundSize = `${tempImg.width * zoomFactor}px ${tempImg.height * zoomFactor}px`;
    }

    viewport.onmouseenter = function() {
        result.style.display = "block";
    };

    viewport.onmouseleave = function() {
        result.style.display = "none";
    };

    viewport.onmousemove = function(e) {
        const rect = img.getBoundingClientRect();
        
        // Mouse position inside the image
        let x = e.clientX - rect.left;
        let y = e.clientY - rect.top;

        // Agar mouse image ke bahar ho toh roko
        if (x < 0 || y < 0 || x > rect.width || y > rect.height) {
            result.style.display = "none";
            return;
        } else {
            result.style.display = "block";
        }

        // Percentage calculation for smooth movement
        let xPercent = x / rect.width;
        let yPercent = y / rect.height;

        let bgWidth = parseInt(result.style.backgroundSize.split(' ')[0]) || (img.naturalWidth * 2.5);
        let bgHeight = parseInt(result.style.backgroundSize.split(' ')[1]) || (img.naturalHeight * 2.5);

        let bgX = xPercent * (bgWidth - result.offsetWidth);
        let bgY = yPercent * (bgHeight - result.offsetHeight);

        result.style.backgroundPosition = `-${bgX}px -${bgY}px`;
    };
}