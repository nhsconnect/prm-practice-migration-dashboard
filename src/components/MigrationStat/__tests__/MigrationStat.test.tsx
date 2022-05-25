import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { MigrationStat } from "../MigrationStat";

describe("MigrationStat", () => {
  it("displays the stat", () => {
    render(
      <MigrationStat
        label={"Average Cutover Duration"}
        value={16.0}
        unit={"days"}
      />
    );

    expect(screen.getByText(16.0)).toBeInTheDocument();
    expect(
      screen.getByText("Average Cutover Duration (days):")
    ).toBeInTheDocument();
  });
});
