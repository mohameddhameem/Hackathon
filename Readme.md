# **MMS - Meeting Made Simple**
## **Application to handle transcript and analyze the incoming text message**

Below are some of the application key behavior
1) Expect input as a TXT file. (in feature if we are getting a audio file, then it need to converted to text via SPEECH To TEXT)
2) Once the text is inputed it will go for basic NLP cleanup - Stopword removal, Stemming, Tokenization
3) Use IBM Watson NaturalLanguageUnderstandingV1 
4) Get the Text Summarization from the Engine.
5) Other functions included are get some of the other analytics as Concept, Action Items
6) The Calendar module will get the required meeting information and get below details :
        a) Organiser
        b) Meeting Attendees
        c) Agenda
        d) Start and End Time
        e) Action Items(if there are any)
7) Formulate a HTML template and send email with the Minutes of Meeting