const { test, expect } = require('@playwright/test');

test('Night mode toggle works', async ({ page }) => {
    // Navigate to the local test server
    await page.goto('http://127.0.0.1:8080');

    // Check the initial state (should be light mode)
    const bodyClass = await page.evaluate(() => document.body.className);
    expect(bodyClass).not.toContain('nightmode-body');

    // Click the night mode button
    await page.click('.night-day-button');

    // Check if night mode is applied
    const updatedBodyClass = await page.evaluate(() => document.body.className);
    expect(updatedBodyClass).toContain('nightmode-body');

    // Click the night mode button again to toggle back
    await page.click('.night-day-button');

    // Check if night mode is removed
    const finalBodyClass = await page.evaluate(() => document.body.className);
    expect(finalBodyClass).not.toContain('nightmode-body');
}); 