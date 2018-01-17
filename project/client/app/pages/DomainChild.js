import React, { Component } from "react";

export default class DomainChild extends Component {
    render() {
      return <iframe src="http://192.168.86.140:5601/app/kibana#/dashboard/1786e3d0-f7ef-11e7-b24e-c9e24e5aea5b?embed=true&_g=(refreshInterval%3A(display%3AOff%2Cpause%3A!f%2Cvalue%3A0)%2Ctime%3A(from%3Anow-6M%2Cmode%3Aquick%2Cto%3Anow))" height="600" width="800"></iframe>;
    }
  }
  