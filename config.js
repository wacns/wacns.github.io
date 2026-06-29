const CONFIG = {
  // Toggle tvOS support
  // true  → generate tvos/ folder + render tvOS section on landing page
  // false → iOS only
  tvosEnabled: false,

  // Base URL (no trailing slash)
  baseURL: "https://wacns.github.io/stremio-source",

  // App metadata
  app: {
    name: "Stremio",
    bundleIdentifier: "com.stremio.streamio",
    developerName: "Stremio",
    subtitle: "Stream anything",
    version: "1.0.0",
    versionDate: "2025-01-01",
    localizedDescription: "Stremio for iOS — stream movies, series, and more.",
    iconURL: "https://www.stremio.com/website/stremio-purple-small.png",
    tintColor: "665af1",
    size: 50000000,
    screenshotURLs: [],
    downloadURL: {
      ios: "https://dl.strem.io/apple/2.0.2b17/ios/stremio_iOS.ipa"
    }
  },

  // Platform definitions
  // deepLink: null = no deep link (show copy-to-clipboard button instead)
  // supportsTV: true = include in tvOS section when tvosEnabled
  platforms: [
    {
      id: "altstore-classic",
      name: "AltStore Classic",
      file: "altstore-classic.json",
      deepLink: "altstore-classic://source?url=",
      supportsTV: false
    },
    {
      id: "sidestore",
      name: "SideStore",
      file: "sidestore.json",
      deepLink: "sidestore://source?url=",
      supportsTV: false
    },
    {
      id: "feather",
      name: "Feather",
      file: "feather.json",
      deepLink: "feather://source/",
      supportsTV: false
    },
    {
      id: "stikstore",
      name: "StikStore",
      file: "stikstore.json",
      deepLink: "stikstore://add-source?url=",
      supportsTV: false
    },
    {
      id: "livecontainer",
      name: "LiveContainer",
      file: "livecontainer.json",
      deepLink: "livecontainer://source?url=",
      supportsTV: false
    },
    {
      id: "trollapps",
      name: "TrollApps",
      file: "trollapps.json",
      deepLink: "trollapps://add?url=",
      supportsTV: false
    },
    {
      id: "esign",
      name: "ESign",
      file: "esign.json",
      deepLink: null,
      supportsTV: false
    },
    {
      id: "ksign",
      name: "KSign",
      file: "ksign.json",
      deepLink: null,
      supportsTV: false
    },
    {
      id: "gbox",
      name: "GBox",
      file: "gbox.json",
      deepLink: null,
      supportsTV: false
    },
    {
      id: "scarlet",
      name: "Scarlet",
      file: "scarlet.json",
      deepLink: null,
      supportsTV: false
    }
  ]
};
