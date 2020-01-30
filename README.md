# README
## Start develoopment environment
Prerequisites: Docker and Visual Studio Code (With remote development extension)
- Open root folder in container with VS code.

## Run tests
- Use vs code Test menu
- Or from root:
```
python -m unittest discover test -p '*_test.py'
```

## Run PLC 2 or 3
- Use vs code rund and debug menu, choose plc from the dropdown

## Code Documentation with Sphinx
### New files *.py
- New files need to be added to `docs/modules.rst`, and `*.rst` file need to be added for each file
### Create/Update
To create/update the documentation, run `make html`from /docs directory.
### View
To view the documentation open `docs/_build/html/index.html` in a browser.

### TODO
- set up travis