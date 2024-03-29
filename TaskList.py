import os
import json
import codecs
import datetime
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from datepicker import DatePicker

# SHA-256 hash of "newYearNewHack" - json only allows dict keys to be strings,
# so this serves as a workaround to create a name for the default list that no user will ever accidentally repeat.
# Probably.
# (Stupid Kivy doesn't allow me to easily set length limits on TextInputs so that the default list name
#  could simply be something longer and achieve a 100% chance of not getting found out)
default_list = "485A39CA22060964FE81DE1A570636C167A2560E5EB6786E9B3CCE2004E49CCA485A39CA22060964FE81DE1A570636C167A2560E5EB6786E9B3CCE2004E49CCA"
# Data format: dict with tasklist names as keys and dicts,
# consisting of a task list and a "complete" boolean, as corresponding values
# Comes with a default list that contains all tasks that are not part of any lists.
# Save file example can be found as "TasksData_example.json"
data = {default_list: {"tasks": [], "completed": True}}


# Load data from save file
def load():
    with open('TasksData.json') as f:
        return json.load(f)


# Save data to file to recover it on next launch
def save():
    with open('TasksData.json', 'wb') as f:
        json.dump(data, codecs.getwriter('utf-8')(f), ensure_ascii=False, indent=4)


# Task object description
class Task:
    def __init__(self, name, deadline, desc, parent_list):
        self.name = name
        self.deadline = deadline
        self.creation_time = datetime.datetime.now()
        self.desc = desc
        self.complete = False
        self.parent_list = parent_list

    def get_data(self):
        task_data = {"name": self.name,
                     "deadline": self.deadline,
                     # To reverse: datetime.datetime.strptime(TIME_STRING, "%Y-%m-%d %H:%M:%S.%f")
                     "creation_time": str(self.creation_time),
                     "desc": self.desc,
                     "complete": self.complete}
        return task_data


# TODO: Task list description
class TaskList:
    def __init__(self):
        self.tasks = []


# Store task in the data variable and call save()
def save_task(name, deadline, desc, parent_list, popup_instance):
    new_task = Task(name, deadline, desc, None)
    data[parent_list]["tasks"].append(new_task.get_data())
    data[parent_list]["completed"] = data[parent_list]["completed"] & True
    save()
    popup_instance.dismiss()
    success_msg = SuccessPopup("Task created")
    success_msg.open()
    Clock.schedule_once(success_msg.dismiss, 0.8)


# TODO: Store tasklist in the data variable and call save()
def save_tasklist():
    raise NotImplementedError


# Success message popup with configurable title
class SuccessPopup(Popup):
    def __init__(self, text, **kwargs):
        super(SuccessPopup, self).__init__(title=text, size_hint=(0.4, None), size=(-1, 100), **kwargs)
        self.add_widget(Button(text="Ok", on_press=self.dismiss))


# Popup to input new task parameters
def create_task_popup():
    popup = Popup(title="Create new task",
                  size_hint=(0.5, 0.5))
    popup.add_widget(NewTaskPopupContent(popup))
    popup.open()


class NewTaskPopupContent(BoxLayout):
    def __init__(self, popup_instance, **kwargs):
        super(NewTaskPopupContent, self).__init__(orientation='vertical', **kwargs)
        self.add_widget(Label(text='Name'))
        name_input = TextInput(hint_text="Task name", multiline=False)
        self.add_widget(name_input)
        self.add_widget(Label(text='Deadline'))
        deadline_input = DatePicker()
        self.add_widget(deadline_input)
        self.add_widget(Label(text="Description"))
        desc_input = TextInput(hint_text="Short description of the task.")
        self.add_widget(desc_input)
        self.add_widget(Button(text="Save", on_press=lambda *args: save_task(name_input.text,
                                                                             deadline_input.text,
                                                                             desc_input.text,
                                                                             # CHANGE ME once task lists are implemented
                                                                             default_list,
                                                                             popup_instance)))
        self.add_widget(Button(text="Cancel", on_press=lambda *args: popup_instance.dismiss()))


# TODO: Popup to input new tasklist parameters
def create_tasklist_popup():
    popup = Popup(title="Create new tasklist",
                  size_hint=(0.5, 0.5))
    popup.add_widget(NewTaskListPopupContent(popup))
    popup.open()


class NewTaskListPopupContent(BoxLayout):
    def __init__(self, popup_instance, **kwargs):
        super(NewTaskListPopupContent, self).__init__(orientation='vertical', **kwargs)
        self.add_widget(Label(text='Ooh, you found me!'))
        self.add_widget(Button(text="Cancel", on_press=lambda *args: popup_instance.dismiss()))


# Sublayout for "Add-new-X" buttons
class New(BoxLayout):
    def __init__(self, **kwargs):
        super(New, self).__init__(**kwargs)
        self.add_widget(Button(text='New task', on_press=lambda x: create_task_popup()))
        btn1 = Button(text='New task list', on_press=lambda x: create_tasklist_popup())
        self.add_widget(btn1)


# Main layout
# TODO: Once tasklists are implemented, convert to kivy.uix.pagelayout.Pagelayout
#  to allow swiping left-right between tasklists
class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(orientation='vertical', **kwargs)
        self.add_widget(Label(text="Hello world!"))
        new = New()
        self.add_widget(new)


# Kivy initiation
class TaskellApp(App):
    def build(self):
        return MainLayout()


if __name__ == '__main__':
    if os.path.isfile("TasksData.json"):
        data = load()
    TaskellApp().run()
