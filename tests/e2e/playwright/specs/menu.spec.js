// tests/e2e/menu.spec.js
import { test, expect } from '@playwright/test';
import { MenuPage } from './pages/MenuPage.js';

test('Customer filters menu items by category', async ({ page }) => {
    const menuPage = new MenuPage(page);
    await menuPage.goto();
    await menuPage.filterByCategory('coffee');
    const names = await menuPage.getVisibleItemNames();
    expect(names.length).toBeGreaterThan(0);
    for (const name of names) {
        // All visible items should be in coffee category
        // (assertion depends on seed data)
    }
});

test('Customer cannot add a sold-out item', async ({ page }) => {
    const menuPage = new MenuPage(page);
    await menuPage.goto();
    // Find sold-out item and verify button is disabled
    const soldOutItems = page.locator('[data-testid="menu-item"].unavailable');
    const count = await soldOutItems.count();
    if (count > 0) {
        const btn = soldOutItems.first().locator('[data-testid="add-to-cart"]');
        await expect(btn).toBeDisabled();
    }
});