import * as React from "react";

import { render, screen } from "@testing-library/react";
import MigrationStatsTable from "../index";

const defaultMigrationStats = [
  {
    cutover_startdate: "2022-01-01T02:03:04Z",
    cutover_enddate: "2022-01-12T04:03:02Z",
    practice_name: "Bury",
    ccg_name: "Greater Manchester",
    source_system: "EMIS Web",
    target_system: "TTP SystemOne",
    cutover_duration: 12,
  },
];

jest.mock("../../data/content/migrations.json", () => defaultMigrationStats, {
  virtual: true,
});

it("renders a table", () => {
  render(<MigrationStatsTable migrationStats={defaultMigrationStats} />);

  expect(screen.queryByText("Cutover Start Date")).toBeTruthy();
  expect(screen.queryByText("Cutover End Date")).toBeTruthy();
  expect(screen.queryByText("Practice Name")).toBeTruthy();
  expect(screen.queryByText("CCG Name")).toBeTruthy();
  expect(screen.queryByText("Source System")).toBeTruthy();
  expect(screen.queryByText("Target System")).toBeTruthy();
  expect(screen.queryByText("Cutover Duration (Days)")).toBeTruthy();

  expect(screen.queryByText("01/01/2022")).toBeTruthy();
  expect(screen.queryByText("12/01/2022")).toBeTruthy();
  expect(screen.queryByText("Bury")).toBeTruthy();
  expect(screen.queryByText("Greater Manchester")).toBeTruthy();
  expect(screen.queryByText("EMIS Web")).toBeTruthy();
  expect(screen.queryByText("TTP SystemOne")).toBeTruthy();
  expect(screen.queryByText("12")).toBeTruthy();
});

it("handles missing fields", () => {
  const missingFields = [{}];
  render(<MigrationStatsTable migrationStats={missingFields} />);

  expect(screen.queryAllByText("—")).toHaveLength(7);
});