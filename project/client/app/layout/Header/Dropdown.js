import React from "react";
import styled from "styled-components";

export default class Dropdown extends React.Component {
  constructor() {
    super();

    this.state = {
      isActive: false
    };
  }

  render() {
    const isActive = this.state.isActive;
    return (
      <Root onClick={() => this.setState({ isActive: !isActive })}>
        <BrandArea>
          <p>Safe Networking</p>
          <BrandAreaArrow className={isActive && "active"}>
            <i className="fa fa-chevron-down" />
          </BrandAreaArrow>
        </BrandArea>
        <DropdownDrawer
          isActive={isActive}
          className={isActive ? "active" : null}
        >
          {isActive ? "OPEN" : "Closed"}
        </DropdownDrawer>
      </Root>
    );
  }
}

const BrandArea = styled.div`
  width: 100%;
  height: 100%;
  position: relative;

  &:before {
    content: " ";
    display: block;
    background: url("/static/images/logo-pan-bg.png") no-repeat 20px center;
    background-size: 55px;
    width: 100%;
    height: 100%;
    position: absolute;
    top: 0;
    left: 0;
    opacity: 0.2;
  }

  p {
    font-size: 18px;
    font-weight: 600;
    text-transform: uppercase;
    color: #fff;
    line-height: 60px;
    margin-left: 33px;
  }
`;

const BrandAreaArrow = styled.div`
  width: 20px;
  height: 20px;
  left: 215px;
  top: 50%;
  transform: translateY(-50%);
  position: absolute;
  transition: all ease 0.2s;

  &.active {
    transform: translateY(-50%) rotate(180deg);
  }

  i {
    color: #fff;
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
  }
`;

const DropdownDrawer = styled.div`
  width: 300px;
  height: 300px;
  background: #fff;
  box-shadow: 0px 0px 3px rgba(0, 0, 0, 0.3);
  position: absolute;
  top: 100%;
  left: 40px;
  transition: all ease 0.3s;
  transform: translateY(-100%);
  z-index: -1;

  &.active {
    transform: translateY(0%);
  }
`;

const Root = styled.div`
  height: 100%;
  width: 340px;
  display: inline-block;
  position: relative;
  background-color: #444;

  &:hover {
    background-color: #222;
  }
`;
