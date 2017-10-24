"use strict";

var _typeof3 =
  typeof Symbol === "function" && typeof Symbol.iterator === "symbol"
    ? function(obj) {
        return typeof obj;
      }
    : function(obj) {
        return obj &&
          typeof Symbol === "function" &&
          obj.constructor === Symbol &&
          obj !== Symbol.prototype
          ? "symbol"
          : typeof obj;
      };

var _typeof2 =
  typeof Symbol === "function" && _typeof3(Symbol.iterator) === "symbol"
    ? function(obj) {
        return typeof obj === "undefined" ? "undefined" : _typeof3(obj);
      }
    : function(obj) {
        return obj &&
          typeof Symbol === "function" &&
          obj.constructor === Symbol &&
          obj !== Symbol.prototype
          ? "symbol"
          : typeof obj === "undefined" ? "undefined" : _typeof3(obj);
      };

var _typeof =
  typeof Symbol === "function" && _typeof2(Symbol.iterator) === "symbol"
    ? function(obj) {
        return typeof obj === "undefined" ? "undefined" : _typeof2(obj);
      }
    : function(obj) {
        return obj &&
          typeof Symbol === "function" &&
          obj.constructor === Symbol &&
          obj !== Symbol.prototype
          ? "symbol"
          : typeof obj === "undefined" ? "undefined" : _typeof2(obj);
      };

var _createClass = (function() {
  function defineProperties(target, props) {
    for (var i = 0; i < props.length; i++) {
      var descriptor = props[i];
      descriptor.enumerable = descriptor.enumerable || false;
      descriptor.configurable = true;
      if ("value" in descriptor) descriptor.writable = true;
      Object.defineProperty(target, descriptor.key, descriptor);
    }
  }
  return function(Constructor, protoProps, staticProps) {
    if (protoProps) defineProperties(Constructor.prototype, protoProps);
    if (staticProps) defineProperties(Constructor, staticProps);
    return Constructor;
  };
})();

function _classCallCheck(instance, Constructor) {
  if (!(instance instanceof Constructor)) {
    throw new TypeError("Cannot call a class as a function");
  }
}

function _possibleConstructorReturn(self, call) {
  if (!self) {
    throw new ReferenceError(
      "this hasn't been initialised - super() hasn't been called"
    );
  }
  return call &&
    ((typeof call === "undefined" ? "undefined" : _typeof(call)) === "object" ||
      typeof call === "function")
    ? call
    : self;
}

function _inherits(subClass, superClass) {
  if (typeof superClass !== "function" && superClass !== null) {
    throw new TypeError(
      "Super expression must either be null or a function, not " +
        (typeof superClass === "undefined" ? "undefined" : _typeof(superClass))
    );
  }
  subClass.prototype = Object.create(superClass && superClass.prototype, {
    constructor: {
      value: subClass,
      enumerable: false,
      writable: true,
      configurable: true
    }
  });
  if (superClass)
    Object.setPrototypeOf
      ? Object.setPrototypeOf(subClass, superClass)
      : (subClass.__proto__ = superClass);
}

var _ReactDOM = ReactDOM,
  render = _ReactDOM.render;

var App = function App() {
  return React.createElement(
    "div",
    { id: "app" },
    React.createElement(Header, null),
    React.createElement(MainContent, null)
  );
};

var Dropdown = (function(_React$Component) {
  _inherits(Dropdown, _React$Component);

  function Dropdown() {
    _classCallCheck(this, Dropdown);

    var _this = _possibleConstructorReturn(
      this,
      (Dropdown.__proto__ || Object.getPrototypeOf(Dropdown)).call(this)
    );

    _this.state = {
      isActive: false
    };
    return _this;
  }

  _createClass(Dropdown, [
    {
      key: "render",
      value: function render() {
        var _this2 = this;

        var isActive = !this.state.isActive;
        return React.createElement(
          "div",
          {
            id: "main-dropdown",
            onClick: function onClick() {
              return _this2.setState({ isActive: isActive });
            }
          },
          React.createElement(
            "div",
            { id: "brand-area" },
            React.createElement("p", null, "Safe Networking"),
            React.createElement(
              "div",
              { id: "brand-area-arrow", className: isActive && "active" },
              React.createElement("i", { className: "fa fa-chevron-down" })
            )
          ),
          React.createElement(DropdownDrawer, { isActive: isActive })
        );
      }
    }
  ]);

  return Dropdown;
})(React.Component);

