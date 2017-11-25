import React from "react";
import Dropdown from "layout/Header/Dropdown";
import Nav from "layout/Header/Nav";
import UtilityBar from "layout/Header/UtilityBar";
import styled from "styled-components";

const Header = () => (
  <Root id="main">
    <Dropdown />
    <Nav />
    <UtilityBar />
  </Root>
);

const Root = styled.header`
  background: #444;
  height: 60px;
  width: 100%;
  flex: 0 0 auto;
  box-shadow: 0px 3px 6px rgba(0, 0, 0, 0.3);
  z-index: 10;
  display: flex;
`;

export default Header;
