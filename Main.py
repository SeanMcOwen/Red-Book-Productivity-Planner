from flask import Flask,request, render_template
import sqlite3
import pandas as pd
from Create_Databases import excel_to_db
import RedBook, RedBookBokeh

from threading import Thread
from tornado.ioloop import IOLoop
from bokeh.embed import server_document

from bokeh.server.server import Server


from RedBookFlask import app

import os




def bk_worker():
    # Can't pass num_procs > 1 in this configuration. If you need to run multiple
    # processes, see e.g. flask_gunicorn_embed.py
    server = Server({'/schedules': RedBookBokeh.schedules,
                     '/dailyincrements': RedBookBokeh.dailyIncrementsTracker,
                     '/schedulesPIT': RedBookBokeh.schedules_PIT,
                     '/calendar': RedBookBokeh.calendar_view,
                     '/progressbars': RedBookBokeh.progress_bars,
                     '/GroupCalendarProgress':  RedBookBokeh.GroupCalendarProgress}, io_loop=IOLoop(), allow_websocket_origin=["localhost:8000"])
    server.start()
    server.io_loop.start()



if __name__ == "__main__":
    Thread(target=bk_worker).start()
    app.run(debug=False, host='0.0.0.0', port=8000)