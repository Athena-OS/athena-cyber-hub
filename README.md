<div align="center">
    <!--<img src="data/icons/hicolor/scalable/apps/org.athenaos.CyberHub.svg" height="64">-->
    <h1>Athena OS Cyber Hub</h1>
    <p>Athena Cyber Hub is a forked version of <a href="https://github.com/Vanilla-OS/vanilla-control-center">Vanilla Control Center</a> with several differences in order to fit the needs of Cyber Security users on <a href="https://github.com/Athena-OS">Athena OS</a>.</p>
    <p>Unlike <a href="https://github.com/Vanilla-OS">Vanilla OS</a>, it replaces distrobox by docker and it is not intended to run operating systems or managing the updates, but it is intended to run vulnerable laboratories for learning purposes and cyber security platforms for offensive and defensive activities.</p>
    <hr />
</a>
    <br />
    <img src="data/screenshot.png">
</div>


## Build from source
### Dependencies
- base-devel
- meson
- go
- appstream-glib
- libadwaita
- gettext
- desktop-file-utils
- python-lxml
- python-toml
- vte4
- docker
- docker-compose
- gnome-console
- marktext

### Build
```bash
meson setup build
ninja -C build
```

### Install
```bash
sudo ninja -C build install
```

## Run
```bash
athena-cyber-hub
```

## Credits
Athena Cyber Hub is a forked project of [Vanilla Control Center](https://github.com/Vanilla-OS/vanilla-control-center) adapted for [Athena OS](https://github.com/Athena-OS). I would like to thank [@mirkobrombin](https://github.com/mirkobrombin) and [Vanilla OS team](https://github.com/orgs/Vanilla-OS/people) for the original project.
