import {render, screen} from "@testing-library/react";
import "@testing-library/jest-dom";
import SupplierCombinationStatsTable from "../index";
import * as React from "react";

const defaultSupplierCombinationStats = [
    {
        source_system: "EMIS Web",
        target_system: "TTP SystemOne",
        count: 1,
        mean_duration: 12,
    },
];

it("renders a table", () => {
    render(<SupplierCombinationStatsTable supplierCombinationStats={defaultSupplierCombinationStats} />);

    expect(screen.getByText("Source Supplier")).toBeInTheDocument();
    expect(screen.getByText("Target Supplier")).toBeInTheDocument();
    expect(screen.getByText("Observed Migrations")).toBeInTheDocument();
    expect(screen.getByText("Average Cutover Duration (Days)")).toBeInTheDocument();

    expect(screen.getByText("EMIS Web")).toBeInTheDocument();
    expect(screen.getByText("TTP SystemOne")).toBeInTheDocument();
    expect(screen.getByText("1")).toBeInTheDocument();
    expect(screen.getByText("12")).toBeInTheDocument();
});