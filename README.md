Zuso
====

Zuso is a plugin that allows you to move between `hex`, `rgb` and `rgba` values seamlessly.

Zuso allows you to:

* convert from `rgb` or `rgba` to `hex` and vice-versa
* select whether you would like uppercase or lowercase conversions for `hex`
* disable shortening of `sugared` `hex` values
* select a default opacity for all `rgba` conversions


Installing
----------
**With the Package Control plugin:** The easiest way to install Zuso is through Package Control, which can be found at this site: http://wbond.net/sublime_packages/package_control

Once you install Package Control, restart ST2 and bring up the Command Palette (`Command+Shift+P` on OS X, `Control+Shift+P` on Linux/Windows). Select "Package Control: Install Package", wait while Package Control fetches the latest package list, then select Zuso when the list appears. The advantage of using this method is that Package Control will automatically keep Zuso up to date with the latest version.

The "Packages" directory is located at:

* OS X:

        ~/Library/Application Support/Sublime Text 2/Packages/

* Linux:

        ~/.config/sublime-text-2/Packages/

* Windows:

        %APPDATA%/Sublime Text 2/Packages/

Using
-----
Zuso runs in either it's default or `active` modes, which is determined by the "active" user setting:

* **Default** - When "active" is set to false,  on selection, Zuso recognizes `hex`, `rgb`, `rgba` values, converts them and displays them in the ST2 autocomplete box.versions to your autocomplete list.

* **Active mode** - When "active" is set to true, you can select more than one selection and invoke Zuso via `Ctrl+Shift+3`.


Thanks
-------
To Will Bond for his excellent tutorial in making ST Plugins. http://bit.ly/tr6UeF

