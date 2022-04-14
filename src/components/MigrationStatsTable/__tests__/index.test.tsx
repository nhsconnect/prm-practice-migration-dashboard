import * as React from "react";

import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import MigrationStatsTable from "../index";

const defaultMigrationStats = [
  {
    cutover_startdate: "2022-01-01T02:03:04Z",
    cutover_enddate: "2022-01-12T04:03:02Z",
    practice_name: "Bury",
    ods_code: "A12345",
    ccg_name: "Greater Manchester CCG",
    source_system: "EMIS Web",
    target_system: "TTP SystemOne",
    cutover_duration: 12,
  },
];

jest.mock("../../data/metrics/migrations.json", () => defaultMigrationStats, {
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

  expect(screen.getByText("Sat, 1 Jan 2022")).toBeInTheDocument();
  expect(screen.getByText("Wed, 12 Jan 2022")).toBeInTheDocument();
  expect(screen.getByText("Bury (A12345)")).toBeInTheDocument();
  expect(screen.getByText("Greater Manchester CCG")).toBeInTheDocument();
  expect(screen.getByText("EMIS Web")).toBeInTheDocument();
  expect(screen.getByText("TTP SystemOne")).toBeInTheDocument();
  expect(screen.getByText("12")).toBeInTheDocument();
});

it("handles missing fields", () => {
  const missingFields = [{}];
  render(<MigrationStatsTable migrationStats={missingFields} />);

  expect(screen.queryAllByText("—")).toHaveLength(7);
});