var DropdownDrawer = function DropdownDrawer(props) {
  return React.createElement(
    "div",
    { id: "dropdown-drawer", className: props.isActive && "active" },
    props.isActive ? "OPEN" : "Closed"
  );
};

var UtilityBar = function UtilityBar() {
  return React.createElement(
    "div",
    { id: "utility-bar" },
    React.createElement(UtilityButton, { title: "Search", icon: "search" }),
    React.createElement(UtilityButton, { title: "Settings", icon: "cog" }),
    React.createElement(UtilityButton, {
      title: "FAQ",
      icon: "question-circle"
    })
  );
};

var UtilityButton = function UtilityButton(props) {
  return React.createElement(
    "a",
    { href: props.link, className: "utility-button fa fa-" + props.icon },
    React.createElement("span", { className: "tooltip" }, props.title)
  );
};

var Header = function Header() {
  return React.createElement(
    "header",
    { id: "main" },
    React.createElement(Dropdown, null),
    React.createElement(Nav, null),
    React.createElement(UtilityBar, null)
  );
};

var Nav = function Nav() {
  return React.createElement(
    "nav",
    null,
    React.createElement(
      "ul",
      null,
      React.createElement(
        "li",
        null,
        React.createElement(
          "a",
          { href: "#", className: "active" },
          " ",
          "Dashboard"
        )
      ),
      React.createElement(
        "li",
        null,
        React.createElement("a", { href: "#" }, " IOT")
      ),
      React.createElement(
        "li",
        null,
        React.createElement("a", { href: "#" }, " Domain")
      )
    )
  );
};

var MainContent = function MainContent() {
  return React.createElement(
    "main",
    null,
    React.createElement("iframe", {
      src: "https://www.warnerbros.com/archive/spacejam/movie/jam.html"
    })
  );
};

var Card = function Card(_ref) {
  var children = _ref.children;
  return React.createElement("div", { className: "card" }, children);
};
render(React.createElement(App, null), document.getElementById("app"));
("use strict");

var _createClass = (function() {
  function defineProperties(target, props) {
    for (var i = 0; i < props.length; i++) {
      var descriptor = props[i];
      descriptor.enumerable = descriptor.enumerable || false;
      descriptor.configurable = true;
      if ("value" in descriptor) descriptor.writable = true;
      Object.defineProperty(target, descriptor.key, descriptor);
    }
  }
  return function(Constructor, protoProps, staticProps) {
    if (protoProps) defineProperties(Constructor.prototype, protoProps);
    if (staticProps) defineProperties(Constructor, staticProps);
    return Constructor;
  };
})();

function _classCallCheck(instance, Constructor) {
  if (!(instance instanceof Constructor)) {
    throw new TypeError("Cannot call a class as a function");
  }
}

function _possibleConstructorReturn(self, call) {
  if (!self) {
    throw new ReferenceError(
      "this hasn't been initialised - super() hasn't been called"
    );
  }
  return call &&
    ((typeof call === "undefined" ? "undefined" : _typeof2(call)) ===
      "object" ||
      typeof call === "function")
    ? call
    : self;
}

function _inherits(subClass, superClass) {
  if (typeof superClass !== "function" && superClass !== null) {
    throw new TypeError(
      "Super expression must either be null or a function, not " +
        (typeof superClass === "undefined" ? "undefined" : _typeof2(superClass))
    );
  }
  subClass.prototype = Object.create(superClass && superClass.prototype, {
    constructor: {
      value: subClass,
      enumerable: false,
      writable: true,
      configurable: true
    }
  });
  if (superClass)
    Object.setPrototypeOf
      ? Object.setPrototypeOf(subClass, superClass)
      : (subClass.__proto__ = superClass);
}

var _ReactDOM = ReactDOM,
  render = _ReactDOM.render;

var App = function App() {
  return React.createElement(
    "div",
    { id: "app" },
    React.createElement(Header, null),
    React.createElement(MainContent, null)
  );
};

