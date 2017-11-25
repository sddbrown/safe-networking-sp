import React from "react";
import styled from "styled-components";

const Nav = () => (
  <Root>
    <ul>
      <li>
        <a
          href="/dashboard"
          className={
            (window.location.pathname === "/dashboard" ||
              window.location.pathname === "") &&
            "active"
          }
        >
          {" "}
          Dashboard
        </a>
      </li>
      <li>
        <a
          href="/iot"
          className={window.location.pathname === "/iot" && "active"}
        >
          IOT
        </a>
      </li>
      <li>
        <a
          href="/domains"
          className={window.location.pathname === "/domains" && "active"}
        >
          Domain
        </a>
      </li>
    </ul>
  </Root>
);

const Root = styled.nav`
  ul {
    display: flex;
    height: 100%;
    margin: 0;
    padding: 0;

    li {
      list-style: none;
      color: #fff;

      a {
        text-decoration: none;
        padding: 0 20px;
        height: 100%;
        display: block;
        color: #fff;
        opacity: 0.666;
        line-height: 60px;
        text-transform: uppercase;
        font-size: 13px;
        border-bottom: solid 5px transparent;

        &.active {
          border-bottom: solid 5px #0e9ac8;
          opacity: 1;
          background: rgba(0, 0, 0, 0.3);
        }

        &:hover {
          opacity: 1;
        }
      }
    }
  }
`;

export default Nav;
