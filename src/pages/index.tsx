import { Table } from "nhsuk-react-components";
import * as React from "react";

import { FC } from "react";
import Layout from "../components/layout";

const IndexPage: FC = () => (
  <Layout>
    <Table>
      <Table.Head>
        <Table.Row>
          <Table.Cell>Cutover Start Date</Table.Cell>
          <Table.Cell>Cutover End Date</Table.Cell>
          <Table.Cell>Practice Name</Table.Cell>
          <Table.Cell>Source System</Table.Cell>
          <Table.Cell>Target System</Table.Cell>
          <Table.Cell>Cutover Duration (Days)</Table.Cell>
        </Table.Row>
      </Table.Head>
    </Table>
  </Layout>
);

export default IndexPage;
