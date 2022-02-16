import * as React from "react";

import { FC } from "react";
import Layout from "../components/layout";
import migrations from "../data/content/migrations.json";
import MigrationStatsTable from "../components/MigrationStatsTable";

const IndexPage: FC = () => (
  <Layout>
    <MigrationStatsTable migrationStats={migrations} />
  </Layout>
);

export default IndexPage;
