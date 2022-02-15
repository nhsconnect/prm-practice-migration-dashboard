import * as React from "react";

import { render, screen } from "@testing-library/react";
import IndexPage from "../index";

jest.mock(
    "../../data/content/migrations.json",
    () => ([{
      "cutover_startdate": "01/01/2022",
      "cutover_enddate": "12/01/2022",
      "practice_name": "Bury",
      "ccg_name": "Greater Manchester",
      "source_system": "EMIS Web",
      "target_system": "TTP SystemOne",
      "cutover_duration": 12
    }]),
    { virtual: true }
);

it("renders a table", () => {
  render(<IndexPage />);

  expect(screen.queryByText("Cutover Start Date")).toBeTruthy();
  expect(screen.queryByText("Cutover End Date")).toBeTruthy();
  expect(screen.queryByText("Practice Name")).toBeTruthy();
  expect(screen.queryByText("CCG Name")).toBeTruthy();
  expect(screen.queryByText("Source System")).toBeTruthy();
  expect(screen.queryByText("Target System")).toBeTruthy();
  expect(screen.queryByText("Cutover Duration (Days)")).toBeTruthy();

  console.log(screen.debug());
  expect(screen.queryByText("01/01/2022")).toBeTruthy();
  expect(screen.queryByText("12/01/2022")).toBeTruthy();
  expect(screen.queryByText("Bury")).toBeTruthy();
  expect(screen.queryByText("Greater Manchester")).toBeTruthy();
  expect(screen.queryByText("EMIS Web")).toBeTruthy();
  expect(screen.queryByText("TTP SystemOne")).toBeTruthy();
  expect(screen.queryByText("12")).toBeTruthy();
});
