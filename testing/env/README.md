# Test environment folder

Add here files from `savannah/core/blanks` and edit them as it is 
necessary for testing.

This is thought for avoiding building the source each time, making 
debugging easier (modification on the spot). 

For `pythonpath` inclusion, don't add to `manage.py` a `sys.path.append` 
line that will add the location of the branch of the framework. Instead, 
install the package in development mode in a virtualenv.