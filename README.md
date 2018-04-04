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

Download a zip file and copy the **kritatoot** folder and the **kritatoot.desktop** file into the following location:

~~~
~/.local/share/krita/pykrita
~~~

Enable plugin: **Settings > Configure Krita... > Python Plugin Manager > kritatoot**

#### Krita 4.0.0 on Windows

Download a zip file and copy the **kritatoot** folder and the **kritatoot.desktop** file into Krita's *Resource Folder* (Settings > Manage Resources > Open Resource Folder). It's usually a folder somewhere in the hidden AppData folder.


Enable the plugin: **Settings > Configure Krita... > Python Plugin Manager > kritatoot**

> You may need to restart Krita



# Limitation

At the moment:

* You can post one image per toot.
* Specifying a focal point is not implemented
* no input for alternate text
* Maximum file size and file types are set by the Mastodon server


# TODO

* implement focal point support or equivalent feature
* determine the best way to add support for multiple images per toot, in an orthogonal fashion. e.g. If an open doc is the subject of a toot's image how do we indicate other images (other open docs?), especially their order.
* alternate text
* spoiler text?

# License

This script is licensed under an (Expat) MIT License. Feel free to fork
