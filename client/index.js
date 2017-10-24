const { render } = ReactDOM;

const App = () => (
  <div id="app">
    <Header />
    <MainContent />
  </div>
);

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
        <a href="#" className="active">
          {" "}
          Dashboard
        </a>
      </li>
      <li>
        <a href="#"> IOT</a>
      </li>
      <li>
        <a href="#"> Domain</a>
      </li>
    </ul>
  </nav>
);

const MainContent = () => (
  <main>
    <iframe src="https://www.warnerbros.com/archive/spacejam/movie/jam.html" />
  </main>
);

const Card = ({ children }) => <div className="card">{children}</div>;
render(<App />, document.getElementById("app"));
