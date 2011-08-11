#!/usr/bin/env /usr/local/epd-7.0-2-rh5-x86_64/bin/python
import web

web.config.debug=False

app = web.application(urls, globals(), True)

if __name__ == "__main__":
    app.run()