var Dropdown = (function(_React$Component) {
  _inherits(Dropdown, _React$Component);

  function Dropdown() {
    _classCallCheck(this, Dropdown);

    var _this = _possibleConstructorReturn(
      this,
      (Dropdown.__proto__ || Object.getPrototypeOf(Dropdown)).call(this)
    );

    _this.state = {
      isActive: false
    };
    return _this;
  }

  _createClass(Dropdown, [
    {
      key: "render",
      value: function render() {
        var _this2 = this;

        var isActive = this.state.isActive;
        return React.createElement(
          "div",
          {
            id: "main-dropdown",
            onClick: function onClick() {
              return _this2.setState({ isActive: isActive });
            }
          },
          React.createElement(
            "div",
            { id: "brand-area" },
            React.createElement("p", null, "Safe Networking"),
            React.createElement(
              "div",
              { id: "brand-area-arrow", className: isActive && "active" },
              React.createElement("i", { className: "fa fa-chevron-down" })
            )
          ),
          React.createElement(DropdownDrawer, { isActive: isActive })
        );
      }
    }
  ]);

  return Dropdown;
})(React.Component);

var DropdownDrawer = function DropdownDrawer(props) {
  return React.createElement(
    "div",
    { id: "dropdown-drawer", className: props.isActive && "active" },
    props.isActive ? "OPEN" : "Closed"
  );
};

var UtilityBar = function UtilityBar() {
  return React.createElement(
    "div",
    { id: "utility-bar" },
    React.createElement(UtilityButton, { title: "Search", icon: "search" }),
    React.createElement(UtilityButton, { title: "Settings", icon: "cog" }),
    React.createElement(UtilityButton, {
      title: "FAQ",
      icon: "question-circle"
    })
  );
};

var UtilityButton = function UtilityButton(props) {
  return React.createElement(
    "a",
    { href: props.link, className: "utility-button fa fa-" + props.icon },
    React.createElement("span", { className: "tooltip" }, props.title)
  );
};

var Header = function Header() {
  return React.createElement(
    "header",
    { id: "main" },
    React.createElement(Dropdown, null),
    React.createElement(Nav, null),
    React.createElement(UtilityBar, null)
  );
};

var Nav = function Nav() {
  return React.createElement(
    "nav",
    null,
    React.createElement(
      "ul",
      null,
      React.createElement(
        "li",
        null,
        React.createElement(
          "a",
          { href: "#", className: "active" },
          " ",
          "Dashboard"
        )
      ),
      React.createElement(
        "li",
        null,
        React.createElement("a", { href: "#" }, " IOT")
      ),
      React.createElement(
        "li",
        null,
        React.createElement("a", { href: "#" }, " Domain")
      )
    )
  );
};

var MainContent = function MainContent() {
  return React.createElement(
    "main",
    null,
    React.createElement("iframe", {
      src: "https://www.warnerbros.com/archive/spacejam/movie/jam.html"
    })
  );
};

var Card = function Card(_ref) {
  var children = _ref.children;
  return React.createElement("div", { className: "card" }, children);
};
render(React.createElement(App, null), document.getElementById("app"));
("use strict");

var _createClass = (function() {
  function defineProperties(target, props) {
    for (var i = 0; i < props.length; i++) {
      var descriptor = props[i];
      descriptor.enumerable = descriptor.enumerable || false;
      descriptor.configurable = true;
      if ("value" in descriptor) descriptor.writable = true;
      Object.defineProperty(target, descriptor.key, descriptor);
    }
  }
  return function(Constructor, protoProps, staticProps) {
    if (protoProps) defineProperties(Constructor.prototype, protoProps);
    if (staticProps) defineProperties(Constructor, staticProps);
    return Constructor;
  };
})();

function _classCallCheck(instance, Constructor) {
  if (!(instance instanceof Constructor)) {
    throw new TypeError("Cannot call a class as a function");
  }
}

function _possibleConstructorReturn(self, call) {
  if (!self) {
    throw new ReferenceError(
      "this hasn't been initialised - super() hasn't been called"
    );
  }
  return call &&
    ((typeof call === "undefined" ? "undefined" : _typeof3(call)) ===
      "object" ||
      typeof call === "function")
    ? call
    : self;
}

