import * as React from "react";

import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import MigrationStatsTable from "../index";

const defaultMigrationStats = [
  {
    cutover_startdate: "2022-01-01T02:03:04Z",
    cutover_enddate: "2022-01-12T04:03:02Z",
    practice_name: "Bury",
    patient_registration_count: 1000,
    ods_code: "A12345",
    ccg_name: "Greater Manchester CCG",
    source_system: "EMIS Web",
    target_system: "TTP SystemOne",
    cutover_duration: 12,
  },
];

const missingFields = [
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

  expect(screen.getByText("Cutover Start Date")).toBeInTheDocument();
  expect(screen.getByText("Cutover End Date")).toBeInTheDocument();
  expect(screen.getByText("Practice Name")).toBeInTheDocument();
  expect(screen.getByText("Patients")).toBeInTheDocument();
  expect(screen.getByText("CCG Name")).toBeInTheDocument();
  expect(screen.getByText("Source System")).toBeInTheDocument();
  expect(screen.getByText("Target System")).toBeInTheDocument();
  expect(screen.getByText("Cutover Duration (Days)")).toBeInTheDocument();

  expect(screen.getByText("Sat, 1 Jan 2022")).toBeInTheDocument();
  expect(screen.getByText("Wed, 12 Jan 2022")).toBeInTheDocument();
  expect(screen.getByText("Bury (A12345)")).toBeInTheDocument();
  expect(screen.getByText("1,000")).toBeInTheDocument();
  expect(screen.getByText("Greater Manchester CCG")).toBeInTheDocument();
  expect(screen.getByText("EMIS Web")).toBeInTheDocument();
  expect(screen.getByText("TTP SystemOne")).toBeInTheDocument();
  expect(screen.getByText("12")).toBeInTheDocument();
});

it("handles missing fields", () => {
  render(<MigrationStatsTable migrationStats={missingFields} />);

  expect(screen.queryAllByText("—")).toHaveLength(1);
});
