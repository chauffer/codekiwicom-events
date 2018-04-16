import base64
import re

from flask import Flask, Response
import icalendar
import requests
import rfeed

app = Flask(__name__)

@app.route('/')
def root():
    r = requests.get(
        'https://calendar.google.com/calendar/ical/' +
        'skypicker.com_dq9oupgj7ngbo0j41b0smoc0dk%40group.calendar.google.com' +
        '/public/basic.ics',
        timeout=10,
        )
    r.raise_for_status()
    text = r.text

    events = []
    feed = rfeed.Feed(
        title='code.kiwi.com events',
        link='https://goo.gl/aCCGCB',
        description='code.kiwi.com events',
        items=events,
    )
    gcal = icalendar.Calendar.from_ical(text)

    for component in gcal.walk():
        if component.name == "VEVENT":
            url = 'https://www.google.com/calendar/event?eid=' + \
                base64.b64encode((component['UID'].split('@')[0] + ' skypicker.com_dq9oupgj7ngbo0j41b0smoc0dk@g').encode()).decode()
            description = component.get('description')
            if description:
                description = re.sub('Tato událost.*\nPřipojit se.*', '', description).strip()

            events.append(
                rfeed.Item(
                    title=component.get('dtstart').dt.strftime('%D') + ' | ' + str(component.get('summary')),
                    link=url,
                    description=str(component.get('description')),
                    guid=rfeed.Guid(url),
                )
            )
    return Response(feed.rss(), mimetype='application/rss+xml')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