function _inherits(subClass, superClass) {
  if (typeof superClass !== "function" && superClass !== null) {
    throw new TypeError(
      "Super expression must either be null or a function, not " +
        (typeof superClass === "undefined" ? "undefined" : _typeof3(superClass))
    );
  }
  subClass.prototype = Object.create(superClass && superClass.prototype, {
    constructor: {
      value: subClass,
      enumerable: false,
      writable: true,
      configurable: true
    }
  });
  if (superClass)
    Object.setPrototypeOf
      ? Object.setPrototypeOf(subClass, superClass)
      : (subClass.__proto__ = superClass);
}

var _ReactDOM = ReactDOM,
  render = _ReactDOM.render;

var App = function App() {
  return React.createElement(
    "div",
    { id: "app" },
    React.createElement(Header, null),
    React.createElement(MainContent, null)
  );
};

var Dropdown = (function(_React$Component) {
  _inherits(Dropdown, _React$Component);

  function Dropdown() {
    _classCallCheck(this, Dropdown);

    var _this = _possibleConstructorReturn(
      this,
      (Dropdown.__proto__ || Object.getPrototypeOf(Dropdown)).call(this)
    );

    _this.state = {
      isActive: false
    };
    return _this;
  }

  _createClass(Dropdown, [
    {
      key: "render",
      value: function render() {
        var _this2 = this;

        var isActive = this.state.isActive;
        return React.createElement(
          "div",
          {
            id: "main-dropdown",
            onClick: function onClick() {
              return _this2.setState({ isActive: isActive });
            }
          },
          React.createElement(
            "div",
            { id: "brand-area" },
            React.createElement("p", null, "Safe Networking"),
            React.createElement(
              "div",
              { id: "brand-area-arrow", className: isActive && "active" },
              React.createElement("i", { className: "fa fa-chevron-down" })
            )
          ),
          React.createElement(DropdownDrawer, { isActive: isActive })
        );
      }
    }
  ]);

  return Dropdown;
})(React.Component);

var DropdownDrawer = function DropdownDrawer(props) {
  return React.createElement(
    "div",
    { id: "dropdown-drawer", className: props.isActive && "active" },
    props.isActive ? "OPEN" : "Closed"
  );
};

var UtilityBar = function UtilityBar() {
  return React.createElement(
    "div",
    { id: "utility-bar" },
    React.createElement(UtilityButton, { title: "Search", icon: "search" }),
    React.createElement(UtilityButton, { title: "Settings", icon: "cog" }),
    React.createElement(UtilityButton, {
      title: "FAQ",
      icon: "question-circle"
    })
  );
};

var UtilityButton = function UtilityButton(props) {
  return React.createElement(
    "a",
    { href: props.link, className: "utility-button fa fa-" + props.icon },
    React.createElement("span", { className: "tooltip" }, props.title)
  );
};

var Header = function Header() {
  return React.createElement(
    "header",
    { id: "main" },
    React.createElement(Dropdown, null),
    React.createElement(Nav, null),
    React.createElement(UtilityBar, null)
  );
};

var Nav = function Nav() {
  return React.createElement(
    "nav",
    null,
    React.createElement(
      "ul",
      null,
      React.createElement(
        "li",
        null,
        React.createElement(
          "a",
          { href: "#", className: "active" },
          " ",
          "Dashboard"
        )
      ),
      React.createElement(
        "li",
        null,
        React.createElement("a", { href: "#" }, " IOT")
      ),
      React.createElement(
        "li",
        null,
        React.createElement("a", { href: "#" }, " Domain")
      )
    )
  );
};

var MainContent = function MainContent() {
  return React.createElement(
    "main",
    null,
    React.createElement("iframe", {
      src: "https://www.warnerbros.com/archive/spacejam/movie/jam.html"
    })
  );
};

var Card = function Card(_ref) {
  var children = _ref.children;
  return React.createElement("div", { className: "card" }, children);
};
render(React.createElement(App, null), document.getElementById("app"));
("use strict");

var _createClass = (function() {
  function defineProperties(target, props) {
    for (var i = 0; i < props.length; i++) {
      var descriptor = props[i];
      descriptor.enumerable = descriptor.enumerable || false;
      descriptor.configurable = true;
      if ("value" in descriptor) descriptor.writable = true;
      Object.defineProperty(target, descriptor.key, descriptor);
    }
  }
  return function(Constructor, protoProps, staticProps) {
    if (protoProps) defineProperties(Constructor.prototype, protoProps);
    if (staticProps) defineProperties(Constructor, staticProps);
    return Constructor;
  };
})();

