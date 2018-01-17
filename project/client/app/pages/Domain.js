import React, { Component } from "react";
import styled from "styled-components";
import Sidebar from "layout/Sidebar";
import Pages from "pages";

export default class Domain extends Component {
  renderContent() {
    const { route } = this.props;
    if (route.name === "domain") return <Pages.DomainDashboard />;
    if (route.name === "domain.child-route") return <Pages.DomainChild />;
  }
  
  render() {
    return (
      <Root>
        <Sidebar
          links={[
            {
              routeName: "domain",
              title: "Dashboard",
              icon: "tachometer"
            },
            {
              routeName: "domain.child-route",
              title: "Malware by FileType",
              icon: "gear"
            }
          ]}
        />
        {this.renderContent()}
      </Root>
    );
  }
}

const Root = styled.div`
  display: flex;
  width: 100%;
  height: 100%;
`;
