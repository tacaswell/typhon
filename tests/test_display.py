############
# Standard #
############

############
# External #
############
import pytest
from ophyd.signal import EpicsSignal, EpicsSignalRO
from ophyd import Device, EpicsMotor, Component as C, FormattedComponent as FC
from ophyd.tests.conftest import using_fake_epics_pv

###########
# Package #
###########
from typhon.utils import clean_attr
from typhon.display import DeviceDisplay
from .conftest import show_widget


class MockDevice(Device):
    # Device signals
    read1 = C(EpicsSignalRO, ':READ1')
    read2 = C(EpicsSignalRO, ':READ2')
    read3 = C(EpicsSignalRO, ':READ3')
    read4 = C(EpicsSignal,   ':READ4')
    read5 = C(EpicsSignal,   ':READ5', write_pv=':WRITE5')
    config1 = C(EpicsSignalRO, ':CFG1')
    config2 = C(EpicsSignalRO, ':CFG2')
    config3 = C(EpicsSignalRO, ':CFG3')
    config4 = C(EpicsSignal,   ':CFG4')
    config5 = C(EpicsSignal,   ':CFG5', write_pv=':CFGWRITE5')
    misc1 = C(EpicsSignalRO, ':MISC1')
    misc2 = C(EpicsSignalRO, ':MISC2')
    misc3 = C(EpicsSignalRO, ':MISC3')
    misc4 = C(EpicsSignal,   ':MISC4')
    misc5 = C(EpicsSignal,   ':MISC5', write_pv=':MISCWRITE5')

    # Component Motors
    x = FC(EpicsMotor, 'Tst:MMS:X', name='X Axis')
    y = FC(EpicsMotor, 'Tst:MMS:Y', name='Y Axis')
    z = FC(EpicsMotor, 'Tst:MMS:Z', name='Z Axis')

    # Default Signal Sorting
    _default_read_attrs = ['read1', 'read2', 'read3', 'read4', 'read5']
    _default_configuration_attrs = ['config1', 'config2', 'config3',
                                    'config4', 'config5']

    def insert(self, width: float=2.0, height: float=2.0,
               fast_mode: bool=False):
        """Fake insert function to display"""
        pass

    def remove(self, height: float,  fast_mode: bool=False):
        """Fake remove function to display"""
        pass


@using_fake_epics_pv
@pytest.fixture(scope='module')
def device():
    return MockDevice("Tst:Dev", name="MockDevice")


@using_fake_epics_pv
@show_widget
def test_display(device):
    display = DeviceDisplay(device)
    # We have all our signals
    shown_read_sigs = list(display.read_panel.pvs.keys())
    assert all([clean_attr(sig) in shown_read_sigs
                for sig in device.read_attrs])
    shown_cfg_sigs = list(display.config_panel.pvs.keys())
    assert all([clean_attr(sig) in shown_cfg_sigs
                for sig in device.configuration_attrs])
    # We have all our subdevices
    sub_devices = [getattr(disp, 'device', None)
                   for disp in display.ui.component_widget.children()]
    assert all([getattr(device, dev) in sub_devices
                for dev in device._sub_devices])
    return display


@using_fake_epics_pv
@show_widget
def test_display_with_funcs(device):
    display = DeviceDisplay(device, methods=[device.insert,
                                             device.remove])
    # The method panel is visible
    assert not display.method_panel.isHidden()
    # Assert we have all our specified functions
    assert 'insert' in display.methods
    assert 'remove' in display.methods
    return display


@using_fake_epics_pv
@show_widget
def test_display_with_hints(device):
    device.hints = {'fields': [device.name + '_read1']}
    display = DeviceDisplay(device)
    assert len(display.ui.hint_plot.curves) == 1
    return display


@using_fake_epics_pv
@show_widget
def test_display_with_images(device, test_images):
    (lenna, python) = test_images
    display = DeviceDisplay(device)
    # Add our main image
    display.add_image(python)
    # Add our component image
    display.add_image(lenna, subdevice=device.x)
    assert not display.image_widget.isHidden()
    # Show our subdevice and image
    display.show_subdevice(device.x.name)
    assert display.image_widget.currentWidget().filename == lenna
    # Hide all subdevices and show main image
    display.hide_subdevices()
    assert display.image_widget.currentWidget().filename == python
    return display
