import React from "react";
import { Link } from "gatsby";
import Logo from "../../assets/logo.svg";
import content from "../../data/content/header.json";

import { FC } from "react";

interface HeaderProps {}

export const Header: FC<HeaderProps> = () => (
  <header className="nhsuk-header" role="banner">
    <div className="nhsuk-width-container nhsuk-header__container">
      <div className="nhsuk-header__logo nhsuk-header__logo--only">
        <Link
          className="gp2gp-header__link"
          to="/"
          aria-label={content.homepageLinkLabel}
        >
          <Logo />
          <span className="nhsuk-header__service-name">
            {content.serviceName}
          </span>
        </Link>
      </div>
    </div>
    <div className="nhsuk-width-container nhsuk-u-padding-bottom-3"></div>
  </header>
);

export default Header;
