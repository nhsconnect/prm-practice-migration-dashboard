import React from "react";
import { render, screen } from "@testing-library/react";
import {MigrationStat} from "../MigrationStat";

describe("MigrationStat", () => {
    it("displays the stat", () => {
        render(<MigrationStat label={"Average Cutover Duration"} value={"16.0"} unit={"Days"} />);

        expect(screen.queryByText("16.0 Days")).toBeTruthy();
        expect(screen.queryByText("Average Cutover Duration:")).toBeTruthy();
    });
});