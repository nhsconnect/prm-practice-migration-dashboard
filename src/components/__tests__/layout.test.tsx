import * as React from "react";

import { render } from "@testing-library/react";
import Layout from "../layout";

it("renders general page layout", () => {
  render(
    <Layout>
      <div>Page content</div>
    </Layout>
  );

  // expect(screen.getByRole('img', { name: 'fancy image' })).toBeTruthy();
});
