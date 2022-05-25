import React, { FC } from "react";
import { Table } from "nhsuk-react-components";
import content from "../../data/content/supplierCombinationStatsTable.json";

interface SupplierCombinationStat {
    source_system: string;
    target_system: string;
    count: number;
    mean_duration: number;
}

interface SupplierCombinationStatsTableProps {
    supplierCombinationStats: SupplierCombinationStat[];
}

export const SupplierCombinationStatsTable: FC<SupplierCombinationStatsTableProps> = ({
    supplierCombinationStats,
}) => (
    <Table>
        <Table.Head>
            <Table.Row>
                <Table.Cell>{content.headings.sourceSystem}</Table.Cell>
                <Table.Cell>{content.headings.targetSystem}</Table.Cell>
                <Table.Cell>{content.headings.count}</Table.Cell>
                <Table.Cell>{content.headings.meanDuration}</Table.Cell>
            </Table.Row>
        </Table.Head>
        <Table.Body>
            {supplierCombinationStats.map((supplierCombination: SupplierCombinationStat) => (
                <Table.Row key={supplierCombination.source_system + "_" + supplierCombination.target_system}>
                    <Table.Cell>{supplierCombination.source_system ?? "—"}</Table.Cell>
                    <Table.Cell>{supplierCombination.target_system ?? "—"}</Table.Cell>
                    <Table.Cell>{supplierCombination.count ?? "—"}</Table.Cell>
                    <Table.Cell>{supplierCombination.mean_duration ?? "—"}</Table.Cell>
                </Table.Row>
            ))}
        </Table.Body>
    </Table>
);

export default SupplierCombinationStatsTable;