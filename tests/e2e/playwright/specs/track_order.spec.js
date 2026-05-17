// tests/e2e/track_order.spec.js
import { test, expect } from '@playwright/test';
import { MenuPage } from './pages/MenuPage.js';
import { CheckoutPage } from './pages/CheckoutPage.js';
import { TrackPage } from './pages/TrackPage.js';

test('Customer sees live order progress', async ({ page }) => {
    // Place an order
    const menuPage = new MenuPage(page);
    await menuPage.goto();
    await menuPage.addFirstAvailableItem(1);
    
    const checkoutPage = new CheckoutPage(page);
    await checkoutPage.goto();
    await checkoutPage.fillCustomerName('Track Test');
    await checkoutPage.placeOrder();
    const orderId = await checkoutPage.getOrderId();
    
    // Navigate to tracking
    const trackPage = new TrackPage(page);
    await trackPage.goto(orderId);
    const status = await trackPage.getStatusText();
    expect(['pending', 'preparing']).toContain(status);
    
    const completedSteps = await trackPage.getCompletedSteps();
    expect(completedSteps).toBeGreaterThanOrEqual(1);
});