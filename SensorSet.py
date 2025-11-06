# -*- coding: utf-8 -*-
import struct
import ctypes
import time
import pysoem
from collections import namedtuple

class BOTA_ETH:
    BOTA_VENDOR_ID = 0xB07A
    BOTA_PRODUCT_CODE = 0x00000001

    # ====== Your filter settings ======
    SINC_LENGTH = 32   # try: 32, 64, 128, 256, 512, 2048
    FIR = 0            # 1 = enable FIR
    FAST = 0           # 1 = enable spike filter
    CHOP = 0           # 1 = enable CHOP
    TEMPCOMP = 1
    IMU_ACTIVE = 0
    # ==================================

    def __init__(self, ifname):
        self._master = pysoem.Master()
        self._ifname = ifname

    def configure_filters(self, slave):

        print("\n--- Switching to SAFE_OP ---")
        self._master.state = pysoem.SAFEOP_STATE
        self._master.write_state()
        time.sleep(0.1)

        print("Writing filter registers...")

        # Calibration & flags
        slave.sdo_write(0x8010, 1, struct.pack('<B', 1))
        slave.sdo_write(0x8010, 2, struct.pack('<B', self.TEMPCOMP))
        slave.sdo_write(0x8010, 3, struct.pack('<B', self.IMU_ACTIVE))

        # Filtering registers
        slave.sdo_write(0x8006, 1, struct.pack('<H', self.SINC_LENGTH))
        slave.sdo_write(0x8006, 2, struct.pack('<B', int(not self.FIR)))
        slave.sdo_write(0x8006, 3, struct.pack('<B', int(self.FAST)))
        slave.sdo_write(0x8006, 4, struct.pack('<B', int(self.CHOP)))

        time.sleep(0.1)

        print("--- Switching back to OP ---")
        self._master.state = pysoem.OP_STATE
        self._master.write_state()
        time.sleep(0.2)

        # Confirm written configuration
        sampling_rate = struct.unpack('<H', slave.sdo_read(0x8011, 0))[0]
        sinc = struct.unpack('<H', slave.sdo_read(0x8006, 1))[0]
        fir_bit = struct.unpack('<B', slave.sdo_read(0x8006, 2))[0]
        fast = struct.unpack('<B', slave.sdo_read(0x8006, 3))[0]
        chop = struct.unpack('<B', slave.sdo_read(0x8006, 4))[0]

        print("\n========== BOTA Filter Config ==========")
        print(f"SINC Length  : {sinc}")
        print(f"FIR Enabled  : {not bool(fir_bit)}")
        print(f"FAST Filter  : {bool(fast)}")
        print(f"CHOP Filter  : {bool(chop)}")
        print(f"Sampling Rate: {sampling_rate} Hz")
        print("========================================\n")

    def run(self):
        self._master.open(self._ifname)
        if self._master.config_init() <= 0:
            raise RuntimeError("No EtherCAT slave found!")

        for idx, slave in enumerate(self._master.slaves):
            if slave.id == self.BOTA_PRODUCT_CODE:
                print(f"Found BOTA sensor at position {idx}")
                self.configure_filters(slave)

        print("Filter configuration completed.\n")
        self._master.close()


if __name__ == '__main__':
    devName = '\\Device\\NPF_{E769D094-BB66-47A2-95AB-D542812C80B9}'

    BOTA = BOTA_ETH(devName)
    BOTA.run()
