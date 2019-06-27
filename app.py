#  Copyright (c) 2019. Created for UBS Hackathon. Intended to use within UBS network.
#  Author - UBS MMS Team

from flask import Flask
import NLPBrain as nlp_brain
import MailHelper as mail_helper
import CalendarHelper as cal_helper

app = Flask(__name__)


@app.route('/')
def hello_minutetaker():
    #lets try to create a stream of incoming file and save it to local disc
    #for now lets assume that we already have a transcript file in below locatio
    # fixed file path for now is /Users/mohameddhameemm/PycharmProjects/MMS/transcript.txt
    #PATH = '/Users/mohameddhameemm/PycharmProjects/MMS/transcript.txt'
    PATH = './1.txt'
    brain = nlp_brain.NLPBrain(PATH, 3)
    print(brain.concepts_discussed())
    #print("Lets see how Text Summary comes out")
    #print(brain.text_summary())
    #print("Lets see how Action Items comes out")
    print('Action Items ->',brain.retrieve_action_items())
    #print("Lets see how calendar items comes out")
    #print(brain.retrieve_calendar_items())
    print('Frequently Discussed Topic :' , brain.frequently_discussed_topics())

    #lets try to get the calendar entries from the Google Calendar

    #print(cal_helper.CalendarHelper.getPastMeetingDetails(""))
    #print(event1)
    start, end, attendees, organizer, title  = cal_helper.CalendarHelper.getPastMeetingDetails("")
    mail_helper.MailHelper.sendEmail("",organizer['email'],"Minutes of Meeting -"+title+" Start:"+start+" End:"+end,"",title,attendees,organizer['email'],title,
                                     brain.text_summary(),brain.retrieve_action_items(),PATH)
    return 'Completed....!'

if __name__ == '__main__':
    app.run()
