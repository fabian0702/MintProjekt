from nicegui import ui
import requests, base64
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
                    b = ui.button(icon='cancel', color='red', on_click=lambda x: removeDevice(x.sender.device)).props('flat dense')
                    b.device = device
            async def add(x):
                id = requests.post(SERVER_URL+f'/register_device/?location={x.sender.location}').json()['id']
                devices = getDevices()
                await deviceDialog(devices[id])
                renderDevices.refresh()
            b1 = ui.button('Add', icon='add', on_click=add)
            b1.location=location
    ui.button('Add Location', icon='add', on_click=addDeviceDialog)

def removeDevice(device):
        with ui.dialog(value=True) as dialog:
            def remove():
                requests.post(SERVER_URL+f'/remove_device/?token={device["token"]}')
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
                requests.post(SERVER_URL+f'/register_device/?location={loc.value}')
                renderDevices.refresh()
            ui.button('Register', on_click=createDevice)

with ui.header():
    with ui.tabs().classes('w-full').props('dense') as tabs:
        data = ui.tab('Data')
        devices = ui.tab('Devices')
        calibrate = ui.tab('Calibrate')
with ui.tab_panels(tabs, value=devices).classes('w-full'):
    with ui.tab_panel(data):
        ui.label('To be implemented')

    with ui.tab_panel(devices).classes('justify-center place-items-center'):
        renderDevices()

    with ui.tab_panel(calibrate).classes('justify-center place-items-center'):
        with ui.card():
            ui.label('Calibration').classes('font-bold text-lg')
            # devices = requests.get(SERVER_URL+'/list_devices/').json()
            # names = [f'{devices[device]["location"]} {devices[device]["id"]}' for device in devices]
            # ui.select(names, value=names[0]).props('dense')
            def validate(x):
                ui.notify(x)
                if len(x.sender.value) in [2, 8, 11]:
                    x.sender.value += ':'
                if len(x.sender.value) == 5:
                    x.sender.value += ' '
            ui.input(placeholder='hour:minute day:month:year or hour:minute').on('change', validate)

ui.run(title='Admin pannel')