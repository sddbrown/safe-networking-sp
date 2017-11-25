export default [
  {
    name: "dashboard",
    path: "/"
  },
  {
    name: "iot",
    path: "/iot",
    children: [
      { name: "dashboard", path: "/dashboard" },
      { name: "child-route", path: "/child-route" }
    ]
  },
  {
    name: "faq",
    path: "/faq"
  },
  {
    name: "domain",
    path: "/domain"
  }
];
