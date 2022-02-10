import React from "react";
import content from "../../data/content/header.json";

import { FC } from "react";

interface HeaderProps {}

const Header: FC<HeaderProps> = () => (
  <header className="nhsuk-header" role="banner">
    <div className="nhsuk-width-container nhsuk-header__container">
      <div className="nhsuk-header__logo nhsuk-header__logo--only">
        <span className="nhsuk-header__service-name">
          {content.serviceName}
        </span>
      </div>
    </div>
    <div className="nhsuk-width-container nhsuk-u-padding-bottom-3"></div>
  </header>
);

export default Header;
