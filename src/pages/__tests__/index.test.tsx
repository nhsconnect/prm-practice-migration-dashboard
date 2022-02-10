import * as React from "react"

import {render} from "@testing-library/react";
import IndexPage from '../index';

it('renders a table', () => {
    render(<IndexPage />);

    // expect(screen.queryByText("Date")).toBeTruthy();
    // expect(screen.queryByText("Practice Name")).toBeTruthy();
    // expect(screen.queryByText("Source Supplier")).toBeTruthy();
    // expect(screen.queryByText("Target Supplier")).toBeTruthy();
    // expect(screen.queryByText("Cutover Duration (Days)")).toBeTruthy();
});