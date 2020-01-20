# Speed Bot
Author/Developer: Mason Rogers (Kangaroo Kids/Stanford Jump Rope)  
Created: May 2019  
Version: 2.0 (in beta, January 2020)  
TL;DR Video: https://youtu.be/vyE-EaiIUfQ

## About
#### Description
Speed bot is a Mac Application that automates speed workout timing to make your training more efficient. Plug in your workout and hit run, and Speed Bot will call out splits, switches, and more. Speed Bot times your workout with an intuitive language of beeps that allow for great timing precision.
#### Who might use Speed Bot?
* Any jumper who has ever jumped a minute of speed while timing themselves on a wall clock
* Any multitasker who has ever miscounted a speed jumper because they were focusing on timing the event (or vice versa)
* Any coach who has ever struggled to focus on their jumpers’ form because they were too busy orchestrating the workout
* Anyone who has had trouble keeping their workout on schedule
* Anyone who jumps rope
#### A Request:
Please report bugs, feature requests, anecdotes about using the program, questions, comments, suggestions, etc. to me however you like to get in touch, or by opening an issue!

## Running Speedbot from Github
Download the 'code' folder and run 'main.py' however you run python code. Make sure your current working directory is set to the code folder. You may have to install several Python packages if you do not already have them. I am working to develop a dependency list for speedbot and find an efficient way to install all of the necessary packages. **If you don't want to mess with the source code and want to use a Mac app version instead, please let me know and I will send you one.**

## Interpreting the User Interface
#### Basics
* To add an event to your workout, simply drag it from the event library to the workout bar at the bottom. You can also drag and drop to reorder events.
* To delete an event from your workout, click on it and a delete button will appear.
* Display modes include the current/next event names, a timer, and a clicker that track split scores.
* The *run* and *stop* buttons start and stop the workout. Note that the *stop* button is not a pause buttion; *that would defeat the point of the application*.
#### Clicker Mode
* To count with your mouse, click on the clicker.
* To count with your keyboard, hover your mouse over the clicker so that it turns blue. The spacebar and up arrow work to click up. The down arrow clicks down. Backspace resets the clicker to zero.
* To open the log and see split scores, either right click or use the left or right arrow keys.
#### Settings
* *Alternating* events will cycle through groups without rest. Repetitions are counted per group, and the total number of repetitions will be displayed when the event is added to your workout.
* *Full workout reps* sets the number of times the full workout will be repeated.
* *Rest warning* sets the number of seconds by which the 'rest ending' beep precedes the next event.
#### Modifying the Library
* To add an event to the library, hit File > Add Speed Event and input the event info. For example, a 4 x 30 relay event has a duration of 120 with splits every 10 and switches every 30.
* To rearrange or delete an event from the library, hit File > Manage Events. Drag and drop to rearrange or select an event to delete.

## Interpreting the Beeps
#### Starting and Ending the Workout
* To start your workout and set a synchronization point for the timer, Speed Bot employs a ‘ski race’-style start cue of four low-pitched beeps followed by one high-pitched 'start' beep.
* At the end of your workout, Speed bot employs a 'soccer match'-style finish cue of two short beeps followed by one longer beep. Congratulations—you’re done!
#### During the Workout
* A single high beep indicates the end of the event/rest (and the beginning of the next one).
* A single low beep indicates a split within an event.
* A double beep (low-medium) indicates a switch within a relay event or an even minute within three minute speed.
* A triple beep (low-medium-high) indicates an alternation between partners/lines repeating the same event.
* A rest warning is a very long, very low-pitched beep.
* *Make sure to communicate the workout plan to everyone involved ahead of time. While the beeps may seem complicated in text form, they are very intuitive to understand within the context of a workout that everyone knows.*

## Technical Notes
#### Timing
Speed Bot aims to time consecutive events as precisely as possible. To do so, it synchronizes event times with the computer’s internal clock. This could be implemented in at least two ways:
1. Observe event 1 start time > Compute scheduled end time of every event > Beep accordingly
2. Observe event 1 start time > Compute scheduled end time of event 1 > Beep and observe start time of event 2 > Compute scheduled end time of event 2 > Beep and observe start time of event 3 > …

The two methods differ from each other by the minute fractions of a second it takes for Speed Bot’s event timing code to run. Both methods are susceptible to slight timing errors on individual events introduced by the tiny amount of time it takes between when an event is scheduled to end and when Speed Bot 'realizes' and 'communicates' the end of an event. The first method has the ostensibly nice property that the workout ends exactly as long after it starts as it should, as the start times of events cannot 'drift'. However, this comes at a cost; errors in event run times would necessarily be correlated to force the total workout error to be zero. In practice, this would likely result in the first event being a slim fraction of a second too long and the last event being a slim fraction of a second too short, which in my opinion is unfair. In the second method, the total workout run time will have small error, but individual event time errors will be uncorrelated and therefore (in my opinion) more fair.

#### Code
I wrote in Python 3.6 with the help of Qt Designer. If you are interested to see or discuss the code, it is available on github. I am interested in porting to other platforms if there is sufficient interest in the jump rope community. I am unfamiliar with iOS and Android development, so if anyone has that skillset, please let me know.

