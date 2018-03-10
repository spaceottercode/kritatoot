# KritaToot

> a simple ready-to-use plugin with no external dependencies

A plugin for Krita 4.x that lets you post a copy of your **current** document directly on Mastodon.

Adds **Tools > Scripts > Post on Mastodon** menu option when enabled. 

A copy of the current document is always exported and posted. 

> If the current document has never been saved, the exported image defaults to a PNG.

You can also specify a message (optional), the privacy setting of your toot (Public, Unlisted, Followers-Only, Direct) and whether you want to hide your image behind a warning title card.

> If no message is given, the default is to include the following: posted with KritaToot

> Log files are written to ~/.kritatoot on Linux.

# Installation


#### Krita 4.0.0 on Linux

Download a zip file and copy the **kritatoot** folder containing the App.py file and the **kritatoot.desktop** file into the following location:

~~~
~/.local/share/krita/pykrita
~~~

Enable plugin: **Settings > Configure Krita... > Python Plugin Manager > kritatoot**

#### Krita 4.0.0 on Windows

Download a zip file and copy the **kritatoot** folder containing the App.py file and the **kritatoot.desktop** file into the *Resource Folder* (Settings > Manage Resources > Open Resource Folder). Usually nested inside the (hidden) AppData folder in your personal user folder. 


Enable plugin: **Settings > Configure Krita... > Python Plugin Manager > kritatoot**

> May require a krita relaunch



# Limitation

* Only one image per toot
* Specifying a focal point, found on new Mastodon servers, is not implemented
* Maximum file size and file types are set by the Mastodon server
* no alternate text

# TODO

* implement focal point support or similar feature
* when adding support for multiple images per toot, how do we indicate images and their order
* alternate text
* spoiler text?

# License

This script is licensed under an (Expat) MIT License. Feel free to fork
