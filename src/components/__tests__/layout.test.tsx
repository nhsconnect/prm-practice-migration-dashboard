import * as React from "react";

import { render, screen } from "@testing-library/react";
import Layout from "../layout";

import content from "../../data/content/header.json";

it("renders general page layout", () => {
  render(
    <Layout>
      <div>Page content</div>
    </Layout>
  );

  expect(screen.queryByText(content.serviceName)).toBeTruthy(); // from Header
  expect(screen.queryByText("Practice Migration data")).toBeTruthy();
  expect(
    screen.queryByText(
      "This platform provides monthly data about system migrations for practices in England."
    )
  ).toBeTruthy();
  expect(screen.queryByText("Page content")).toBeTruthy();
  expect(screen.queryByText(/ Crown copyright/)).toBeTruthy(); // from Footer
});
