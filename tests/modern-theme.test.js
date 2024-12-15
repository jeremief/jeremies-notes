const { test, expect } = require('@playwright/test');

test.describe('Modern Theme Tests', () => {
  test('modern theme button toggles theme correctly', async ({ page }) => {
    // Navigate to the home page with full URL
    await page.goto('http://127.0.0.1:8080');

    // Get the theme toggle button
    const themeButton = page.locator('.theme-toggle-button');
    
    // Verify button exists and has correct initial text
    await expect(themeButton).toBeVisible();
    await expect(themeButton).toHaveText('Modern Theme');

    // Click the theme button
    await themeButton.click();

    // Check if modern theme class is added to body
    await expect(page.locator('body')).toHaveClass(/modern-theme/);

    // Verify theme preference is saved in localStorage
    const themePreference = await page.evaluate(() => {
      return localStorage.getItem('modernTheme');
    });
    expect(themePreference).toBe('true');

    // Click again to toggle off
    await themeButton.click();

    // Check if modern theme class is removed
    await expect(page.locator('body')).not.toHaveClass(/modern-theme/);

    // Verify localStorage is updated
    const updatedPreference = await page.evaluate(() => {
      return localStorage.getItem('modernTheme');
    });
    expect(updatedPreference).toBe('false');
  });

  test('modern theme persists across page reloads', async ({ page }) => {
    // Navigate to home page with full URL
    await page.goto('http://127.0.0.1:8080');

    // Enable modern theme
    await page.locator('.theme-toggle-button').click();

    // Reload the page
    await page.reload();

    // Verify modern theme is still applied
    await expect(page.locator('body')).toHaveClass(/modern-theme/);
  });
}); 