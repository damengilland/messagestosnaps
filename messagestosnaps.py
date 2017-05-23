#!/usr/bin/python

import sqlite3
import os
import logging
import getpass

AGE_MINS = 10
AGE_SECS = AGE_MINS*60

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    user = getpass.getuser()
    DB_LOCATION = "/Users/"+str(user)+"/Library/Messages/chat.db"
    ATT_LOCATION = "/Users/"+str(user)+"/Library/Messages/Attachments/"
    logging.debug("Database location:  "+DB_LOCATION)
    logging.debug("Database location:  "+ATT_LOCATION)

    output = os.popen('sleep 2; lsappinfo info `lsappinfo front` |grep bundleID |cut -d "=" -f 2').read()
    output = output.strip().replace('"','')
    if output == 'com.apple.iChat':
        logging.debug("iChat in foreground; quitting")
        exit(1)
    else:
        logging.debug("Other app in foreground, continuing")
    
    logging.debug("Killing Messages")
    command = 'killall Messages > /dev/null 2>&1'
    logging.debug(command);
    os.popen(command)
    logging.debug("Removing all messages older than "+str(AGE_MINS)+" minutes from chat database");
    logging.debug("Connecting to DB at:  "+DB_LOCATION)
    conn = sqlite3.connect(DB_LOCATION)
    c = conn.cursor()
    age_secs = AGE_MINS*60
    query = "delete from message where date < (strftime('%s','now')-strftime('%s','2001-01-01')-"+str(AGE_SECS)+");"
    logging.debug(query)
    c.execute(query)
    
    query = "delete from chat_message_join where message_id not in (select ROWID from message)"
    logging.debug(query)
    c.execute(query)
    
    query = "delete from chat where ROWID not in (select chat_id from chat_message_join)"
    logging.debug(query)
    c.execute(query)
    
    query = "delete from deleted_messages"
    logging.debug(query)
    c.execute(query)
    
    conn.commit()
    conn.close()
    logging.debug("Removing all attachments older than "+str(AGE_MINS)+" minutes from attachments files");
    command = 'find '+ATT_LOCATION+' -mmin +' +str(AGE_MINS)+ ' -type f -delete'
    logging.debug(command);
    os.popen(command)

    logging.debug("Bouncing imagent")
    command = 'killall imagent > /dev/null 2>&1'
    logging.debug(command);
    os.popen(command)

    logging.debug("Starting messages")
    command = """osascript -e 'tell application "/Applications/Messages.app" to run' """
    logging.debug(command);
    os.popen(command)
    
