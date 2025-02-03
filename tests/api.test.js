const { test, expect } = require('@playwright/test');

test.describe('Wikipedia API Tests', () => {
    test('search form returns Wikipedia summary', async ({ page }) => {
        // Navigate to Stage 5 page
        await page.goto('http://127.0.0.1:8080/five');

        // Get the search form elements
        const searchInput = page.locator('#searchInput');
        const searchForm = page.locator('#searchForm');

        // Type a test search term
        await searchInput.fill('JavaScript');

        // Submit the form
        await searchForm.evaluate(form => form.dispatchEvent(new Event('submit')));

        // Wait for the result to appear
        const searchResult = page.locator('#searchResult');
        await expect(searchResult).toBeVisible();

        // Get the result text
        const resultText = await searchResult.textContent();

        // Verify that we got a non-empty response
        try {
            expect(resultText.length).toBeGreaterThan(0);
            expect(resultText).toContain('JavaScript');
        } catch (error) {
            console.log('Received text:', resultText);
            throw error;
        }
    });

    test('handles invalid search terms gracefully', async ({ page }) => {
        // Navigate to Stage 5 page
        await page.goto('http://127.0.0.1:8080/five');

        // Get the search form elements
        const searchInput = page.locator('#searchInput');
        const searchForm = page.locator('#searchForm');

        // Type an invalid search term
        await searchInput.fill('thisisnotarealwikipediaarticle12345');

        // Submit the form
        await searchForm.evaluate(form => form.dispatchEvent(new Event('submit')));

        // Wait for the result to appear
        const searchResult = page.locator('#searchResult');
        await expect(searchResult).toBeVisible();

        // Get the result text
        const resultText = await searchResult.textContent();

        // Verify that we got an error message
        try {
            expect(resultText).toContain('error');
        } catch (error) {
            console.log('Received text:', resultText);
            throw error;
        }
    });
});