import { expect, test } from "@playwright/test";

test("renders Time and confirms the real API liveness endpoint", async ({
  page,
}) => {
  const liveResponse = page.waitForResponse(
    (response) =>
      response.url().endsWith("/api/v1/health/live") &&
      response.status() === 200,
  );

  await page.goto("/");

  await liveResponse;
  await expect(page.getByRole("heading", { name: "Time" })).toBeVisible();
  await expect(page.getByText("服务正常")).toBeVisible();
  await expect(page.getByText("API 0.1.0")).toBeVisible();
});
