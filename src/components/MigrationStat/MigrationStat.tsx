import React from "react";
import {FC} from "react";

interface MigrationStatProps {
    label: string,
    value: string,
    unit: string
}

export const MigrationStat: FC<MigrationStatProps> = ({ label, value, unit }) => (
    <p><strong>{ `${label}: ` }</strong>{`${value} ${unit}`}</p>
);