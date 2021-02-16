# eva-plugin-userinfo

User info plugin for [EVA ICS](https://www.eva-ics.com/). Provides simple
key-value storage for extended user information for EVA ICS user db.

## Installation

This is a single-file plugin, put "userinfo.py" into EVA ICS plugins folder and
enjoy

## Configuration

Example (/opt/eva/etc/\<controller\>.ini):

```ini
[plugin.userinfo]
rw = name,email
ro = job
```

* rw - read-write fields (allowed to set by user)
* ro - read-only fields (allowed to set with master key only)

Info database can be shared between controllers / EVA ICS instances.

## Exposed API methods

* **x\_userinfo\_get\_field**(u, p, n) - get user info field

    * u - user login (requires master key)
    * p - user type
    * n - field name

* **x\_userinfo\_set\_field**(u, p, n, v) - set user info field

    * u - user login (requires master key)
    * p - user type
    * n - field name
    * v - field value (string)

If user is not specified in params, an API call must be authenticated with
valid user token and field data is get/set for the current logged in user.
