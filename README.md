# Chaac
Modern server monitoring system - WORK IN PROGRESS

## Quick Notes
These are breif notes and will be tidied up later once the system is more developed.  It is very much incomplete at this point in time
### Python Path
The server side components (e.g. collector) require access to parts of the "common" module.  You should therefore set your PYTHONPATH environment variable to the path containing the commmon package (i.e. the root of the git repo):
```
export PYTHONPATH=/path/to/git/repo/:$PYTHONPATH
```
