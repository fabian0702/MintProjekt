from nicegui import ui
from nicegui.events import ValueChangeEventArguments
import requests, base64
from datetime import datetime
from os import environ
SERVER_URL = environ.get('SERVER_URL', None)
if SERVER_URL is None:
    print('Please set SERVER_URL to the url of the api')
    exit(1)

def getDevices():
    return requests.get(SERVER_URL+'/list_devices/').json()

@ui.refreshable
def renderDevices():
    devices = getDevices()
    locations = {devices[device]['location']:[] for device in devices}
    for device in devices:
        locations[devices[device]['location']].append(devices[device])

    for location in locations:
        with ui.card().classes('w-1/3'):
            ui.label(location).classes('font-bold text-xl')
            for device in locations[location]:
                with ui.row().classes('w-full p-2').style('box-shadow: 0rem 0.1rem 0.2rem gray; border-radius: 0.5rem'):
                    l = ui.label(f"{device['location']} {device['id']}").classes('text-xl').on('click', lambda x: deviceDialog(x.sender.device))
                    l.device = device
                    s = ui.space().on('click', lambda x: deviceDialog(x.sender.device))
                    s.device = device
                    with ui.button(icon='cancel', color='red', on_click=lambda x: removeDevice(x.sender.device)).props('flat dense') as b:
                        b.device = device
                        ui.tooltip('Remove device')
            async def add(x):
                id = requests.post(SERVER_URL+f'/register_device/',params={'location':x.sender.location}).json()['id']
                devices = getDevices()
                await deviceDialog(devices[id])
                renderDevices.refresh()
            b1 = ui.button('Add Device', icon='add', on_click=add)
            b1.location=location
    ui.button('Add Location', icon='add', on_click=addDeviceDialog)

def removeDevice(device):
        with ui.dialog(value=True) as dialog:
            def remove():
                requests.post(SERVER_URL+f'/remove_device/', params={'token':device["token"]})
                renderDevices.refresh()
            with ui.card():
                ui.label('Remove confirmation').classes('font-bold text-lg')
                ui.label(f'Do you want to remove {device["location"]} {device["id"]}?')
                with ui.row():
                    ui.button('Cancel', on_click=lambda x: dialog.close())
                    ui.button('Delete', color='red', on_click=remove)

def deviceDialog(device):
    with ui.dialog() as dialog:
        with ui.card().classes('w-1/2'):
            with ui.row().classes('w-full'):
                ui.label(f"{device['location']} {device['id']}").classes('font-bold text-xl')
                ui.space()
                def remove():
                    removeDevice(device)
            ui.textarea(label='Token').bind_value(device, 'token').classes('w-full').props('readonly autogrow')
            ui.button('Remove', color='red', on_click=remove)
            ui.button('Done', on_click=lambda x: renderDevices.refresh())
        dialog.open()
    return dialog

def addDeviceDialog():
    with ui.dialog(value=True) as dialog:
        with ui.card().classes('w-1/3'):
            ui.label('New location:')
            loc = ui.input(placeholder='Click here to type...').props('clearable')
            def createDevice():
                requests.post(SERVER_URL+f'/register_device/', params={'location':loc.value})
                renderDevices.refresh()
            ui.button('Register', on_click=createDevice)

with ui.header():
    with ui.tabs().classes('w-full').props('dense') as tabs:
        # data = ui.tab('Data')
        devices = ui.tab('Devices')
        calibrate = ui.tab('Calibrate')
with ui.tab_panels(tabs, value=devices).classes('w-full'):
    #with ui.tab_panel(data):
    #    ui.label('To be implemented')

    with ui.tab_panel(devices).classes('justify-center place-items-center'):
        renderDevices()

    with ui.tab_panel(calibrate).classes('justify-center place-items-center'):
        with ui.card().classes('w-1/4 justify-center place-items-center'):
            ui.label('Calibration').classes('font-bold text-lg')
            devices = requests.get(SERVER_URL+'/list_devices/').json()
            names = [f'{devices[device]["location"]} {devices[device]["id"]}' for device in devices]
            with ui.select(names, value=names[0], label='Location').props('dense').classes('w-1/2') as location:
                ui.tooltip('The device you would like to calibrate')
            with ui.input(label='time', placeholder='hh:mm (dd:mm:year)', validation={
                'Please input a valide hour': lambda value: int(value[:2]) in range(0, 24),
                'Please input a valide minutes': lambda value: len(value) <= 3 or int(value[3:5]) in range(0, 60),
                'Please input a valide day': lambda value: len(value) <= 6 or int(value[6:8]) in range(0, 30),
                'Please input a valide month': lambda value: len(value) <= 9 or int(value[9:11]) in range(0, 30),
                'Please either provide a complete time or a complete time and date' : lambda value: len(value) in [6, 16]
            }).props('mask="##:## ##-##-####" clearable').classes('w-1/2') as time:
                ui.tooltip('The time/date at which you would like to calibrate the device.')

            with ui.input('desired result', validation={'Please input a value':lambda value: len(value)>0}).props('mask="######" clearable').classes('w-1/2') as result:
                ui.tooltip('The result you would like on the given date.')
            
            def errorDialog(errorMessage:str):
                with ui.dialog(value=True) as dialog:
                    with ui.card():
                        ui.label(errorMessage)
                        ui.button('OK', on_click=lambda x: dialog.close())
            def convert_to_timestamp(input_str):
                if not (input_str is None or len(input_str) in [6, 16]):
                    return None
                elif len(input_str) == 6:
                    input_str += datetime.now().strftime('%d-%m-%Y')
                              
                return datetime.strptime(input_str, '%H:%M %d-%m-%Y').timestamp()

            def calibrateRequest():
                if not len(result.value):
                    errorDialog('Please provide a expected value')
                    return
                timestamp = convert_to_timestamp(time.value)
                if timestamp is None:
                    errorDialog('Please provide a correct time')
                    return
                print({ "timestamps": [ timestamp ], "desiredResults": [ float(result.value) ] })
                response = requests.post(SERVER_URL+'/adjust_coeficients/', params={'location':list(devices.keys())[names.index(location.value)]}, json={ "timestamps": [ convert_to_timestamp(time.value) ], "desiredResults": [ float(result.value) ] })
                if response.status_code == 404:
                    errorDialog('No data at the specified time found at the specified time.')
                elif response.status_code == 200:
                    errorDialog('Configuration succesfully updated')
            ui.button('Calibrate', on_click=calibrateRequest)


ui.run(title='Admin pannel')