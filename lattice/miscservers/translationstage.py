import sys
import usb.core
import usb.util

# find our device
#dev = usb.core.find(idVendor=0xfffe, idProduct=0x0001)
dev = usb.core.find(find_all=True, bDeviceClass=0)


# was it found?
if dev is None:
    raise ValueError('Device not found')

print dev

for i in dev:
    print i.idVendor
    print i.idProduct
    for cfg in i:
        sys.stdout.write(str(cfg.bConfigurationValue) + '\n')
        for intf in cfg:
            sys.stdout.write('\t' + \
                             str(intf.bInterfaceNumber) + \
                             ',' + \
                             str(intf.bAlternateSetting) + \
                             '\n')
            for ep in intf:
                sys.stdout.write('\t\t' + \
                                 str(ep.bEndpointAddress) + \
                                 '\n')

## set the active configuration. With no arguments, the first
## configuration will be the active one
#dev.set_configuration()
#
## get an endpoint instance
#cfg = dev.get_active_configuration()
#interface_number = cfg[(0,0)].bInterfaceNumber
#alternate_settting = usb.control.get_interface(interface_number)
#intf = usb.util.find_descriptor(cfg, bInterfaceNumber = interface_number, bAlternateSetting = alternate_setting)
#
#ep = usb.util.find_descriptor(intf,
#    # match the first OUT endpoint
#    custom_match = \
#    lambda e: \
#        usb.util.endpoint_direction(e.bEndpointAddress) == \
#        usb.util.ENDPOINT_OUT
#)
#
#assert ep is not None
#
## write the data
#ep.write('test')