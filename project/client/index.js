const { render } = ReactDOM;

const App = () => <Header />;

class Dropdown extends React.Component {
  constructor() {
    super();

    this.state = {
      isActive: false
    };
  }

  render() {
    const isActive = this.state.isActive;
    return (
      <div
        id="main-dropdown"
        onClick={() => this.setState({ isActive: !isActive })}
      >
        <div id="brand-area">
          <p>Safe Networking</p>
          <div id="brand-area-arrow" className={isActive && "active"}>
            <i className="fa fa-chevron-down" />
          </div>
        </div>
        <DropdownDrawer isActive={isActive} />
      </div>
    );
  }
}

const DropdownDrawer = props => (
  <div id="dropdown-drawer" className={props.isActive && "active"}>
    {props.isActive ? "OPEN" : "Closed"}
  </div>
);

const UtilityBar = () => (
  <div id="utility-bar">
    <UtilityButton title="Search" icon="search" />
    <UtilityButton title="Settings" icon="cog" />
    <UtilityButton title="FAQ" icon="question-circle" />
  </div>
);

const UtilityButton = props => (
  <a href={props.link} className={`utility-button fa fa-${props.icon}`}>
    <span className="tooltip">{props.title}</span>
  </a>
);

const Header = () => (
  <header id="main">
    <Dropdown />
    <Nav />
    <UtilityBar />
  </header>
);

const Nav = () => (
  <nav>
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
  </nav>
);

const MainContent = () => (
  <main>
    <iframe src="http://localhost:5601/app/kibana#/dashboard/AV8hRiO321JUDssTBFEH?embed=true&_g=(refreshInterval%3A(display%3AOff%2Cpause%3A!f%2Cvalue%3A0)%2Ctime%3A(from%3A'2016-10-24T01%3A14%3A04.450Z'%2Cmode%3Aabsolute%2Cto%3A'2017-10-24T01%3A29%3A04.451Z'))" />
  </main>
);

const Card = ({ children }) => <div className="card">{children}</div>;
render(<App />, document.getElementById("react-app-mount"));
