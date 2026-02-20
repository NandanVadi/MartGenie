window.storeCatalog = {
    "MARTGENIE-STORE-001": [
        {
            "id": "PROD001",
            "name": "Maggi Noodles",
            "price": 14.0,
            "category": "Food",
            "barcode": "8901058000001"
        },
        {
            "id": "PROD002",
            "name": "Coca Cola 750ml",
            "price": 40.0,
            "category": "Beverages",
            "barcode": "8901058000002"
        },
        {
            "id": "PROD003",
            "name": "Good Day Biscuit",
            "price": 20.0,
            "category": "Food",
            "barcode": "8901058000003"
        },
        {
            "id": "PROD004",
            "name": "Colgate Toothpaste",
            "price": 65.0,
            "category": "Personal Care",
            "barcode": "8901058000004"
        },
        {
            "id": "PROD005",
            "name": "Dettol Soap",
            "price": 35.0,
            "category": "Personal Care",
            "barcode": "8901058000005"
        }
    ]
};

window.mockProducts = window.storeCatalog["MARTGENIE-STORE-001"];

window.fetchProducts = (storeCode) => {
    return new Promise((resolve) => {
        setTimeout(() => {
            const normalized = (storeCode || '').trim().toUpperCase();
            if (!normalized || !window.storeCatalog[normalized]) {
                resolve([]);
                return;
            }
            resolve(window.storeCatalog[normalized]);
        }, 500);
    });
};
