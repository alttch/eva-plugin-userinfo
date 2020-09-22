# eva-plugin-userinfo

User info plugin for [EVA ICS](https://www.eva-ics.com/). Provides simple
key-value storage for extended user information.

## Installation

This is a single-file plugin, put "userinfo.py" to EVA ICS plugins folder and
enjoy

## Configuration

Example:

```ini
[userinfo]
db = runtime/db/userinfo.db
rw = name,email
ro = job
```

* db - required, relative path to SQLite database or SQLAlchemy DB uri
* rw - read-write fields (allowed to set by user)
* ro - read-only fields (allowed to set with master key only)

Info database can be shared between controllers / EVA ICS instances.

## Exposed API methods

* x_userinfo_get_field(u, p, n) - get user info field

    * u - user login (requires master key)
    * p - user type
    * n - field name

* x_userinfo_set_field(u, p, n) - set user info field

    * u - user login (requires master key)
    * p - user type
    * n - field name

If user is not specified in params, an API call must be authenticated with
valid user token and field data is get/set for the current logged in user.
