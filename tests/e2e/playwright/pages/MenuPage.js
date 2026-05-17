// tests/e2e/pages/MenuPage.js
export class MenuPage {
    constructor(page) {
        this.page = page;
        this.categoryFilter = page.locator('[data-testid="category-filter"]');
        this.menuItems = page.locator('[data-testid="menu-item"]');
        this.addToCartButtons = page.locator('[data-testid="add-to-cart"]');
    }

    async goto() {
        await this.page.goto('http://localhost:5000/menu.html');
    }

    async filterByCategory(category) {
        await this.categoryFilter.selectOption(category);
        await this.page.waitForTimeout(300); // allow render
    }

    async getVisibleItemNames() {
        return await this.menuItems.locator('.item-name').allTextContents();
    }

    async addFirstAvailableItem(quantity = 1) {
        const btn = this.addToCartButtons.first();
        await btn.click();
        if (quantity > 1) {
            await this.page.locator('[data-testid="qty-input"]').fill(String(quantity));
            await this.page.locator('[data-testid="confirm-add"]').click();
        }
    }
}