import { Table } from "nhsuk-react-components";
import * as React from "react";

import { FC } from "react";
import Layout from "../components/layout";
import migrations from '../data/content/migrations.json';

interface MigrationStat {
  cutover_startdate: string;
  cutover_enddate: string;
  practice_name: string;
  ccg_name: string;
  source_system: string;
  target_system: string;
  cutover_duration: number;
}

const IndexPage: FC = () => (
  <Layout>
    <Table>
      <Table.Head>
        <Table.Row>
          <Table.Cell>Cutover Start Date</Table.Cell>
          <Table.Cell>Cutover End Date</Table.Cell>
          <Table.Cell>Practice Name</Table.Cell>
          <Table.Cell>CCG Name</Table.Cell>
          <Table.Cell>Source System</Table.Cell>
          <Table.Cell>Target System</Table.Cell>
          <Table.Cell>Cutover Duration (Days)</Table.Cell>
        </Table.Row>
      </Table.Head>
      <Table.Body>
        {
          migrations.map(((migration : MigrationStat) => (
            <Table.Row key={migration.practice_name}>
              <Table.Cell>{migration.cutover_startdate}</Table.Cell>
              <Table.Cell>{migration.cutover_enddate}</Table.Cell>
              <Table.Cell>{migration.practice_name}</Table.Cell>
              <Table.Cell>{migration.ccg_name}</Table.Cell>
              <Table.Cell>{migration.source_system}</Table.Cell>
              <Table.Cell>{migration.target_system}</Table.Cell>
              <Table.Cell>{migration.cutover_duration}</Table.Cell>
            </Table.Row>
          )))
        }
      </Table.Body>
    </Table>
  </Layout>
);

export default IndexPage;
