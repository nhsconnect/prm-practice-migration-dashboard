import * as React from "react";

import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import IndexPage from "../index";
import content from "../../data/content/index.json";

jest.mock(
  "../../data/metrics/migrations.json",
  () => ({
    mean_cutover_duration: "12.0",
    migrations: [
      {
        cutover_startdate: "2022-01-01T02:03:04Z",
        cutover_enddate: "2022-01-12T04:03:02Z",
        practice_name: "Bury",
        ccg_name: "Greater Manchester",
        source_system: "EMIS Web",
        target_system: "TTP SystemOne",
        cutover_duration: 12,
      },
    ],
  }),
  { virtual: true }
);

describe("index", () => {
  it("renders a table", () => {
    render(<IndexPage />);

    expect(screen.queryByText("Cutover Start Date")).toBeTruthy();
    expect(screen.queryByText("Cutover End Date")).toBeTruthy();
    expect(screen.queryByText("Practice Name")).toBeTruthy();
    expect(screen.queryByText("CCG Name")).toBeTruthy();
    expect(screen.queryByText("Source System")).toBeTruthy();
    expect(screen.queryByText("Target System")).toBeTruthy();
    expect(screen.queryByText("Cutover Duration (Days)")).toBeTruthy();

    expect(screen.getByText("Sat, 1 Jan 2022")).toBeInTheDocument();
    expect(screen.getByText("Wed, 12 Jan 2022")).toBeInTheDocument();
    expect(screen.getByText("Bury")).toBeInTheDocument();
    expect(screen.getByText("Greater Manchester")).toBeInTheDocument();
    expect(screen.getByText("EMIS Web")).toBeInTheDocument();
    expect(screen.getByText("TTP SystemOne")).toBeInTheDocument();
    expect(screen.getByText("12")).toBeInTheDocument();
  });

  it("renders the mean cutover duration stat", () => {
    render(<IndexPage />);

    expect(
      screen.getByText(
        `${content.meanCutoverDurationLabel} (${content.meanCutoverDurationUnit}):`
      )
    ).toBeInTheDocument();
    expect(screen.getByText(`12.0`)).toBeInTheDocument();
  });

  it("renders notification of observed migrations", () => {
    render(<IndexPage />);

    expect(screen.getByTestId("observation-notice").textContent).toBe(
      "This data has been derived from 1 observed practice migration(s)."
    );
  });
});
