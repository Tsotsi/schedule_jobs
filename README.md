

### Usage

```

$ mkdir  path  && cd path
$ virtualenv venv --no-site-packages
$ . venv/bin/activate
$ mkdir jobs
$ touch jobs/__init__.py

```


`jobs/date_job.py`

```python
from schedule_jobs.core.base_job import BaseJob
import datetime

class DateJob(BaseJob):
    def run(self, *args, **kwargs):
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
```

`main.py`

```python

from schedule_jobs.app import App


def main():
    print("main")
    app = App()
    app.schedule()


if __name__ == "__main__":
    main()

```
#### dir

```
    path
    path/jobs/__init__.py
    path/jobs/date_job.py
    path/main.py

```

#### finally
```

$ python main.py

```
