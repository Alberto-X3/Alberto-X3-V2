# Alberto-X3


### Structure

```
Project
├── AlbertoX3
│   ├── scales
│   │   └── <category>
│   │       ├── <scale>
│   │       │   ├── translations
│   │       │   │   └── en.yml
│   │       │   ├── __init__.py
│   │       │   ├── colors.py
│   │       │   ├── models.py
│   │       │   ├── permissions.py
│   │       │   ├── settings.py
│   │       │   └── stats.py
│   │       └── __init__.py
│   ├── __init__.py
│   ├── __main__.py
│   ├── aio.py
│   ├── colors.py
│   ├── config.py
│   ├── database.py
│   ├── dis_snek.py
│   ├── enum.py
│   ├── environment.py
│   ├── permissions.py
│   ├── settings.py
│   ├── stats.py
│   ├── translations.py
│   ├── types.py
│   └── utils.py
└── config.yml
```


### Internal

#### Imports

```py
from __future__ import annotations


__all__ = ...


import something  # e.g. 'sys' or 're'

from something import something  # e.g. 'TYPE_CHECKING' from 'typing'

from dis_snek import something

from AlbertoX3 import something

from .something import something  # e.g. 'Colors' from '.colors'


if TYPE_CHECKING:
    from something import something  # for type hinting


# source code...
```
