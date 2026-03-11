/* =================================
   SMARTMARKET MVP FRONTEND
================================= */

/* ---------- API CONFIG ---------- */

const BASE_URL = "http://127.0.0.1:8000";

const API = {
    products: `${BASE_URL}/api/products`,
    registerShop: `${BASE_URL}/api/shop/register`,
    stats: `${BASE_URL}/api/stats`,
    recommendations: `${BASE_URL}/api/recommendations`,
    order: `${BASE_URL}/api/order`,
    addProduct: `${BASE_URL}/api/product/add`
};

/* ---------- GLOBAL STATE ---------- */

const state = {
    products: [],
    stats: null
};

/* =================================
   API REQUEST HELPER
================================= */

async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                "Content-Type": "application/json"
            },
            ...options
        });

        if (!response.ok) {
            throw new Error("API request failed");
        }

        return await response.json();

    } catch (error) {
        console.error("API ERROR:", error);
        alert("Ошибка соединения с сервером");
        return null;
    }
}

/* =================================
   PRODUCTS
================================= */

async function loadProducts() {

    const data = await apiRequest(API.products);
    if (!data) return;

    state.products = data;
    renderProducts();
}

function renderProducts() {

    const grid = document.getElementById("productGrid");
    grid.innerHTML = "";

    state.products.forEach(product => {

        const card = document.createElement("div");
        card.className = "product-card";

        card.innerHTML = `
            <img src="${product.image}" alt="${product.name}">
            <h3>${product.name}</h3>
            <p>${product.price} ₸</p>
            <button>Купить</button>
        `;

        card.querySelector("button")
            .addEventListener("click", () => orderProduct(product.id));

        grid.appendChild(card);
    });
}

/* =================================
   ORDER PRODUCT
================================= */

async function orderProduct(productId) {

    const result = await apiRequest(API.order, {
        method: "POST",
        body: JSON.stringify({
            product_id: productId
        })
    });

    if (result) {
        alert("Заказ оформлен ✅");
        loadStats();
    }
}

/* =================================
   SHOP REGISTRATION
================================= */

async function registerShop(event) {

    event.preventDefault();

    const payload = {
        name: document.getElementById("shopName").value,
        owner: document.getElementById("ownerName").value,
        contact: document.getElementById("contact").value
    };

    const result = await apiRequest(API.registerShop, {
        method: "POST",
        body: JSON.stringify(payload)
    });

    if (result) {
        alert("Магазин создан 🚀");
        event.target.reset();
        loadStats();
    }
}

/* =================================
   ADD PRODUCT (SELLER)
================================= */

async function addProduct(event) {

    event.preventDefault();

    const payload = {
        name: document.getElementById("productName").value,
        price: Number(document.getElementById("productPrice").value),
        image: document.getElementById("productImage").value
    };

    const result = await apiRequest(API.addProduct, {
        method: "POST",
        body: JSON.stringify(payload)
    });

    if (result) {
        alert("Товар добавлен ✅");
        event.target.reset();
        loadProducts();
        loadStats();
    }
}

/* =================================
   STATS
================================= */

async function loadStats() {

    const data = await apiRequest(API.stats);
    if (!data) return;

    state.stats = data;

    document.getElementById("salesCount").innerText = data.sales;
    document.getElementById("usersCount").innerText = data.users;
    document.getElementById("productsCount").innerText = data.products;
}

/* =================================
   AI RECOMMENDATIONS
================================= */

async function loadRecommendations() {

    const data = await apiRequest(API.recommendations);
    if (!data) return;

    const box = document.getElementById("aiRecommendations");

    box.innerHTML = `
        <h4>🤖 AI Анализ спроса</h4>
        <pre>${data.text}</pre>
    `;
}

/* =================================
   EVENTS
================================= */

function bindEvents() {

    // регистрация магазина
    document
        .getElementById("shopForm")
        .addEventListener("submit", registerShop);

    // добавление товара
    document
        .getElementById("productForm")
        .addEventListener("submit", addProduct);

    // AI рекомендации
    document
        .getElementById("aiBtn")
        .addEventListener("click", loadRecommendations);
}

/* =================================
   INIT APP
================================= */

async function init() {
    bindEvents();
    await loadProducts();
    await loadStats();
}

document.addEventListener("DOMContentLoaded", init);