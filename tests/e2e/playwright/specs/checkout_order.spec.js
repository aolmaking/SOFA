// tests/e2e/checkout_order.spec.js
import { test, expect } from '@playwright/test';
import { MenuPage } from './pages/MenuPage.js';
import { CheckoutPage } from './pages/CheckoutPage.js';

test('Customer places an order from a valid cart', async ({ page }) => {
    // Step 1: Add item to cart
    const menuPage = new MenuPage(page);
    await menuPage.goto();
    await menuPage.addFirstAvailableItem(2);
    
    // Step 2: Go to checkout and place order
    const checkoutPage = new CheckoutPage(page);
    await checkoutPage.goto();
    await checkoutPage.fillCustomerName('E2E Test Customer');
    await checkoutPage.placeOrder();
    const orderId = await checkoutPage.getOrderId();
    expect(orderId).toMatch(/^EC-[A-Z0-9]+$/);
});

test('Empty cart cannot be submitted', async ({ page }) => {
    const checkoutPage = new CheckoutPage(page);
    await checkoutPage.goto();
    await checkoutPage.fillCustomerName('Empty Cart Test');
    
    // Attempt to place order with empty cart
    await checkoutPage.placeOrderBtn.click();
    const errorToast = page.locator('[data-testid="error-toast"]');
    await expect(errorToast).toContainText('empty cart');
});