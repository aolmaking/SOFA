// tests/e2e/pages/CheckoutPage.js
export class CheckoutPage {
    constructor(page) {
        this.page = page;
        this.customerName = page.locator('[data-testid="customer-name"]');
        this.placeOrderBtn = page.locator('[data-testid="place-order"]');
        this.orderIdDisplay = page.locator('[data-testid="order-id"]');
        this.trackLink = page.locator('[data-testid="track-link"]');
    }

    async goto() {
        await this.page.goto('http://localhost:5000/checkout.html');
    }

    async fillCustomerName(name) {
        await this.customerName.fill(name);
    }

    async placeOrder() {
        await this.placeOrderBtn.click();
        await this.orderIdDisplay.waitFor({ state: 'visible', timeout: 5000 });
    }

    async getOrderId() {
        return await this.orderIdDisplay.textContent();
    }
}