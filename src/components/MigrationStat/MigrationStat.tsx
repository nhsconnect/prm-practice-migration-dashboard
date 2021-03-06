import React from "react";
import { FC } from "react";

interface MigrationStatProps {
  label: string;
  value: number;
  unit: string;
}

export const MigrationStat: FC<MigrationStatProps> = ({
  label,
  value,
  unit,
}) => (
  <p>
    <strong>{`${label} (${unit}): `}</strong>
    {`${value}`}
  </p>
);
