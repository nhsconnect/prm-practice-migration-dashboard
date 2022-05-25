import React, { FC } from "react";
import { Table } from "nhsuk-react-components";
import { DateTime } from "luxon";
import content from "../../data/content/migrationStatsTable.json";

interface MigrationStat {
  cutover_startdate?: string;
  cutover_enddate?: string;
  practice_name?: string;
  ods_code?: string;
  ccg_name?: string;
  source_system?: string;
  target_system?: string;
  cutover_duration?: number;
}

interface MigrationStatsTableProps {
  migrationStats: MigrationStat[];
}

function formatDate(isoDateTime?: string): string {
  if (!isoDateTime) {
    return "—";
  }
  return DateTime.fromISO(isoDateTime).toFormat("EEE, d LLL yyyy");
}

function formatPracticeName(practice_name?: string, ods_code?: string): string {
  if (!practice_name) {
    return "—";
  }
  return `${practice_name} (${ods_code})`;
}

export const MigrationStatsTable: FC<MigrationStatsTableProps> = ({
  migrationStats,
}) => (
  <Table>
    <Table.Head>
      <Table.Row>
        <Table.Cell>{content.headings.cutoverStartDate}</Table.Cell>
        <Table.Cell>{content.headings.cutoverEndDate}</Table.Cell>
        <Table.Cell>{content.headings.practiceName}</Table.Cell>
        <Table.Cell>{content.headings.ccgName}</Table.Cell>
        <Table.Cell>{content.headings.sourceSystem}</Table.Cell>
        <Table.Cell>{content.headings.targetSystem}</Table.Cell>
        <Table.Cell>{content.headings.cutoverDuration}</Table.Cell>
      </Table.Row>
    </Table.Head>
    <Table.Body>
      {migrationStats.map((migration: MigrationStat, index: number) => (
        <Table.Row key={migration.practice_name ?? index}>
          <Table.Cell>{formatDate(migration.cutover_startdate)}</Table.Cell>
          <Table.Cell>{formatDate(migration.cutover_enddate)}</Table.Cell>
          <Table.Cell>
            {formatPracticeName(migration.practice_name, migration.ods_code)}
          </Table.Cell>
          <Table.Cell>{migration.ccg_name ?? "—"}</Table.Cell>
          <Table.Cell>{migration.source_system ?? "—"}</Table.Cell>
          <Table.Cell>{migration.target_system ?? "—"}</Table.Cell>
          <Table.Cell>{migration.cutover_duration ?? "—"}</Table.Cell>
        </Table.Row>
      ))}
    </Table.Body>
  </Table>
);

export default MigrationStatsTable;
