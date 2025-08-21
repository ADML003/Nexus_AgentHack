export type SiteConfig = typeof siteConfig;

export const siteConfig = {
  name: "Nexus",
  description: "Make beautiful websites regardless of your design experience.",
  navItems: [
    {
      label: "Features",
      href: "#features",
    },
    {
      label: "About",
      href: "/about",
    },
    {
      label: "Agent",
      href: "/agent",
    },
  ],
  navMenuItems: [
    {
      label: "Profile",
      href: "/profile",
    },
    {
      label: "Agent",
      href: "/agent",
    },
    {
      label: "Projects",
      href: "/projects",
    },
    {
      label: "Team",
      href: "/team",
    },
    {
      label: "Calendar",
      href: "/calendar",
    },
    {
      label: "Settings",
      href: "/settings",
    },
    {
      label: "Help & Feedback",
      href: "/help-feedback",
    },
    {
      label: "Logout",
      href: "/logout",
    },
  ],
  links: {
    github: "https://github.com/DarkInventor",
    twitter: "https://twitter.com/kathanmehtaa",
    docs: "#",
    discord: "#",
    sponsor: "#",
  },
};
