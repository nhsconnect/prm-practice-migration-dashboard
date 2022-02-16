import React from "react";
import content from "../../data/content/header.json";

import { FC } from "react";
import { Header } from "nhsuk-react-components";

interface HeaderProps {}

export const HeaderContainer: FC<HeaderProps> = () => (
  <Header transactional>
    <Header.Container>
      <Header.Logo href="/" />
      <Header.ServiceName href="/">{content.serviceName}</Header.ServiceName>
    </Header.Container>
  </Header>
);

export default HeaderContainer;