function _classCallCheck(instance, Constructor) {
  if (!(instance instanceof Constructor)) {
    throw new TypeError("Cannot call a class as a function");
  }
}

function _possibleConstructorReturn(self, call) {
  if (!self) {
    throw new ReferenceError(
      "this hasn't been initialised - super() hasn't been called"
    );
  }
  return call && (typeof call === "object" || typeof call === "function")
    ? call
    : self;
}

function _inherits(subClass, superClass) {
  if (typeof superClass !== "function" && superClass !== null) {
    throw new TypeError(
      "Super expression must either be null or a function, not " +
        typeof superClass
    );
  }
  subClass.prototype = Object.create(superClass && superClass.prototype, {
    constructor: {
      value: subClass,
      enumerable: false,
      writable: true,
      configurable: true
    }
  });
  if (superClass)
    Object.setPrototypeOf
      ? Object.setPrototypeOf(subClass, superClass)
      : (subClass.__proto__ = superClass);
}

var _ReactDOM = ReactDOM,
  render = _ReactDOM.render;

var App = function App() {
  return React.createElement(
    "div",
    { id: "app" },
    React.createElement(Header, null),
    React.createElement(MainContent, null)
  );
};

var Dropdown = (function(_React$Component) {
  _inherits(Dropdown, _React$Component);

  function Dropdown() {
    _classCallCheck(this, Dropdown);

    var _this = _possibleConstructorReturn(
      this,
      (Dropdown.__proto__ || Object.getPrototypeOf(Dropdown)).call(this)
    );

    _this.state = {
      isActive: false
    };
    return _this;
  }

  _createClass(Dropdown, [
    {
      key: "render",
      value: function render() {
        var _this2 = this;

        var isActive = this.state.isActive;
        return React.createElement(
          "div",
          {
            id: "main-dropdown",
            onClick: function onClick() {
              return _this2.setState({ isActive: !isActive });
            }
          },
          React.createElement(
            "div",
            { id: "brand-area" },
            React.createElement("p", null, "Safe Networking"),
            React.createElement(
              "div",
              { id: "brand-area-arrow", className: isActive && "active" },
              React.createElement("i", { className: "fa fa-chevron-down" })
            )
          ),
          React.createElement(DropdownDrawer, { isActive: isActive })
        );
      }
    }
  ]);

  return Dropdown;
})(React.Component);

var DropdownDrawer = function DropdownDrawer(props) {
  return React.createElement(
    "div",
    { id: "dropdown-drawer", className: props.isActive && "active" },
    props.isActive ? "OPEN" : "Closed"
  );
};

var UtilityBar = function UtilityBar() {
  return React.createElement(
    "div",
    { id: "utility-bar" },
    React.createElement(UtilityButton, { title: "Search", icon: "search" }),
    React.createElement(UtilityButton, { title: "Settings", icon: "cog" }),
    React.createElement(UtilityButton, {
      title: "FAQ",
      icon: "question-circle"
    })
  );
};

var UtilityButton = function UtilityButton(props) {
  return React.createElement(
    "a",
    { href: props.link, className: "utility-button fa fa-" + props.icon },
    React.createElement("span", { className: "tooltip" }, props.title)
  );
};

var Header = function Header() {
  return React.createElement(
    "header",
    { id: "main" },
    React.createElement(Dropdown, null),
    React.createElement(Nav, null),
    React.createElement(UtilityBar, null)
  );
};

var Nav = function Nav() {
  return React.createElement(
    "nav",
    null,
    React.createElement(
      "ul",
      null,
      React.createElement(
        "li",
        null,
        React.createElement(
          "a",
          { href: "#", className: "active" },
          " ",
          "Dashboard"
        )
      ),
      React.createElement(
        "li",
        null,
        React.createElement("a", { href: "#" }, " IOT")
      ),
      React.createElement(
        "li",
        null,
        React.createElement("a", { href: "#" }, " Domain")
      )
    )
  );
};

var MainContent = function MainContent() {
  return React.createElement(
    "main",
    null,
    React.createElement("iframe", {
      src: "https://www.warnerbros.com/archive/spacejam/movie/jam.html"
    })
  );
};

var Card = function Card(_ref) {
  var children = _ref.children;
  return React.createElement("div", { className: "card" }, children);
};
render(React.createElement(App, null), document.getElementById("app"));
