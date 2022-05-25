import * as React from "react";
import {FC} from "react";
import Layout from "../components/layout";
import migrations from "../data/metrics/migrations.json";
import MigrationStatsTable from "../components/MigrationStatsTable";
import {MigrationStat} from "../components/MigrationStat/MigrationStat";
import content from "../data/content/index.json";
import SupplierCombinationStatsTable from "../components/SupplierCombinationStatsTable";

const IndexPage: FC = () => {
    return (
  <Layout>
      <h2>General Statistics</h2>
      <p data-testid="observation-notice">This data has been derived from <strong>{migrations.migrations.length}</strong> observed practice migration(s).</p>
    <MigrationStat
          label={content.meanCutoverDurationLabel}
          value={migrations.mean_cutover_duration}
          unit={content.meanCutoverDurationUnit} />
      <SupplierCombinationStatsTable supplierCombinationStats={migrations.supplier_combination_stats} />
      <h2>Migrations</h2>
      <MigrationStatsTable migrationStats={migrations.migrations} />
  </Layout>
)};

export default IndexPage;
