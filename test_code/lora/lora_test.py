from LoRaRF import SX127x

# Initialize LoRa module
lora = SX127x()

# Set SPI bus configuration (SPI bus 0, chip select 0)
lora.setSpi(0, 0)

# Set GPIO pins: NSS (CS), RESET, and DIO0 (IRQ)
lora.setPins(8, 22, 25)  # NSS=8 (GPIO8/CE0), RESET=22, DIO0=25

print("Begin LoRa radio")
if not lora.begin():
    raise Exception("Something wrong, can't begin LoRa radio")

# Set frequency to 866 MHz
print("Set frequency to 867.525 MHz")
lora.setFrequency(867525000)

# Set RX gain. RX gain options are power saving gain or boosted gain
print("Set RX gain to boosted gain")
lora.setRxGain(lora.RX_GAIN_BOOSTED, lora.RX_GAIN_AUTO)  # AGC on, Power saving gain

print("Set TX power to +17 dBm")
lora.setTxPower(17, lora.TX_POWER_PA_BOOST)

# Configure modulation parameters
print("Set modulation parameters:\n\tSpreading factor = 7\n\tBandwidth = 500 kHz\n\tCoding rate = 4/5")
lora.setSpreadingFactor(7)
lora.setBandwidth(500000)
lora.setCodeRate(5)

# Configure packet parameters
print("Set packet parameters:\n\tExplicit header type\n\tPreamble length = 8\n\tPayload Length = 60\n\tCRC on")
lora.setHeaderType(lora.HEADER_EXPLICIT)
lora.setPreambleLength(8)
lora.setPayloadLength(60)
lora.setCrcEnable(True)

# Set synchronize word (0xA5)
print("Set synchronize word to 0xA5")
lora.setSyncWord(0xA5)

print("\n-- LoRa Receiver --\n")

def receive_packets():

# Receive message continuously
    # Request for receiving new LoRa packet
    lora.request()
    # Wait for incoming LoRa packet
    lora.wait()

    raw_data = []

# Read available bytes from the LoRa receiver
    while lora.available():
        raw_data.append(lora.read())

    print(f"Raw bytes: {raw_data}")
    
    # Example of decoding a uint8_t value from the raw data

    # Print packet/signal status including RSSI, SNR, and signalRSSI
    print("Packet status: RSSI = {0:0.2f} dBm | SNR = {1:0.2f} dB".format(lora.packetRssi(),lora.snr()))

    # Print received message and counter
    #print(f"{message}  {counter}")
    
    # Show received status in case CRC or header error occur
    status = lora.status()
    if status == lora.STATUS_CRC_ERR:
        print("CRC error")
    elif status == lora.STATUS_HEADER_ERR:
        print("Packet header error")


    return raw_data
