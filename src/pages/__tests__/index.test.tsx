import * as React from "react";

import { render, screen } from "@testing-library/react";
import IndexPage from "../index";

it("renders a table", () => {
  render(<IndexPage />);

  expect(screen.queryByText("Cutover Start Date")).toBeTruthy();
  expect(screen.queryByText("Cutover End Date")).toBeTruthy();
  expect(screen.queryByText("Practice Name")).toBeTruthy();
  expect(screen.queryByText("Source System")).toBeTruthy();
  expect(screen.queryByText("Target System")).toBeTruthy();
  expect(screen.queryByText("Cutover Duration (Days)")).toBeTruthy();
});
